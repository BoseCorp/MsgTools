package msgtools.milesengineering.msgserver.connectionmgr;

import java.io.IOException;
import java.nio.ByteBuffer;

/**
 * Abstraction interface for a connection manager component which is basically
 * responsible for creating connections to which we'll route messages
 */
public interface IConnectionMgr {

    /**
     * Start handling connection
     */
    void start();

    /**
     * Add a new listener to our callback list.  Listeners are invoked on
     * the ConnectionManager's thread and should be threadsafe and not hold up
     * exeuction for too long.
     *
     * @param listener Listener to add to the list
     */
    void addListener( IConnectionMgrListener listener );

    /**
     * Remove a listener from the list
     * @param listener Listener to remove
     * @return true if the listener was removed, else false
     */
    boolean removeListener( IConnectionMgrListener listener );

    /**
     * Stop monitoring and close all active connections.
     */
    void requestHalt();

    /**
     * Check to see if a halt request is pending...use Thread.getState or isAlive
     * to confirm when the thread is done.
     * @return true if halt is pending, else false.
     */
    boolean haltPending();

    /**
     * Retrieve a string representing the protocol this connection manager handles
     * e.g. TCP, WS or Websocket, etc.
     *
     * @return A three chracter or less protocol indicator
     */
    String protocol();

    /**
     * Retrieve a description of the server - suggested descriptions might be the IP address of
     * the server socket, or the MAC address of the host adapter.  Ideally some information that
     * would be of use to an end user in using this server.
     *
     * @return A short string description
     */
    String description();
}
