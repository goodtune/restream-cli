<-

### <a name="stream-key"></a>Stream key

###### Get a user's stream key and SRT url

> <span class="info" /> **Required scope:** stream.read

> <span class="warning" /> **Note:** This method requires authentication

Retrieve a user's stream key and SRT url.
(If user does not have access to SRT streaming - SRT url will have a NULL value in the response )

```bash
curl -H "Authorization: Bearer [access token]" https://api.restream.io/v2/user/streamKey
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
