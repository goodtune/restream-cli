"""Test platforms and servers API functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import responses
from click.testing import CliRunner

from restream_io import config
from restream_io.cli import cli
from restream_io.schemas import Platform, PlatformImage, Server


class TestPlatformsAPI:
    """Test platforms API functionality."""

    @responses.activate
    def test_get_platforms(self, mock_client):
        """Test getting platforms from API."""
        platforms_data = [
            {
                "id": 1,
                "name": "Twitch",
                "url": "http://twitch.tv",
                "image": {
                    "png": "https://restream.io/img/api/platforms/platform-1.png",
                    "svg": "https://restream.io/img/api/platforms/platform-1.svg",
                },
                "altImage": {
                    "png": "https://restream.io/img/api/platforms/platform-1-alt.png",
                    "svg": "https://restream.io/img/api/platforms/platform-1-alt.svg",
                },
            },
            {
                "id": 5,
                "name": "Youtube",
                "url": "https://www.youtube.com",
                "image": {
                    "png": "https://restream.io/img/api/platforms/platform-5.png",
                    "svg": "https://restream.io/img/api/platforms/platform-5.svg",
                },
                "altImage": {
                    "png": "https://restream.io/img/api/platforms/platform-5-alt.png",
                    "svg": "https://restream.io/img/api/platforms/platform-5-alt.svg",
                },
            },
        ]

        responses.add(
            "GET",
            "https://api.restream.io/v2/platform/all",
            json=platforms_data,
            status=200,
        )

        platforms = mock_client.get_platforms()

        assert len(platforms) == 2
        assert all(isinstance(p, Platform) for p in platforms)
        assert platforms[0].name == "Twitch"
        assert platforms[0].id == 1
        assert platforms[1].name == "Youtube"
        assert platforms[1].id == 5
        assert isinstance(platforms[0].image, PlatformImage)
        assert isinstance(platforms[0].altImage, PlatformImage)


class TestServersAPI:
    """Test servers API functionality."""

    @responses.activate
    def test_get_servers(self, mock_client):
        """Test getting servers from API."""
        servers_data = [
            {
                "id": 20,
                "name": "Autodetect",
                "url": "live.restream.io",
                "rtmpUrl": "rtmp://live.restream.io/live",
                "latitude": "0.00000000",
                "longitude": "0.00000000",
            },
            {
                "id": 1,
                "name": "EU-West (London, GB)",
                "url": "london.restream.io",
                "rtmpUrl": "rtmp://london.restream.io/live",
                "latitude": "51.50735100",
                "longitude": "-0.12775800",
            },
        ]

        responses.add(
            "GET",
            "https://api.restream.io/v2/server/all",
            json=servers_data,
            status=200,
        )

        servers = mock_client.get_servers()

        assert len(servers) == 2
        assert all(isinstance(s, Server) for s in servers)
        assert servers[0].name == "Autodetect"
        assert servers[0].id == 20
        assert servers[1].name == "EU-West (London, GB)"
        assert servers[1].id == 1


class TestPlatformsCLI:
    """Test platforms CLI command."""

    @responses.activate
    def test_platforms_human_readable_output(self):
        """Test platforms command displays human-readable output by default."""
        platforms_data = [
            {
                "id": 1,
                "name": "Twitch",
                "url": "http://twitch.tv",
                "image": {
                    "png": "https://restream.io/img/api/platforms/platform-1.png",
                    "svg": "https://restream.io/img/api/platforms/platform-1.svg",
                },
                "altImage": {
                    "png": "https://restream.io/img/api/platforms/platform-1-alt.png",
                    "svg": "https://restream.io/img/api/platforms/platform-1-alt.svg",
                },
            }
        ]

        responses.add(
            "GET",
            "https://api.restream.io/v2/platform/all",
            json=platforms_data,
            status=200,
        )

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(cli, ["platforms"])

        assert result.exit_code == 0
        assert "Platform: Twitch" in result.output
        assert "ID: 1" in result.output
        assert "URL: http://twitch.tv" in result.output
        assert "PNG:" in result.output
        assert "SVG:" in result.output

    @responses.activate
    def test_platforms_json_output(self):
        """Test platforms command outputs JSON when --json flag is used."""
        platforms_data = [
            {
                "id": 1,
                "name": "Twitch",
                "url": "http://twitch.tv",
                "image": {
                    "png": "https://restream.io/img/api/platforms/platform-1.png",
                    "svg": "https://restream.io/img/api/platforms/platform-1.svg",
                },
                "altImage": {
                    "png": "https://restream.io/img/api/platforms/platform-1-alt.png",
                    "svg": "https://restream.io/img/api/platforms/platform-1-alt.svg",
                },
            }
        ]

        responses.add(
            "GET",
            "https://api.restream.io/v2/platform/all",
            json=platforms_data,
            status=200,
        )

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(cli, ["platforms", "--json"])

        assert result.exit_code == 0
        output_data = json.loads(result.output.strip())
        assert len(output_data) == 1
        assert output_data[0]["id"] == 1
        assert output_data[0]["name"] == "Twitch"


class TestServersCLI:
    """Test servers CLI command."""

    @responses.activate
    def test_servers_human_readable_output(self):
        """Test servers command displays human-readable output by default."""
        servers_data = [
            {
                "id": 20,
                "name": "Autodetect",
                "url": "live.restream.io",
                "rtmpUrl": "rtmp://live.restream.io/live",
                "latitude": "0.00000000",
                "longitude": "0.00000000",
            }
        ]

        responses.add(
            "GET",
            "https://api.restream.io/v2/server/all",
            json=servers_data,
            status=200,
        )

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(cli, ["servers"])

        assert result.exit_code == 0
        assert "Server: Autodetect" in result.output
        assert "ID: 20" in result.output
        assert "RTMP URL: rtmp://live.restream.io/live" in result.output

    @responses.activate
    def test_servers_json_output(self):
        """Test servers command outputs JSON when --json flag is used."""
        servers_data = [
            {
                "id": 20,
                "name": "Autodetect",
                "url": "live.restream.io",
                "rtmpUrl": "rtmp://live.restream.io/live",
                "latitude": "0.00000000",
                "longitude": "0.00000000",
            }
        ]

        responses.add(
            "GET",
            "https://api.restream.io/v2/server/all",
            json=servers_data,
            status=200,
        )

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(cli, ["servers", "--json"])

        assert result.exit_code == 0
        output_data = json.loads(result.output.strip())
        assert len(output_data) == 1
        assert output_data[0]["id"] == 20
        assert output_data[0]["name"] == "Autodetect"
