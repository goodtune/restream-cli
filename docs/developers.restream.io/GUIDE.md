# Restream.io REST API - Quick Hacker's Guide

## Public Endpoints (No Auth)
- **GET** `/v2/platform/all` - List all supported platforms
- **GET** `/v2/server/all` - List all ingest servers

## User & Profile
- **GET** `/v2/user/profile` - Get user profile (`profile.read`)

## Channels  
- **GET** `/v2/user/channel/{id}` - Get channel details (`channel.read`)
- **PATCH** `/v2/user/channel/{id}` - Enable/disable channel (`channel.write`)
- **GET** `/v2/user/channel-meta/{id}` - Get channel metadata (`channel.read`)
- **PATCH** `/v2/user/channel-meta/{id}` - Update title/description (`channel.write`)
- **GET** `/v2/user/ingest` - Get selected ingest server (`channel.read`)

## Events (All require `stream.read`)
- **GET** `/v2/user/events/{id}` - Get specific event
- **GET** `/v2/user/events/upcoming?source=X&scheduled=true` - List upcoming events
- **GET** `/v2/user/events/in-progress` - List active events  
- **GET** `/v2/user/events/history?page=X&limit=Y` - List finished events

## Stream Keys (All require `stream.read`)
- **GET** `/v2/user/streamKey` - Get primary stream key + SRT URL
- **GET** `/v2/user/events/{id}/streamKey` - Get event-specific stream key
- **GET** `/v2/user/events/{id}/srt/streamKey` - Get SRT keys (Business+ only)

## Chat
- **GET** `/v2/user/webchat/url` - Get embeddable chat URL (`chat.read`)

## WebSocket (Real-time)
- **WSS** `streaming.api.restream.io/ws?accessToken=X` - Stream status updates
- **WSS** `chat.api.restream.io/ws?accessToken=X` - Chat events

---
**Base URL:** `https://api.restream.io`  
**Auth:** `Authorization: Bearer {token}`  
**Total REST Endpoints:** 15