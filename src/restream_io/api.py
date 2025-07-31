import requests

from .errors import APIError

BASE_URL = "https://api.restream.io/v1"  # placeholder; confirm from docs


class RestreamClient:
    def __init__(self, session: requests.Session, token: str):
        self.session = session
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_profile(self):
        resp = self.session.get(f"{BASE_URL}/profile")
        if not resp.ok:
            raise APIError(f"Failed to get profile: {resp.status_code} {resp.text}")
        return resp.json()

    def list_channels(self):
        resp = self.session.get(f"{BASE_URL}/channels")
        if not resp.ok:
            raise APIError(f"Failed to list channels: {resp.status_code} {resp.text}")
        return resp.json()

    def get_channel(self, channel_id: str):
        resp = self.session.get(f"{BASE_URL}/channels/{channel_id}")
        if not resp.ok:
            raise APIError(f"Failed to get channel: {resp.status_code} {resp.text}")
        return resp.json()

    def list_events(self):
        resp = self.session.get(f"{BASE_URL}/events")
        if not resp.ok:
            raise APIError(f"Failed to list events: {resp.status_code} {resp.text}")
        return resp.json()
