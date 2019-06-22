websocket_alexlf_livemessage = new WebSocket("wss://www.superboard.com:9001/");
websocket_alexlf_livemessage.onopen = function(evt) { onOpen(evt) };
websocket_alexlf_livemessage.onclose = function(evt) { onClose(evt) };
websocket_alexlf_livemessage.onmessage = function(evt) { onMessage(evt) };
websocket_alexlf_livemessage.onerror = function(evt) { onError(evt) };

function reopen(){
	websocket_alexlf_livemessage = new WebSocket("wss://www.superboard.com:9001/");
}

function onOpen(evt)
{
	websocket_alexlf_livemessage.send("0;{SECRET_CODE_WEBSOCKET}");
}

function onClose(evt)
{
	reopen();
}

function onError(evt)
{
	reopen();
}

function onMessage(evt)
{
	alertify.notify("<center>"+evt.data+"</center>", 'success', 12);
}