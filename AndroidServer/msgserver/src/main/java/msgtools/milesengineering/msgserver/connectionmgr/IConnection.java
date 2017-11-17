package msgtools.milesengineering.msgserver.connectionmgr;

import java.io.IOException;
import java.nio.ByteBuffer;

/**
 * Connection interface, that represents a connection to a message source/sink
 * Your implementation MUST be threadsafe with respect to this interface.
 */
public interface IConnection {
    /**
     * Send a  message on this connection. The message will be converted
     * to use a header appropriate to it's underlying transport before sending.
     *
     * @param msgId MsgTools header message ID
     * @param payloadBuff Data payload for the message.
     * @return true if the message was sent, else false
     */
    boolean sendMessage(long msgId, ByteBuffer payloadBuff);

    /**
     * Get the total number of messages sent
     *
     * @return int of total messages sent
     */
    int getMessagesSent();

    /**
     * Get the total number of messages received
     *
     * @return int total messages received
     */
    int getMessagesReceived();

    /**
     * Close the connection.
     */
    void close() throws IOException;
}
