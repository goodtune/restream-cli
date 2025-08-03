<-

### <a name="events-history"></a>Events history

> <span class="info" /> **Required scopes:** stream.read

###### List of user's finished and missed events

> <span class="warning" /> **Note:** This method requires authentication

Retrieve a list of the user's finished and missed events.

```bash
curl -H "Authorization: Bearer [access token]" https://api.restream.io/v2/user/events/history?page=1&limit=10
```

<-

->
Success

```json
{
  "items": [
    {
      "id": "2527849f-f961-4b1d-8ae0-8eae4f068327",
      "status": "finished", ( or "missed" )
      "title": "Event title",
      "description": "Event description",
      "coverUrl": "URL or null",
      "isRecordOnly": false, ( true if the event was streamed in a record-only mode )
      "scheduledFor": 1599983310, (timestamp (seconds) or NULL)
      "startedAt": 1599983310, (timestamp (seconds) or NULL)
      "finishedAt": 1599983310, (timestamp (seconds) or NULL)
      "destinations": [
        {
          "channelId": 1,
          "externalUrl": "URL or null",
          "streamingPlatformId": 5
        }
      ]
    },
    ...
  ],
  "pagination": {
    "pages_total": 10,
    "page": 1,
    "limit": 10
  }
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
