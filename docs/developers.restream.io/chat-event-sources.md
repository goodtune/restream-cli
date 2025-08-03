<-
### <a name="chat-event-sources"></a>Event Sources

Events sources are the platforms and services which supported by Restream Chat. 
That means that we can receive events from their APIs and for most of them - send events back (reply) and relay events between them (relay). 
List of supported event sources along with the features available for them provided in the table below.

Some of event sources are called `event-based` (marked _italic_ in the table), which means that every stream has a separate event (link, page, etc.).
In most cases, chat requires for that event to be live in order to be able to connect and operate properly.

| `eventSourceId` | Name                          | Read | Reply | Relay |
| :-------------: | ----------------------------- | :--: | :---: | :---: |
|        1        | Restream                      |      |       |       |
|        2        | Twitch                        |  ✅  |  ✅   |  ✅   |
|       13        | _YouTube_                     |  ✅  |  ✅   |  ✅   |
|       19        | _Facebook (Personal profile)_ |  ✅  |  ❌   |  ❌   |
|       20        | _Facebook (Public page)_      |  ✅  |  ✅   |  ❌   |
|       21        | _Facebook (Group)_            |  ✅  |  ❌   |  ❌   |
|       24        | DLive                         |  ✅  |  ✅   |  ✅   |
|       25        | Discord                       |  ✅  |  ✅   |  ✅   |
|       26        | _LinkedIn_                    |  ✅  |  ❌   |  ❌   |
|       27        | Trovo                         |  ✅  |  ✅   |  ❌   |

<-
