/*
    <OUTPUTFILENAME>
    Created <DATE> from:
        Messages = <INPUTFILENAME>
        Template = <TEMPLATEFILENAME>
        Language = <LANGUAGEFILENAME>

                     AUTOGENERATED FILE, DO NOT EDIT

*/
package <MESSAGE_PACKAGE>;

import java.nio.ByteBuffer;
import java.util.HashMap;
import java.util.Map;
import msgtools.FieldInfo;
import msgtools.FieldAccess;

public class <MSGSHORTNAME> extends msgplugin.Message
{
    public static final int MSG_ID = (int)<MSGID>;
    public static final int MSG_SIZE = <MSGSIZE>;
    public <MSGSHORTNAME>()
    {
        super(MSG_SIZE);
        SetMessageID(MSG_ID);
        //InitializeTime();
        Init();
    }
    public <MSGSHORTNAME>(ByteBuffer buffer)
    {
        super(buffer);
    }
    public <MSGSHORTNAME>(ByteBuffer header, ByteBuffer payload)
    {
        super(header, payload);
    }
    void Init()
    {
        <INIT_CODE>
    }
    <ENUMERATIONS>
    <FIELDINFOS>
    <ACCESSORS>

    public static msgtools.MsgInfo msgInfo;
    static
    {
        msgInfo = new msgtools.MsgInfo(<MSGSHORTNAME>.class, MSG_ID, "<MSGDESCRIPTION>", MSG_SIZE);
        msgInfo.AddField(new <REFLECTION>);
    }
};
