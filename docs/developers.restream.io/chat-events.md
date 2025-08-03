<-
### <a name="chat-events"></a>Events
###### Used to display incoming events.

Action `event` represents a single incoming message collected from one of the supported event sources. 
Event payload will differ depending on the event type. 
The full list of supported event types along with a short description can be found in the table below. 
Typescript interfaces provided in the code snippet to the right.
That list can be extended the same as more fields can be added to interfaces.

| `eventTypeId` | Event Type | Description | 
|:-:|---|---|
| 4 | Twitch Text | Payload can include emojis as UTF symbols and links in text format. Mentions are provided in the text format (@username). Twitch emotes are just words in `text`. The payload includes `replaces`, which point to emojis in the text. Avatar will be provided only if the user has `Display avatar` setting enabled. |
| 5 | YouTube Text | Payload can include emojis as UTF symbols and links in text format. Mentions are provided in the text format (@username). |
| 7 | YouTube Super Chat | Payload contains an amount which was donated and currency. Also, a text message can be added to this event. |
| 8 | YouTube Super Sticker | Payload contains an amount which was donated and currency. StickerId saved for reference, API does not provide a link to an image. Also, altText which describes sticker added to the text field. |
| 11 | Facebook (Personal profile) Text | Payload can include emojis as UTF symbols and links and mentions in text format. Sometimes Facebook can omit information about the author, so fields inside `author` are optional. `parent` field, if present, contains the name of the author of the comment to which this comment was sent as a reply. |
| 12 | Facebook (Personal profile) Sticker | Extended payload of the Facebook (Personal profile) Text event. `link` has a URL of sticker image. |
| 13 | Facebook (Public page) Text | Payload can include emojis as UTF symbols and links and mentions in text format. Sometimes Facebook can omit information about the author, so fields inside `author` are optional. `parent` field, if present, contains the name of the author of the comment to which this comment was sent as a reply. |
| 14 | Facebook (Public page) Sticker | Extended payload of the Facebook (Public page) Text event. `link` has a URL of sticker image. |
| 19 | Facebook (Group) Text | Payload can include emojis as UTF symbols and links and mentions in text format. Facebook omits information about the author in group comments due to privacy concerns. This information available only if user granted permissions to see its name and picture. Otherwise `author` object will remain empty. `parent` field, if present, contains the name of the author of the comment to which this comment was sent as a reply. |
| 20 | Facebook (Group) Sticker | Extended payload of the Facebook (Group) Text event. `link` has a URL of sticker image. Facebook omits information about the author in group comments due to privacy concerns. This information available only if user granted permissions to see its name and picture. Otherwise `author` object will remain empty. `parent` field, if present, contains the name of the author of the comment to which this comment was sent as a reply. |
| 2 | DLive Text | Payload can include emojis as UTF symbols and links in text format. Mentions are provided in the text format (@username). |
| 3 | DLive Emoji | Payload contains a link to image with DLive emoji. |
| 1 | Discord Text | Payload can include emojis as UTF symbols and links. Mentions are provided in the text format (@username). |
| 21 | LinkedIn Text | It can include emojis as UTF symbols and links and mentions in text format. The author can be retrieved only for users who allows getting such information, so this field is optional. |

You can use `connectionIdentifier` to associate an event with the connection from which it received.

You **can't** use `eventIdentifier` to uniquely identify events.

Each event has enough information to render it the same way it shown in Restream chat. 
If event has some attachments (stickers for example) payload will contain all data so no additional requests need to be made in order to display event content.

#### Emojis and replaces
Emojis provided as UTF-8 symbols, so it's your decision about how to render them (Links processing and display is your choice as well.). 
In cases when event source has a support for custom emojis, `replaces` will be included into event payload. 
`replaces` is an array of objects with required `from`, `to` and `type` fields, where `from` is a position in the event text from which you should start the replacement and `to` is a position of replacement end. 
Replaces provided in reverse order so you can just iterate over them and replace directly in the text and don't worry about replacement position change.

All images used for attachments are stored on event source side. So Restream can't guaranty that all of them will be accessible all the time.
<-

->
> <span class="warning" /> **Note**: TypeScript syntax, new actions and fields may be added over time

```typescript
interface IEventTypePayloadBasic {}

interface IEventTypePayloadTwitchText extends IEventTypePayloadBasic {
    author: {
        avatar: string | null;
        badges: Array<{
            title: string;
            imageUrl: string;
            clickUrl: string | null;
        }>;
        // color of the nickname and `/me` messages 
        color: string | null;
        displayName: string | null;
        id: string;
        name: string;
        subscribedFor: number | null;
    };
    // message created by bot
    bot: boolean;
    contentModifiers: {
        me: boolean;
        whisper: boolean;
    };
    replaces: Array<{
        from: number;
        to: number;
        type: 'imageUrl';
        payload: {
            url: string;
        };
    }>;
    text: string;
}

interface IEventTypePayloadYouTubeText extends IEventTypePayloadBasic {
    author: {
        id: string;
        avatar: string;
        displayName: string;
        isChatModerator: boolean;
        isChatOwner: boolean;
        isChatSponsor: boolean;
        isVerified: boolean;
    };
    bot: boolean;
    text: string;
}

interface IEventTypePayloadYouTubeSuperChat extends IEventTypePayloadBasic {
    author: {
        id: string;
        avatar: string;
        displayName: string;
        isChatModerator: boolean;
        isChatOwner: boolean;
        isChatSponsor: boolean;
        isVerified: boolean;
    };
    bot: false;
    donation: {
        amount: string;
        currencyString: string;
        tier: number;
    };
    text: string;
}

interface IEventTypePayloadYouTubeSuperSticker extends IEventTypePayloadBasic {
    author: {
        id: string;
        avatar: string;
        displayName: string;
        isChatModerator: boolean;
        isChatOwner: boolean;
        isChatSponsor: boolean;
        isVerified: boolean;
    };
    bot: boolean;
    donation: {
        amount: string;
        currencyString: string;
        stickerId: string;
        tier: number;
    };
    text: string;
}

interface IEventTypePayloadFacebookPersonalText extends IEventTypePayloadBasic {
    author: {
        id?: string;
        name?: string;
        picture?: string;
    };
    bot: false;
    parent?: {
        name?: string;
    };
    text: string;
}

interface IEventTypePayloadFacebookPersonalSticker extends IEventTypePayloadBasic {
    author: {
        id?: string;
        name?: string;
        picture?: string;
    };
    bot: false;
    parent?: {
        name?: string;
    };
    link: string;
    text: string;
}

interface IEventTypePayloadFacebookPageText extends IEventTypePayloadBasic {
    author: {
        id?: string;
        name?: string;
        picture?: string;
    };
    bot: false;
    parent?: {
        name?: string;
    };
    text: string;
}

interface IEventTypePayloadFacebookPageSticker extends IEventTypePayloadBasic {
    author: {
        id?: string;
        name?: string;
        picture?: string;
    };
    bot: false;
    parent?: {
        name?: string;
    };
    link: string;
    text: string;
}

interface IEventTypePayloadFacebookGroupTextMessage extends IEventTypePayloadBasic {
    author: {
        id?: string;
        name?: string;
        picture?: string;
    };
    bot: false;
    parent?: {
        name?: string;
    };
    text: string;
}

interface IEventTypePayloadFacebookGroupSticker extends IEventTypePayloadBasic {
    author: {
        id?: string;
        name?: string;
        picture?: string;
    };
    bot: false;
    parent?: {
        name?: string;
    };
    link: string;
    text: string;
}

interface IEventTypePayloadDLiveText extends IEventTypePayloadBasic {
    author: {
        avatar: string;
        badges: string[];
        name: string;
        partnerStatus: string;
        role: string;
        roomRole: string;
        subscribing: boolean;
        username: string;
    };
    bot: boolean;
    text: string;
}

interface IEventTypePayloadDLiveEmoji extends IEventTypePayloadBasic {
    author: {
        avatar: string;
        badges: string[];
        name: string;
        partnerStatus: string;
        role: string;
        roomRole: string;
        subscribing: boolean;
        username: string;
    };
    bot: boolean;
    link: string;
}

interface IEventTypePayloadDiscordText extends IEventTypePayloadBasic {
    author: {
        avatar: string | null;
        discriminator: string;
        id: string;
        name: string;
        nickname: string | null;
        nicknameColor: string | null;
        roles: Array<{
            color: string;
            name: string;
        }> | null;
    };
    bot: boolean;
    text: string;
}

interface IEventTypePayloadLinkedInText extends IEventTypePayloadBasic {
    author?: {
        avatarUrl?: string;
        name: string;
    };
    bot: false;
    text: string;
}
```
->
