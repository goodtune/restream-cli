<-
### <a name="servers"></a>Ingest servers
###### List all Restream's ingest servers

> <span class="success" /> **Note:** This is a public method, authentication is not required

List all Restream's ingest servers. Ingest servers are the RTMP ingestion points where users can send their 
streams.

~~~ bash
curl -X GET https://api.restream.io/v2/server/all
~~~
<-

->
Success
  ~~~ json
  [
      {
          "id": 20,
          "name": "Autodetect",
          "url": "live.restream.io",
          "rtmpUrl": "rtmp://live.restream.io/live",
          "latitude": "0.00000000",
          "longitude": "0.00000000"
      },
      {
          "id": 1,
          "name": "EU-West (London, GB)",
          "url": "london.restream.io",
          "rtmpUrl": "rtmp://london.restream.io/live",
          "latitude": "51.50735100",
          "longitude": "-0.12775800"
      },
    ...
  ]
  ~~~
->
