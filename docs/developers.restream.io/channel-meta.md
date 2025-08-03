<-
### <a name="channel-meta"></a>Channel Meta

###### Get user channel meta by id

> <span class="info" /> **Required scope:** channel.read
 
> <span class="warning" /> **Note:** This method requires authentication

Retrieve a user channel meta by id.

~~~bash
curl -H "Authorization: Bearer [access token]" https://api.restream.io/v2/user/channel-meta/123456
~~~
<-

->
Success
  ~~~json
    {
        "title": "Channel Title"
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
