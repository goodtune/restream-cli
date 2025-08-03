<-
### <a name="selected-ingest"></a>Selected ingest

###### Get user's selected ingest id

> <span class="info" /> **Required scope:** channel.read

> <span class="warning" /> **Note:** This method requires authentication

Retrieves a user's selected ingest id.

~~~bash
curl -H "Authorization: Bearer [access token]" https://api.restream.io/v2/user/ingest
~~~
<-

->
Success
  ~~~json
  {
    "ingestId": 8
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
