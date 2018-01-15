package msgtools.milesengineering.msgserver;

import android.app.Service;
import android.content.Intent;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.os.Looper;
import android.os.Message;
import android.os.Messenger;
import android.os.Process;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.util.Hashtable;
import java.util.concurrent.ConcurrentHashMap;

import headers.NetworkHeader;
import msgtools.milesengineering.msgserver.connectionmgr.IConnection;
import msgtools.milesengineering.msgserver.connectionmgr.IConnectionMgr;
import msgtools.milesengineering.msgserver.connectionmgr.IConnectionMgrListener;
import msgtools.milesengineering.msgserver.connectionmgr.MessageRouterThread;
import msgtools.milesengineering.msgserver.connectionmgr.bluetooth.BluetoothConnectionMgr;
import msgtools.milesengineering.msgserver.connectionmgr.tcp.TCPConnectionMgr;
import msgtools.milesengineering.msgserver.connectionmgr.websocket.WebsocketConnectionMgr;

/**
 * The main MsgServerService class.  This sets up a service thread, manages incoming messages
 * for API requests, and broadcasts intents to interested clients for new and dropped connections.
 */
public class MsgServerService extends Service implements Handler.Callback, IConnectionMgrListener {
    private static final String TAG = MsgServerService.class.getSimpleName();

    //
    // Constants
    //
    public static final String INTENT_SEND_SERVERS = "msgtools.milesengineering.msgserver.MsgServerServiceSendServers";
    public static final String INTENT_SEND_CONNECTIONS = "msgtools.milesengineering.msgserver.MsgServerServiceSendConnection";
    public static final String INTENT_SEND_NEW_CONNECTION = "msgtools.milesengineering.msgserver.MsgServerServiceSendNewConnection";
    public static final String INTENT_SEND_CLOSED_CONNECTION = "msgtools.milesengineering.msgserver.MsgServerServiceSendClosedConnection";
    public static final String INTENT_SEND_LOGGING_STATUS = "msgtools.milesengineering.msgserver.MsgServerServiceSendLoggingStatus";

    private final static int TCP_PORT = 5678;
    private final static int WEBSOCKET_PORT = 5679;
    private final static int TIMER_INTERVAL = 1000; // ms for each RX/TX update
    public final static String LOG_DIRECTORY = "MessageServer";

    private Messenger m_MsgHandler;               // For external client binding
    private Handler m_MsgServerHandler;           // To pump messages on this service...
    private MessageRouterThread m_RouterThread;   // Routes our incoming messages and handles special messages like StartLog
    private boolean m_LastLogState;               // Track our last known log state so we can post updates...
    //
    // Connection Managers which handle connections on various transports for us.  Treated
    // as Singletons by this class
    //
    private IConnectionMgr m_TCPConnectionMgr;
    private IConnectionMgr m_WebsocketConnectionMgr;
    private IConnectionMgr m_BluetoothConnectionMgr;

    private String m_ServersJSON = "";  // List of connection managers in JSON for when a client app asks

    // Keep a class local record of connections - you might be wondering why we don't just get a list
    // of connections from each manager.  Threadsafety is the simple answer.  Rather than making
    // repeated copies of collections from the managers to iterate on for each message it's
    // more performant to maintain a global list in the service.
    // This of course leads to potential synchronization issues which we have to handle.
    private ConcurrentHashMap<IConnection,IConnection> m_Connections =
            new ConcurrentHashMap<IConnection,IConnection>();

    // Timer properties used to post RX/TX updates
    private Handler m_TimerHandler = new Handler();
    private Runnable m_TimerRunnable = new Runnable() {
        @Override
        public void run() {
            if (m_RouterThread.messagesSent() == true)
                sendConnectionsIntent();

            // Broadcast a logging status update - if it changed
            broadcastLoggingStatusIntent(null);

            m_TimerHandler.postDelayed(this, TIMER_INTERVAL);
        }
    };

    // Message Logging
    private MessageLogger m_MsgLogger;

    /**
     * Private utility class that processes Messages from bound clients.  This is where our
     * MsgServerServiceAPI messages are processed.
     */
    private class MsgServerAPIHandler extends Handler {
        @Override
        public void handleMessage(Message msg) {
            switch (msg.what) {
                case MsgServerServiceAPI.ID_REQUEST_SERVERS:
                    android.util.Log.d(TAG, "Servers Request Received");
                    sendServersIntent();
                    break;
                case MsgServerServiceAPI.ID_REQUEST_CONNECTIONS:
                    android.util.Log.d(TAG, "Connections Request Received");
                    sendConnectionsIntent();
                    break;
                case MsgServerServiceAPI.ID_REQUEST_START_LOGGING:
                    android.util.Log.d(TAG, "Start Logging Request");
                    try {
                        String json = (String) msg.obj;
                        JSONObject jsonObj = (JSONObject) new JSONTokener(json).nextValue();
                        startLogging(jsonObj.getString("filename"), jsonObj.getString("msgVersion"), null);
                    }
                    catch(JSONException je) {
                        broadcastLoggingStatusIntent(je.getMessage());
                    }
                    break;
                case MsgServerServiceAPI.ID_REQUEST_STOP_LOGGING:
                    android.util.Log.d(TAG, "Stop Logging Request");
                    stopLogging(null);
                    break;
                default:
                    android.util.Log.w(TAG, "Unknown message type received by MsgServer.");
                    super.handleMessage(msg);
            }
        }
    }

    public MsgServerService() {
        super();
    }

    @Override
    public void onCreate() {
        android.util.Log.i(TAG, "onCreate()");
        Toast.makeText(this, "MsgServer Service Starting...", Toast.LENGTH_SHORT).show();

        // Setup a binding message handler for any client bind requests
        m_MsgHandler = new Messenger(new MsgServerAPIHandler());

        // Spin up our message handling thread and ConnectionManagers
        HandlerThread ht = new HandlerThread( "MsgServerServiceThread",
                Process.THREAD_PRIORITY_BACKGROUND);
        ht.start();

        Looper looper = ht.getLooper();
        m_MsgServerHandler = new Handler(looper, this);

        // Instantiate our connection managers - but don't start them quite yet...
        m_TCPConnectionMgr = new TCPConnectionMgr(new InetSocketAddress(TCP_PORT), this);
        m_WebsocketConnectionMgr = new WebsocketConnectionMgr(new InetSocketAddress(WEBSOCKET_PORT), this);
        m_BluetoothConnectionMgr = new BluetoothConnectionMgr(this, this);

        // Fire up a logger and message router thread and get all registered for callbacks
        // etc.  Do this before starting up our managers so we don't miss anything.
        m_MsgLogger = new MessageLogger(LOG_DIRECTORY);
        m_LastLogState = false;
        m_RouterThread = new MessageRouterThread(m_MsgLogger);
        m_RouterThread.start();

        // Register the router as a listener for connection and msg events...
        m_TCPConnectionMgr.addListener(m_RouterThread);
        m_WebsocketConnectionMgr.addListener(m_RouterThread);
        m_BluetoothConnectionMgr.addListener(m_RouterThread);

        // Start managers...
        m_TCPConnectionMgr.start();
        m_WebsocketConnectionMgr.start();
        m_BluetoothConnectionMgr.start();

        // Build up a servers JSON list for when clients ask.  This is static for now since we
        // hard code the servers.  If we move to dynamic model you might want to maintain a list
        // and rebuild on the fly...
        buildServersJSON();

        // Kick off a 1 second timer which we will use to post RX/TX updates and check for log
        // status changes...
        m_TimerHandler.postDelayed(m_TimerRunnable, TIMER_INTERVAL);
    }

    @Override
    public void onDestroy() {
        android.util.Log.i(TAG, "onDestroy()");
        Toast.makeText(this, "MsgServer Service Being Destroyed...", Toast.LENGTH_SHORT).show();

        m_TimerHandler.removeCallbacks(m_TimerRunnable);

        m_MsgLogger.stopLogging();

        m_TCPConnectionMgr.requestHalt();
        m_WebsocketConnectionMgr.requestHalt();
        m_BluetoothConnectionMgr.requestHalt();
        m_RouterThread.requestHalt();

        m_MsgServerHandler.getLooper().quitSafely();

        m_TCPConnectionMgr = null;
        m_WebsocketConnectionMgr = null;
        m_BluetoothConnectionMgr = null;
        m_RouterThread = null;

        m_MsgServerHandler = null;

        m_MsgServerHandler.getLooper().quitSafely();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        android.util.Log.i(TAG, "onStartCommand(...)");

        if (flags == START_FLAG_REDELIVERY) {
            return START_NOT_STICKY;
        }

        return START_STICKY;
    }

    //
    // Service binding stuff...
    //

    @Override
    public IBinder onBind(Intent intent) {
        android.util.Log.i(TAG, "onBind(...)");
        return m_MsgHandler.getBinder();
    }

    @Override
    public void onRebind(Intent intent) {
        android.util.Log.i(TAG, "onRebind(...)");
        // TODO: reset any state based on binding if needed
    }

    @Override
    public boolean onUnbind(Intent intent) {
        android.util.Log.i(TAG, "onUnbind(...)");
        return super.onUnbind(intent);
    }

    /**
     * Process messages from bound clients...
     * @param msg message to process
     * @return always returns false to continue processing.
     */
    @Override
    public boolean handleMessage(Message msg) {
        android.util.Log.i(TAG, "MessageHandler::handleMessage(...)");

        // This is where we process messages from our bound clients
        switch(msg.what) {
            default:
                android.util.Log.w(TAG, "Received unknown message: " + msg.what);
        }

        return false;   // Keep going
    }

    //
    // Connection Manager Listener
    //

    @Override
    public void onNewConnection(IConnectionMgr mgr, IConnection newConnection) {
        if (m_Connections.put(newConnection, newConnection) == null) {
            broadcastNewConnectionIntent(mgr, newConnection);
        } else {
            android.util.Log.w(TAG, "Received a duplicate new connection event");
        }
    }

    @Override
    public void onClosedConnection(IConnectionMgr mgr, IConnection closedConnection) {
        if ( m_Connections.remove(closedConnection) == null ) {
            android.util.Log.w(TAG, "Attempted to remove a closed connection that is not being tracked");
        }
        else
            broadcastClosedConnectionIntent(mgr, closedConnection);
    }

    @Override
    public void onMessage(IConnectionMgr mgr, IConnection srcConnection, NetworkHeader networkHeader,
                          ByteBuffer hdrBuff, ByteBuffer payloadBuff) {
        // Do nothing - our router thread handles it all
    }

    //
    // MsgServerServiceAPI Handlers
    //

    private void sendServersIntent() {
        Intent sendIntent = new Intent();
        sendIntent.setAction(MsgServerService.INTENT_SEND_SERVERS);
        sendIntent.putExtra(Intent.EXTRA_TEXT, m_ServersJSON);

        sendBroadcast(sendIntent);
    }

    private void sendConnectionsIntent() {
        // Build up a full list of connections...going to again do brute force JSON
        // conversion. Build up a list of connections...
        JSONArray jarray = new JSONArray();
        for( IConnection c : m_Connections.values() ) {
            jarray.put(getConnectionJSON(c));
        }

        // Broadcast the list
        Intent sendIntent = new Intent();
        sendIntent.setAction(MsgServerService.INTENT_SEND_CONNECTIONS);
        sendIntent.putExtra(Intent.EXTRA_TEXT, jarray.toString());

        sendBroadcast(sendIntent);
    }

    private void startLogging(String filename, String msgVersion, IConnection srcConnection) {
        String errorMsg = m_MsgLogger.startLogging(filename, msgVersion);
        broadcastLoggingStatusIntent(errorMsg);
    }

    private void stopLogging(IConnection srcConnection) {
        String errorMsg = m_MsgLogger.stopLogging();
        broadcastLoggingStatusIntent(errorMsg);
    }

    //
    // Misc utility methods
    //

    private void buildServersJSON() {
        // Brute force method here - nothing fancy
        IConnectionMgr[] managers = new IConnectionMgr[3];
        managers[0] = m_BluetoothConnectionMgr;
        managers[1] = m_TCPConnectionMgr;
        managers[2] = m_WebsocketConnectionMgr;

        JSONArray jarray = new JSONArray();
        for( IConnectionMgr cm : managers ) {
            Hashtable<String,String> map = new Hashtable<String,String>();
            map.put("protocol", cm.getProtocol());
            map.put("description", cm.getDescription());

            jarray.put(JSONObject.wrap(map));
        }

        m_ServersJSON = jarray.toString();
    }

    private JSONObject getConnectionJSON(IConnection conn) {
        // TODO: Probably ought to create a utility class for this so clients
        // can stay in sync...
        JSONObject jsonObj = new JSONObject();
        try {
            jsonObj.put("id", conn.hashCode());
            jsonObj.put("description", conn.getDescription());
            jsonObj.put("recvCount", conn.getMessagesReceived());
            jsonObj.put("sendCount", conn.getMessagesSent());
            jsonObj.put("protocol", conn.getProtocol());
        }
        catch( JSONException je ) {
            je.printStackTrace();
        }

        return jsonObj;
    }

    //
    // Broadcast Intent methods - our reverse API of sorts...
    //

    private void broadcastNewConnectionIntent(IConnectionMgr mgr, IConnection newConnection) {
        android.util.Log.i(TAG, "broadcastNewConnectionIntent");
        broadcastConnectionChangedIntent(MsgServerService.INTENT_SEND_NEW_CONNECTION,
                mgr, newConnection);
    }

    private void broadcastClosedConnectionIntent(IConnectionMgr mgr, IConnection closedConnection) {
        android.util.Log.i(TAG, "broadcastClosedConnectionIntent");
        broadcastConnectionChangedIntent(MsgServerService.INTENT_SEND_CLOSED_CONNECTION,
                mgr, closedConnection);
    }

    private void broadcastConnectionChangedIntent(String action, IConnectionMgr mgr,
                                                  IConnection connection) {
        android.util.Log.d(TAG, "broadcastConnectionChangedIntent");

        JSONObject jsonObject = getConnectionJSON(connection);

        // Broadcast the list
        Intent sendIntent = new Intent();
        sendIntent.setAction(action);
        sendIntent.putExtra(Intent.EXTRA_TEXT, jsonObject.toString());

        sendBroadcast(sendIntent);
    }
    private void broadcastLoggingStatusIntent(String error) {
        // Threadsafe get
        MessageLogger.LogStatus status = m_MsgLogger.getStatus();

        // Only send if something has changed or error is non-null
        if (status.enabled != m_LastLogState || error != null) {
            android.util.Log.d(TAG, "broadcastLoggingStatusIntent");

            JSONObject jsonObj = new JSONObject();
            try {
                jsonObj.put("enabled", status.enabled);
                if (status.enabled == true) {
                    if (status.filename != null)
                        jsonObj.put("filename", status.filename);

                    if (status.version != null)
                        jsonObj.put("msgVersion", status.version);
                }

                if (error != null)
                    jsonObj.put("error", error);
            } catch (JSONException je) {
                // Should never happen.
                je.printStackTrace();
            }

            Intent sendIntent = new Intent();
            sendIntent.setAction(INTENT_SEND_LOGGING_STATUS);
            sendIntent.putExtra(Intent.EXTRA_TEXT, jsonObj.toString());

            sendBroadcast(sendIntent);

            m_LastLogState = status.enabled;
        }
    }
}
