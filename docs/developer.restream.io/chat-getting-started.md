<-
### <a name="chat-getting-started"></a>Chat
###### Listen for chat actions

That API allows you to connect to Restream Chat and receive all actions which include: information about current chat connections; incoming events collected from event sources like Twitch, YouTube, etc.; sent replies and relays.

> <span class="warning" /> **Note**: This method requires authentication

Here is a sample in JavaScript that connects to the API using WebSocket API as it is available in the browser:

```javascript
// OAuth `bearer` token
const accessToken = '[access token]';
const url = `wss://chat.api.restream.io/ws?accessToken=${accessToken}`;
const connection = new WebSocket(url);

connection.onmessage = (message) => {
    const action = JSON.parse(message.data);
    console.log(action);
};

connection.onerror = console.error;
```

This API works one way - from the server to the client. The server will ignore any incoming messages.

<-
