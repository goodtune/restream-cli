<-
### <a name="chat-reply"></a>Reply
###### Used to display replies send from Restream Chat.

When reply created in Restream Chat, you will receive `reply_created` action. 
It will contain `replyUuid` which used to associate that reply with `reply_accepted`, `reply_failed`, and `reply_confirmed` actions received afterwards. 
Be aware that `reply_confirmed` can be received before `reply_accepted`. 
Also if `reply_confirmed` not received at all that doesn't mean that message wasn't delivered. 
`reply_confirmed` send only when we 100% sure that message was delivered, which not always can't be guaranteed because of specifics of each event source.

In Restream Chat, a reply can be sent to all connections (common reply) or one connection (direct reply).
`eventSourceId` will be set to 1 when this is a common reply (Event Source with `id = 1` is Restream).
For direct reply, it will be set to Event Source to which that connection belongs. 

In case of error, `reply_failed` action will have `reason` field with text code of the occurred error.

List of possible reasons along with description can be found in the table below.

> <span class="warning" /> **Note**: Most reasons are self-explanatory. Only the most common ones will be provided and explained.

| Reason | Event Source | Description |
|---|---|---|
| `dlive_api_send_message_rate_limit` | DLive | Rate limit on DLive side. |
| `facebook_event_not_live` | Facebook | The event should be live in order to leave a comment. |
| `connection_in_error_state` | any | The connection has an error. We won't send a reply while the connection is broken. |
| `discord_rate_limit` | Discord | Rate limit on Discord side. |
| `connection_not_established_yet` | any | The connection is not established yet, can't send reply right now. |
| `internal` | any | Some internal error occurred. Try to send reply one more time. If the problem persists - user will need to contact Restream Support in order to resolve that issue. |

<-
