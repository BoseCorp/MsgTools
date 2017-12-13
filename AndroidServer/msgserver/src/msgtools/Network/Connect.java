/*
    /Users/mosminer/Projects/obj/CodeGenerator/Java/Network/Connect.java
    Created 16/11/2017 at 08:02:48 from:
        Messages = messages/Network/Connect.yaml
        Template = ../Java/JavaTemplate.java
        Language = ../Java/language.py

                     AUTOGENERATED FILE, DO NOT EDIT

*/
package Network;

import java.nio.ByteBuffer;
import java.util.HashMap;
import java.util.Map;
import MsgApp.*;

public class Connect extends Message
{
    public static final int MSG_ID = (int)4294967041L;
    public static final int MSG_SIZE = 64;
    public Connect()
    {
        super(MSG_SIZE);
        SetMessageID(MSG_ID);
        //InitializeTime();
        Init();
    }
    public Connect(ByteBuffer buffer)
    {
        super(buffer);
    }
    void Init()
    {
    }
    class NameFieldInfo {
        static final int loc   = 0;
        static final short max   = 255;
        static final short min   = 0;
        static final String units = "ASCII";
        static final int count = 64;
    };
    
    // The name of the client. ASCII, (0 to 255)
    public short GetName(int idx)
    {
        return (short)Byte.toUnsignedInt(m_data.get(0+idx*1));
    }
    // The name of the client. ASCII, (0 to 255)
    public void SetName(short value, int idx)
    {
        m_data.put(0+idx*1, (byte)value);
    }

    public static MsgInfo msgInfo;
    static
    {
        msgInfo = new MsgInfo(Connect.class, MSG_ID, "Connection message used to announce a client's existance to the server.", MSG_SIZE);
        msgInfo.AddField(new FieldInfo("Name", "The name of the client.", "ASCII", 64));
    }
};