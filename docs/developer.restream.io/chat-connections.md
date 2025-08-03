<-
### <a name="chat-connections"></a>Connections
###### Used to display the list of connected channels and Discords.

After establishing WebSocket connection, you'll receive messages with `connection_info` action - one for each enabled channel which belongs to supported event sources and one for each connected Discord channel.

Your application should keep the map of connections using `connectionIdentifier` as a key and the last received payload of `connection_info` with that `connectionIdentifier` as a value.
The connection should be deleted from that map only after receiving `connection_closed` with `connectionUuid`(not a `connectionIdentifier`) equivalent to the one saved in the value.
 
You can receive duplicates of exactly the same `connection_info` messages. 
You can either ignore them or just follow the rule and overwrite the previous payload in the map of connections.

Also, there can be a case when you will receive a `connection_closed` message and won't be able to find a connection in the map to delete. This can happen because that connection can be already overwritten by the next one which replaced it. When we need to establish a connection to the same target one more time (let's say chat settings was changed), we will first establish a new one and only then terminate the previous in order to avoid downtime (API will handle event deduplication for you)

Connections have a target which is different for each event source.
The full list of target interfaces can be found in the code snippet to the right.

##### Connection errors
You can receive `connection_info` action with `status = 'error'`. 
In that case, `reason` field will contain error code.
 
List of possible reasons along with description can be found in the table below.

> <span class="warning" /> **Note**: Most reasons are self-explanatory. Only the most common ones will be provided and explained. 

| Reason | Event Source | Description |
|---|---|---|
| `restream_channel_connection_expired` | any | Credentials used to connect to event source API expired. User should go to Restream Dashboard and refresh them. |
| `youtube_livechat_ended` | YouTube | Live chat is no longer live. Broadcast completed. No comments can be received from completed broadcasts. |
| `facebook_event_not_live` | Facebook | LiveVideo is not live. Can get comments only from live events. |
| `youtube_broadcast_completed` | YouTube | Broadcast is completed. No comments can be received from completed broadcasts. |
| `event_not_started` | event-based | No streams via Restream were made from this channel yet. So there is no event to connect to. |
| `discord_invalid_refresh_token` | Discord | User should reconnect that Discord channel via Restream Chat settings. |
| `channel_added_manually` | any | Channel was added to Restream Dashboard manually. We can't get access to event source in such case. |
| `internal` | any | Some internal error occurred. Try to reconnect a channel in Restream Dashboard. If the problem persists - user will need to contact Restream Support in order to resolve that issue. |

<-

->
###### TypeScript interfaces describing connection targets

> <span class="warning" /> **Note**: TypeScript syntax, new interfaces and fields may be added over time


```typescript
interface IConnectionTargetBasic {    
}

interface IConnectionTargetTwitch extends IConnectionTargetBasic {
    owner: {
        avatar?: string;
        displayName: string;
        id: string;
        name?: string;
        url?: string;
    };
    // Restream `channel_id`
    websiteChannelId: number;
}

interface IConnectionTargetYouTube extends IConnectionTargetBasic {
    event: {
        id: string;
        title?: string;
        url: string;
    };
    owner: {
        avatar?: string;
        displayName: string;
        id: string;
    };
    websiteChannelId: number;
}

interface IConnectionTargetFacebookPersonal extends IConnectionTargetBasic {
    liveVideo: {
        id: string;
        status?: string;
        title?: string;
        url?: string;
    };
    user: {
        avatar?: string;
        id: string;
        name: string;
    };
    websiteChannelId: number;
}

interface IConnectionTargetFacebookPage extends IConnectionTargetBasic {
    liveVideo: {
        id: string;
        status?: string;
        title?: string;
        url?: string;
    };
    page: {
        id: string;
        name: string;
        picture?: string;
    };
    websiteChannelId: number;
}

interface IConnectionTargetDLive extends IConnectionTargetBasic {
    owner: {
        avatar?: string;
        displayName: string;
        url: string;
        username: string;
    };
    websiteChannelId: number;
}

interface IConnectionTargetDiscord extends IConnectionTargetBasic {
    channel: {
        id: string,
        name?: string,
        url: string,
    };
    owner?: {
        avatar: string;
        id: string;
        name: string;
    };
    server?: {
        icon: string | null;
        id: string;
        name: string;
    };
}

interface IConnectionTargetLinkedIn extends IConnectionTargetBasic {
    organization?: {
        avatarUrl?: string;
        id: number;
        name: string;
    };
    post: {
        id: string;
        url?: string;
    };
    user?: {
        avatarUrl?: string;
        id?: string;
        name: string;
    };
    websiteChannelId: number;
}

```
->
