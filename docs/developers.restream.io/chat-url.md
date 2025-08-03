<-
### <a name="chat-url"></a>Chat URL

###### Get a user's chat URL

> <span class="info" /> **Required scope:** chat.read

> <span class="warning" /> **Note**: This method requires authentication

Retrieve a user's chat URL.

~~~bash
curl -H "Authorization: Bearer [access token]" https://api.restream.io/v2/user/webchat/url
~~~

> **Note**: The URL returned has the default parameters set. You can modify these values as needed.
<-

->
Success
  ~~~json
  {
    "webchatUrl": "https://chat.restream.io/embed?token=xxx"
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
