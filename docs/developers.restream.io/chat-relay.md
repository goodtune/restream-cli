<-
### <a name="chat-relay"></a>Relay
###### Used to display relay delivery and errors

Relay is a feature of Restream Chat which allows to sync chats between different event sources.
When relay enabled in settings, whenever the user receives an event, it will be sent to other connections from the name of Restream Bot. 
That way chatters on any platform will see all messages which streamer receives from different event sources.

Relay has much in common with a reply. 
They have a common list of errors, so for relay error reasons, you can check the reply section. 
Also, the workflow is the same. First, you will receive `relay_accepted` action, followed by `relay_confirmed` if we are 100% sure that message was delivered. 
The only difference is that relay triggered by an incoming event, and because of this, it's related to that incoming event by `sourceEventIdentifier`.
<-
