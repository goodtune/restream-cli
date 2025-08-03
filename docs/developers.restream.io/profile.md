<-
### <a name="profile"></a>Profile

###### List user's profile details

> <span class="info" /> **Required scope:** profile.read

> <span class="warning" /> **Note:** This method requires authentication

Retrieve a user's profile information.

~~~ bash
curl -H "Authorization: Bearer [access token]" https://api.restream.io/v2/user/profile
~~~
<-

->
Success
  ```json
  {
    "id": 000,
    "username": "xxx",
    "email": "xxx"
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
