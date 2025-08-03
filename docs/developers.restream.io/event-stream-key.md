<-

### <a name="event-stream-key"></a>Event stream key

> <span class="info" /> **Required scopes:** stream.read

###### Get stream key and SRT url for user's event by id

> <span class="warning" /> **Note:** This method requires authentication

Retrieve a stream key and SRT url by event id.
(If user does not have access to SRT streaming - SRT url will have a NULL value in the response )

```bash
curl -H "Authorization: Bearer [access token]" https://api.restream.io/v2/user/events/2527849f-f961-4b1d-8ae0-8eae4f068327/streamKey
```

<-

->
Success

```json
{
  "streamKey": "re_xxx_xxx",
  "srtUrl": "srt://live.restream.io:2010?streamid=srt_xxx_xxx_xxx&passphrase=re_xxx_xxx"
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
