# Design Notes

## TODO List
* Add Tx/Rx Message counts - should broadcast on a 1 sec interval (for Hz) and build up a specialized list item view for decent formatting
* Logging feature - start-stop(remote/local)/timestamp/base filename/entry of message version/JSON format
* Make sure app sleep and wake works ok
* Power optimizations
* 

## Assumptions
The following assumptions have been made:
* NetworkHeader is the de-facto header for all clients.  If you need to work with a different header then do that translation
as part of your specific IConnection implementations.
* All headers MUST have an ID and payload length.  To support any protocol you can comprise the ID out of any bits your want.
They just need to be unique within the overall message space.  The length MUST be the number of payload bytes after the header.


# Adding a new MessageService API and intent handler

The message service as a message based API, that sends responses via braodcast intents.
These are the steps to follow when adding a new API and intent. Note that the current design
could be cleaned up and streamlined to establish a better pattern, however a large number
of APIs isn't anticipated so a lot of time wasn't spent designing something more elegant.

## New API
1. To MessageServiceServerAPI add a new message ID and request method.  Just follow the established pattern
2. In MsgServerService::MsgServerAPIHandler::handleMessage add a case for your new message

## New Intent Response
1. Add a new intent id at the top of MsgServerService
2. In the handleMessage method mentioned in step 2 above - send a broadcast intent with your response using the new intent id
3. In AppBroadcastReceiver.java add a case to handle the new intent