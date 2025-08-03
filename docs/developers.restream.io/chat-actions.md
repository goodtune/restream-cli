<-
### <a name="chat-actions"></a>Actions

Each message received from the API is a JSON encoded object which represents one of actions. 
The full list of actions along with a short description and the TypeScript interfaces names provided in the table below.
Interfaces provided in the code snippet to the right.
A detailed description of different actions provided in the separate sections below.

> <span class="warning" /> **Note**: That list can be extended over time

| Action | Interface | Description |
|--------------|--------------|--------------|
| **heartbeat** | `IActionHeartbeat` | Sent by server approx every 45 seconds. If not received in 60 seconds - consider the connection broken and try to reconnect. |
| **connection_info** | `IActionConnectionInfo` | Information about connections to the event sources. |
| **connection_closed** | `IActionConnectionClosed` | Sent when the connection is closed. |
| **event** | `IActionEvent` | The event received from the event source. |
| **reply_created** | `IActionReplyCreated` | The user created a reply. |
| **reply_accepted** | `IActionReplyAccepted` | The event source accepted the reply. |
| **reply_confirmed** | `IActionReplyConfirmed` | The reply delivery confirmed. |
| **reply_failed** | `IActionReplyFailed` | The reply failed to send to the event source. |
| **relay_accepted** | `IActionRelayAccepted` | The event source accepted the relay. |
| **relay_confirmed** | `IActionRelayConfirmed` | The relay delivery confirmed. |
| **relay_failed** | `IActionRelayFailed` | The relay failed to send to the event source. |

<-
 
->
###### TypeScript interfaces describing available actions

> <span class="warning" /> **Note**: TypeScript syntax, new actions and fields may be added over time

```typescript
type IActionType = 
    'heartbeat'
    | 'connection_info' 
    | 'connection_closed' 
    | 'event' 
    | 'reply_created' 
    | 'reply_accepted' 
    | 'reply_confirmed' 
    | 'reply_failed' 
    | 'relay_accepted' 
    | 'relay_confirmed'
    | 'relay_failed';

interface IBasicAction {
    action: IActionType;
    payload: {};
    // timestamp in seconds
    timestamp: number;
}

interface IActionHeartbeat extends IBasicAction {
    action: 'heartbeat';
}

interface IActionConnectionInfo extends IBasicAction {
    action: 'connection_info';
    payload: {
        // unique identifier of connection target
        connectionIdentifier: string;
        // unique identifier of connection
        connectionUuid: string;
        eventSourceId: number;
        // text code of error, not null only when `status` = 'error'
        reason: string | null;
        status: 'connecting' | 'connected' | 'error';
        // event source specific target description
        target: IConnectionTargetBasic;
        userId: number;
    };
}

interface IActionConnectionClosed extends IBasicAction {
    action: 'connection_closed';
    payload: {
        connectionUuid: string;
        reason: 
            // channel deleted or disabled
            'removed' 
            // replaced by another connection
            | 'replaced' 
            // no longer needed
            | 'expired'
            // replaced by another connection
            | 'superseded' 
            // instance which serving that connection is shutting down
            | 'shutdown' 
            // connection was disabled before it was established
            | 'connection_establish_too_long'    
            | 'internal';
    };   
}

interface IActionEvent extends IBasicAction {
    action: 'event';
    payload: {
        connectionIdentifier: string;
        // do NOT use it to uniquely identify events
        eventIdentifier: string;
        // event type specific payload
        eventPayload: IEventTypePayloadBasic;
        eventSourceId: number;
        eventTypeId: number;
        userId: number;
    };
}

interface IActionReplyCreated extends IBasicAction {
    action: 'reply_created';
    payload: {
        clientReplyUuid: string;
        connectionIdentifiers: [string];
        eventSourceId: number;
        replyUuid: string;
        text: string;
    };
}

interface IActionReplyAccepted extends IBasicAction {
    action: 'reply_accepted';
    payload: {
        connectionIdentifier: string;
        replyUuid: string;
    };
}

interface IActionReplyConfirmed extends IBasicAction {
    action: 'reply_confirmed';
    payload: {
        connectionIdentifier: string;
        replyUuid: string;
    };
}

interface IActionReplyFailed extends IBasicAction {
    action: 'reply_failed';
    payload: {
        connectionIdentifier: string;
        // text code of the error
        reason: string;
        replyUuid: string;
    };
}

interface IActionRelayAccepted extends IBasicAction {
    action: 'relay_accepted';
    payload: {
        connectionIdentifier: string;
        // `eventIdentifier` of the event which was relayed
        sourceEventIdentifier: string;
    };
}

interface IActionRelayConfirmed extends IBasicAction {
    action: 'relay_confirmed';
    payload: {
        connectionIdentifier: string;
        sourceEventIdentifier: string;
    };
}

interface IActionRelayFailed extends IBasicAction {
    action: 'relay_failed';
    payload: {
        connectionIdentifier: string;
        // text code of the error
        reason: string;
        sourceEventIdentifier: string;
    };
}
```
->
