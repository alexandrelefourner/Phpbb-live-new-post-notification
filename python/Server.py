#!/usr/bin/env python
# coding: utf-8

# In[1]:


import mysql.connector
import asyncio
import config
import re
from SimpleWebSocketServer import *
from threading import RLock, Thread
import time



class TrackingUser():
    def __init__(self, user_id):
        self.uid = user_id
        self.sockets_list = []
        self.followed_topic = []
        
    def add_connection(self, socket):
        printdebug(self.uid)
        self.sockets_list.append(socket)

    def inform_new_response(self, topic_title, from_user, post_id):
        message = config.generate_message(topic_title, from_user, post_id)
        printdebug("Sending", message, "to", len(self.sockets_list), "connections")
        for socket in self.sockets_list:
            try:
                socket.sendMessage(message)
            except:
                #Dead socket ?
                pass
        
class FollowedTopic():
    def __init__(self, topicid, topic_title):
        self._followers = []
        self.tid = topicid
        self.title = topic_title
        
    def add_follower(self, follower):
        if(follower in self._followers):
            return
        self._followers.append(follower)
        
    def new_post(self, from_user, post_id):
        printdebug(self.tid, "is followed by", len(self._followers)," users")
        for follower in self._followers:
            printdebug("Found user", follower)
            if(follower != from_user):
                printdebug("Sending informations...")
                get_user(follower).inform_new_response(self.title, from_user, post_id)


# In[3]:


def connect_to_db():
    global connection
    connection = mysql.connector.connect(
        user=config.DATABASE_CONFIG["user"],
        password=config.DATABASE_CONFIG["password"],
        host=config.DATABASE_CONFIG["host"],
        database=config.DATABASE_CONFIG["dbname"],
        port=config.DATABASE_CONFIG["port"],
        )
    
    connection.autocommit = True


# In[4]:


def select_all(query):
    global cursor, connection
    
    if(not connection.is_connected()):
        connect_to_db()
    cursor = connection.cursor()
        
    cursor.execute(query)
    records = cursor.fetchall()
    for record in records:
        yield record
    cursor.close()


# In[5]:


def printdebug(*args):
    if(config.DEBUG):
        print(*args)


# In[6]:


def get_user_from_key_and_id(user_id, user_key):
    
    
    #Avoiding injection
    if(not user_id.isnumeric()):
        printdebug("Invalid user_id", user_id)
        return -1
    
    if(not re.match('^[a-zA-Z0-9_]+$', user_key)):
        printdebug("Invalid key", user_key)
        return -1
    
    
    
    for record in select_all("Select user_id from "+config.prefix_table+"users "+                              "WHERE user_regdate = '"+user_key+"' AND user_id="+user_id):
        return record[0]  
    printdebug("No record found for", user_id, user_key)             
    return -1
    


# In[7]:


connect_to_db()
if(not connection.is_connected()):
    print("Can't connect to database.")
else:
    print("Connection ok.")


# In[8]:


def trigger_chain_messages(topic_id, poster_name, post_id):
    global topics_watched
    
    topic_id = int(topic_id)
    printdebug("Checking topic", topic_id)
    if(not topic_id in topics_watched):
        printdebug("Topic", topic_id, "not found!")
        return
    
    printdebug("Topic", topic_id, "found. Sending...", topics_watched[topic_id])
    
    topics_watched[topic_id].new_post(poster_name, post_id)


# In[9]:


topics_watched = {}
users_list = {}
connections_list = []


# In[10]:


def get_user(user_id):
    global users_list
    
    if(not user_id in users_list):
        users_list[user_id] = TrackingUser(user_id)
    
    return users_list[user_id]


# In[11]:


def reset_topic_watched():
    
    global topics_watched, protect_locker
    
    try:
        local_watched_topics = {}
        
        for record in select_all("Select user_id, "+config.prefix_table+"topics_watch.topic_id, "+                              config.prefix_table+"topics.topic_title from "+                              config.prefix_table+"topics_watch INNER JOIN "+config.prefix_table+"topics ON "+                              config.prefix_table+"topics_watch.topic_id = "+config.prefix_table+"topics.topic_id"):
            user_id = record[0]
            topic_id = record[1]
            topic_title = record[2]


            if(not topic_id in local_watched_topics):
                local_watched_topics[topic_id] = FollowedTopic(topic_id, topic_title)
            local_watched_topics[topic_id].add_follower(user_id)
        
        with protect_locker:
            del(topics_watched)
            topics_watched = local_watched_topics #Update of the list.
    except:
        printdebug("Reset error.")
    #printdebug("topics reset")


def tread_reset_topic():
    while True:
        reset_topic_watched()
        time.sleep(5)
        
#reset_topic_watched()
protect_locker = RLock()
threader = Thread(target=tread_reset_topic, args=(), daemon=True)
threader.start()


# In[12]:


class ClientManager(WebSocket):
    
    logged_in = False
    
    def handleMessage(self):
        #try:
        if(not ";" in self.data):
            self.close()
            return
        data_split = self.data.split(";")
        self.parsePacket(data_split)

        #except:
        #    print("err")
        #    self.close()
        
    def handleConnected(self):
        connections_list.append(self)
    
    def handleClose(self):
        pass
    
    def parsePacket(self, data_split):
        global protect_locker
            
        if(data_split[0] == "0"): #User login.
            printdebug(data_split[1], data_split[2])
            #0;user_id;session_key
            uid = get_user_from_key_and_id(data_split[1], data_split[2])
            printdebug("Results_conn:",uid)
            if(uid == -1):
                self.close()
                return
            printdebug("User", uid, "connected")
            self.logged_in = True
            get_user(uid).add_connection(self)
            
        elif(data_split[0] == "1"): #Server inform new response.
            printdebug("Connect attempt from server")
            if(data_split[1] != config.SERVER_KEY):
                printdebug("Incorrect key!")
                self.close()
            
            printdebug("Ok.", data_split)
            #1;Secret Sever Key;topic_id;poster_name;post_id
            
            with protect_locker:
                trigger_chain_messages(data_split[2], data_split[3], data_split[4])
            self.close()
            
            
        elif(data_split[0] == "2"): #Server informs a new track from a user.
            if(data_split[1] != config.SERVER_KEY):
                self.close()
            #TODO
            self.close()
            
        elif(data_split[0] == "3"): #Server informs a track has been removed
            if(data_split[1] != config.SERVER_KEY):
                self.close()
            #TODO
            self.close()


# In[13]:


if(config.USE_SSL == 1):
    server = SimpleSSLWebSocketServer(config.SERVER_IP, config.SERVER_PORT, ClientManager, config.SSL_CERT_PATH, config.SSL_KEY_PATH)
else:
    server = SimpleWebSocketServer(config.SERVER_IP, config.SERVER_PORT, ClientManager)

server.serveforever()