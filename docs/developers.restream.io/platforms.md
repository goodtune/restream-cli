<-
### <a name="platforms"></a>Platforms
###### List all Restream's supported platforms

> <span class="success" /> **Note:** This is a public method, authentication is not required

List all Restream's supported platforms. Platforms are the destinations where users can send their 
streams.

~~~ bash
curl -X GET https://api.restream.io/v2/platform/all
~~~
<-

->
Success
  ~~~ json
  [
      {
          "id": 1,
          "name": "Twitch",
          "url": "http://twitch.tv",
          "image": {
              "png": "https://restream.io/img/api/platforms/platform-1.png",
              "svg": "https://restream.io/img/api/platforms/platform-1.svg"
          }
      },
      {
          "id": 5,
          "name": "Youtube",
          "url": "https://www.youtube.com",
          "image": {
              "png": "https://restream.io/img/api/platforms/platform-5.png",
              "svg": "https://restream.io/img/api/platforms/platform-5.svg"
          }
      },
    ...
  ]
  ~~~
->
