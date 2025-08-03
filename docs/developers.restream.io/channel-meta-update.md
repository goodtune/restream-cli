<-

### <a name="channel-meta-update"></a>Channel Meta Update

###### Update a user's channel meta

> <span class="info" /> **Required scope:** channel.write

> <span class="warning" /> **Note:** This method requires authentication

Update channel title.

```bash
curl -X PATCH -H "Authorization: Bearer [access token]" -H "Content-Type: application/json" -d '{ "title": "New title" }' https://api.restream.io/v2/user/channel-meta/123456
```

<-

->
Request body

```json

 {
   "title": "New title",
   "description": "New description" (optional field)
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
