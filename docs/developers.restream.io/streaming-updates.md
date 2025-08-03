<-
### <a name="streaming-updates"></a>Streaming updates
###### Listen for streaming-related updates events

This is a newer and improved replacement for stream status events Restream had before.

> <span class="warning" /> **Note**: This method requires authentication

Here is a sample in TypeScript that connects to the API using WebSocket API as it is available in the browser:
```typescript
// OAuth `bearer` token
const accessToken = '[access token]';
const url = `wss://streaming.api.restream.io/ws?accessToken=${accessToken}`;
const connection = new WebSocket(url);

connection.onmessage = (message) => {
    // IUpdates interface is provided on the right
    const update: IUpdates = JSON.parse(message.data);
    console.log(update);
};

connection.onerror = console.error;
```

The way this API works is following:
* upon connection you'll receive all updates since about 1 minute ago (this should be enough information to reconstruct the whole state if needed)
* you will continue receiving new updates as they happen

<-

->
All WebSocket messages are JSON strings and should strictly satisfy following schema (TypeScript syntax, new actions and fields may be added over time):
```typescript
// Incoming stream has created or updated (there is no separate event for creation here)
interface IIncomingStreamUpdated {
    action: 'updateIncoming';
    userId: number;
    // When stream started, Unix timestamp in seconds
    createdAt: number;
    // Streaming session identifier
    suid: string;
    // Streaming parameters
    streaming: {
        fps: number;
        keyframeInterval: number;
        lossRate: number;
        // Bits per second
        bitrate: {
            total: number,
            audio: number,
            video: number,
        };
        codec: {
            audio: string,
            video: string,
        },
        profileAndLevel: string;
        height: number;
        width: number;
    };
}

// Incoming stream has finished
interface IIncomingStreamDeleted {
    action: 'deleteIncoming';
    userId: number;
    // When stream started, Unix timestamp in seconds
    createdAt: number;
    // Streaming session identifier
    suid: string;
}

// Outgoing stream to end platform has created or updated (there is no separate event for creation here)
interface IOutgoingStreamUpdated {
    action: 'updateOutgoing';
    userId: number;
    // Streaming platform ID on Restream
    platformId: number;
    channelId: number;
    // When outgoing stream started, Unix timestamp in seconds
    createdAt: number;
    // Channel details
    channelIdentifier: string;
    eventIdentifier: string;
    // Streaming parameters
    streaming: {
        // Status from the point of view of Restream
        status: 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED',
        // Bits per second
        bitrate: number,
        bufferedBytes: number,
    };
}

// Outgoing stream has finished
interface IOutgoingStreamDeleted {
    action: 'deleteOutgoing';
    userId: number;
    // Streaming platform ID on Restream
    platformId: number;
    channelId: number;
    // When outgoing stream started, Unix timestamp in seconds
    createdAt: number;
}

// Stream information from the point of view of end platform
interface IStatusesUpdated {
    action: 'updateStatuses';
    userId: number;
    // Streaming platform ID on Restream
    platformId: number;
    channelId: number;
    // When outgoing stream started, Unix timestamp in seconds
    createdAt: number;
    // When the information was collected (this can be a bit outdated cached information for long streaming sessions)
    updatedAt: number;
    // Channel details
    channelIdentifier: string;
    eventIdentifier: string;
    // Information from end platform
    channelViews: number | null;
    followers: number | null;
    gameTitle: string | null;
    online: boolean;
    streamViews: number | null;
    title: string | null;
    viewers: number | null;
}

export type IUpdates =
    IIncomingStreamUpdated |
    IIncomingStreamDeleted |
    IOutgoingStreamUpdated |
    IOutgoingStreamDeleted |
    IStatusesUpdated;
```

NOTE: `null` means that information is not available for the stream (temporarily or permanently)
->
