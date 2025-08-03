<-

### <a name="upcoming-events"></a>Upcoming events

> <span class="info" /> **Required scopes:** stream.read

###### List of user's events

> <span class="warning" /> **Note:** This method requires authentication

Retrieve a list of the user's events.

```bash
curl -H "Authorization: Bearer [access token]" https://api.restream.io/v2/user/events/upcoming
```

**Query Parameters:**

| Parameter   | Type    | Description                                                             |
| ----------- | ------- | ----------------------------------------------------------------------- |
| `source`    | integer | Filter events by source type (`1` - Studio, `2` - Encoder, `3` - Video) |
| `scheduled` | boolean | When `true`, returns only scheduled events                              |

Example request:

```bash
curl -H "Authorization: Bearer [access token]" https://api.restream.io/v2/user/events/upcoming?source=1&scheduled=true
```

<-

->
Success

```json
[
  {
      "id": "2527849f-f961-4b1d-8ae0-8eae4f068327",
      "status": "upcoming",
      "title": "Event title",
      "description": "Event description",
      "coverUrl": "URL or null",
      "scheduledFor": 1599983310, (timestamp (seconds) or NULL)
      "startedAt": null,
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
