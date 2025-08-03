<-
### <a name="channel-update"></a>Channel Update

###### Update a user's channel

> <span class="info" /> **Required scope:** channel.write

> <span class="warning" /> **Note:** This method requires authentication

Enable or disable channel in their Restream Dashboard.

```bash
curl -X PATCH -H "Authorization: Bearer [access token]" -H "Content-Type: application/json" -d '{ "active": true }' https://api.restream.io/v2/user/channel/123456
```
<-

->
Request body
  ```json

   {
     "active": true
   }

  ```
  Success
  ```text
   <Empty body>
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
