<-

### <a name="event"></a>Event

> <span class="info" /> **Required scopes:** stream.read

###### Get user event by id

> <span class="warning" /> **Note:** This method requires authentication

Retrieve a user event by id.

```bash
curl -H "Authorization: Bearer [access token]" https://api.restream.io/v2/user/events/2527849f-f961-4b1d-8ae0-8eae4f068327
```

<-

->
Success

```json
  {
    "id": "2527849f-f961-4b1d-8ae0-8eae4f068327",
    "status": "upcoming | in-progress | finished",
    "title": "Event title",
    "description": "Event decription",
    "coverUrl": "URL or null",
    "isRecordOnly": false, ( true if the event is/was streamed in a record-only mode )
    "scheduledFor": 1599983310, (timestamp (seconds) or NULL),
    "startedAt": 1599983310, (timestamp (seconds) or NULL)
    "finishedAt": 1599983310, (timestamp (seconds) or NULL)
    "destinations": [
      {
        "channelId": 1,
        "externalUrl": "URL or null",
        "streamingPlatformId": 5
      }
    ]
  }
```

Error

```json
{
  "error": {
    "statusCode": 401,
    "status": 401,
    "code": 401,
    "message": "Invalid token: access token is invalid",
    "name": "invalid_token"
  }
}
```

->
