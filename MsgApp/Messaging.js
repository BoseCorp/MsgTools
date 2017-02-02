function toJSON(obj) {
    //console.log("JSON for " + obj.MSG_NAME + ", ID=",+obj.MSG_ID+", "+obj.MSG_SIZE+" bytes")
    var jsonStr = '"'+obj.MSG_NAME+'": ';
    jsonStr += JSON.stringify(obj.toObject());
    return jsonStr;
}

function buf2hex(buffer) { // buffer is an ArrayBuffer
  return Array.prototype.map.call(new Uint8Array(buffer), x => ('00' + x.toString(16)).slice(-2)).join('');
}

var MessageDictionary = {};
    
var MessagingClient = function() {
    this.webSocket = new WebSocket("ws://127.0.0.1:5679", "BMAP");
    this.webSocket.binaryType = 'arraybuffer';
    this.webSocket.onopen = this.onopen.bind(this);
    this.webSocket.onclose = this.onclose.bind(this);
    this.webSocket.onmessage = this.onmessage.bind(this);
}

MessagingClient.prototype.onopen = function (event) {
    cm = new Connect();
    cm.SetNameString("javascript");
    this.send(cm);

    // default values will make us receive all messages
    sm = new MaskedSubscription();
    this.send(sm);

    if(typeof this.onconnect === "function")
    {
        this.onconnect();
    }

};

MessagingClient.prototype.onclose = function(event) {
    console.log("Websocket closed");
};

MessagingClient.prototype.onmessage = function (event) {
    var hdr = new NetworkHeader(event.data);
    var id = hdr.GetMessageID();
    var strId = String(id >>> 0)
    if(strId in MessageDictionary)
    {
        msgClass = MessageDictionary[strId];
        msg = new msgClass(event.data);
        if(typeof this.onmsg === "function")
        {
            this.onmsg(msg);
        }
    }
    else
    {
        console.log("ERROR! Msg ID " + id + " not defined!");
    }
};

MessagingClient.prototype.send = function (msg) {
    this.webSocket.send(msg.m_data.buffer);
};
