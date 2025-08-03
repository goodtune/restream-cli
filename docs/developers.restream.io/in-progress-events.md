<-

### <a name="in-progress-events"></a>In Progress events

> <span class="info" /> **Required scopes:** stream.read

###### List of user's events

> <span class="warning" /> **Note:** This method requires authentication

Retrieve a list of the user's in-progress events.

```bash
curl -H "Authorization: Bearer [access token]" https://api.restream.io/v2/user/events/in-progress
```

<-

->
Success

```json
[
  {
      "id": "2527849f-f961-4b1d-8ae0-8eae4f068327",
      "status": "in-progress",
      "title": "Event title",
      "description": "Event description",
      "coverUrl": "URL or null",
      "isRecordOnly": false, ( true if the event is streamed in a record-only mode )
      "scheduledFor": 1599983310, (timestamp (seconds) or NULL)
      "startedAt": 1599983310, (timestamp (seconds))
      "finishedAt": null,
      "destinations": [
        {
          "channelId": 1,
          "externalUrl": "URL or null",
          "streamingPlatformId": 5
        }
      ]
  },
  ...
]

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
