<-

### <a name="event-srt-stream-keys"></a>Event SRT stream keys

> <span class="info" /> **Required scopes:** stream.read

###### Get SRT stream keys and url for user's event by id

> <span class="warning" /> **Note:** This method requires authentication

> <span class="warning" /> SRT is available on Business and custom Enterprise plans only.

Retrieve SRT stream keys and url by event id.

```bash
curl -H "Authorization: Bearer [access token]" https://api.restream.io/v2/user/events/2527849f-f961-4b1d-8ae0-8eae4f068327/srt/streamKey
```

<-

->
Success

```json
{
  "streamId": "srt_xxx_xxx_xxx",
  "passPhrase": "re_xxx_xxx",
  "url": "srt://live.restream.io:2010?streamid=srt_xxx_xxx_xxx&passphrase=re_xxx_xxx"
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
