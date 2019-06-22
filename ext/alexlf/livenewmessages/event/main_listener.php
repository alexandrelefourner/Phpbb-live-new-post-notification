<?php
/**
 *
 * Live new messages. An extension for the phpBB Forum Software package.
 *
 * @copyright (c) 2019, Alexandre A. LE FOURNER
 * @license GNU General Public License, version 2 (GPL-2.0)
 *
 */
namespace alexlf\livenewmessages\event;

require(dirname(dirname(__FILE__)) . '/vendor/autoload.php');

use WebSocket\Client;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;




class main_listener implements EventSubscriberInterface
{
	static public function getSubscribedEvents()
	{
		return array(
			'core.submit_post_end' => 'submit_post_end',
			'core.page_header' => 'load_header',
		);
	}

	/* @var \phpbb\controller\helper */
	protected $helper;
	
	/* @var \phpbb\config\config */
	protected $config;

	/* @var \phpbb\template\template */
	protected $template;

	/* @var \phpbb\user */
	protected $user;

	/** @var string phpEx */
	protected $php_ext;

	/**
	 * Constructor
	 *
	 * @param \phpbb\controller\helper	$helper		Controller helper object
	 * @param \phpbb\template\template	$template	Template object
	 * @param \phpbb\user               $user       User object
	 * @param string                    $php_ext    phpEx
	 */
	public function __construct(\phpbb\controller\helper $helper, \phpbb\template\template $template, \phpbb\user $user, $php_ext,\phpbb\config\config $config)
	{
		$this->helper   = $helper;
		$this->template = $template;
		$this->user     = $user;
		$this->php_ext  = $php_ext;
		$this->config  = $config;
	}


	public function submit_post_end($event){
		global $user;
		
		if($event["mode"] == "reply" OR $event["mode"] == "post"){
			$client = new Client("wss://url_of_your_server:port_of_your_server/");
			$client->send("1;key_of_your_server;" . $event["data"]["topic_id"] . ";" . $user->data["username"].  ";" . $event["data"]["post_id"]);
		}
	}
	
	public function load_header(){
		global $user;
		
		$this->template->assign_vars(array(	
			'SECRET_CODE_WEBSOCKET' => $user->data["user_id"] . ";" . $user->data["user_regdate"]
		));
	}

}
