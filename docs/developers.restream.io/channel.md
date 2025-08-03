<-
### <a name="channel"></a>Channel

###### Get user channel by id

> <span class="info" /> **Required scope:** channel.read
 
> <span class="warning" /> **Note:** This method requires authentication

Retrieve a user channel by id.

~~~bash
curl -H "Authorization: Bearer [access token]" https://api.restream.io/v2/user/channel/123456
~~~
<-

->
Success
  ~~~json
    {
        "id": 123456,
        "streamingPlatformId": 000,
        "embedUrl": "https://beam.pro/embed/player/xxx",
        "url": "https://beam.pro/xxx",
        "identifier": "xxx",
        "displayName": "xxx",
        "active": true
    }
  ~~~
Error
  ~~~json
  {
    "error": {
      "statusCode": 401,
      "status": 401,
      "code": 401,
      "message": "Invalid token: access token is invalid",
      "name": "invalid_token"
    }
  }
  ~~~
->
