#Please fill the configuration to connect to your database.
DATABASE_CONFIG = {
    'host': '127.0.0.1',
    'dbname': 'YOUR_PHPBB_ADRESS',
    'user': 'MYSQL_ACCOUNT_NAME',
    'password': 'MYSQL_PASSWORD',
    'port': 3306
}

#Please change SERVER_IP with your server IP adres
SERVER_IP = "YOUR_PYTHON_SERVER_HOST_ADRESS"
#You can change server port... please take care to allow its access from your firewall!
SERVER_PORT = 9001
#Create a special key for the server. DO NOT SHARE IT WITH ANYONE ! It should not contain any semicolon (;)
SERVER_KEY = "A_RANDOM_PHPBB_KEY"

#If you do not use https (SSL/TLS) leave USE_SSL = 0
#If you use an SSL gateway, you will need to configure your access from your SSL Panel and leave USE_SSL = 0
#If you use SSL for the board, set USE_SSL = 1 and point the pem files.
USE_SSL = 0
SSL_CERT_PATH = "/etc/letsencrypt/live/XXXXXX/fullchain.pem"
SSL_KEY_PATH = "/etc/letsencrypt/live/XXXXX/privkey.pem"

#Please fill here the url of your website.
board_url = "/"
#Please fill here the prefix to all phpbb tables
prefix_table = "phpbb_"


#Change the text below if you want to change the text displayed when a new post has been made.
def generate_message(topic_name, username, postid):
    return "<b>"+username + "</b> has just posted an answer to <i>"+topic_name+"</i><br>Click <a href='"+board_url+"viewtopic.php?p="+postid+"#p"+postid+"'>here</a> to read it."

#DEBUG
DEBUG = False
