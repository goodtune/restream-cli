"""Test channel management functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import responses
from click.testing import CliRunner

from restream_io import config
from restream_io.cli import cli
from restream_io.schemas import ChannelMeta


class TestChannelMetaAPI:
    """Test channel metadata API functionality."""

    @responses.activate
    def test_get_channel_meta(self, mock_client):
        """Test getting channel metadata from API."""
        meta_data = {
            "title": "Test Channel Title",
            "description": "Test channel description",
        }

        responses.add(
            "GET",
            "https://api.restream.io/v2/user/channel-meta/123456",
            json=meta_data,
            status=200,
        )

        meta = mock_client.get_channel_meta("123456")

        assert isinstance(meta, ChannelMeta)
        assert meta.title == "Test Channel Title"
        assert meta.description == "Test channel description"

    @responses.activate
    def test_update_channel(self, mock_client):
        """Test updating channel active status."""
        responses.add(
            "PATCH",
            "https://api.restream.io/v2/user/channel/123456",
            status=204,  # Empty response
        )

        # Should not raise an exception
        mock_client.update_channel("123456", True)

        # Verify the request was made with correct payload
        request = responses.calls[0].request
        assert json.loads(request.body) == {"active": True}

    @responses.activate
    def test_update_channel_meta(self, mock_client):
        """Test updating channel metadata."""
        responses.add(
            "PATCH",
            "https://api.restream.io/v2/user/channel-meta/123456",
            status=204,  # Empty response
        )

        # Should not raise an exception
        mock_client.update_channel_meta("123456", "New Title", "New Description")

        # Verify the request was made with correct payload
        request = responses.calls[0].request
        assert json.loads(request.body) == {
            "title": "New Title",
            "description": "New Description",
        }

    @responses.activate
    def test_update_channel_meta_title_only(self, mock_client):
        """Test updating channel metadata with title only."""
        responses.add(
            "PATCH",
            "https://api.restream.io/v2/user/channel-meta/123456",
            status=204,  # Empty response
        )

        # Should not raise an exception
        mock_client.update_channel_meta("123456", "New Title")

        # Verify the request was made with correct payload
        request = responses.calls[0].request
        assert json.loads(request.body) == {"title": "New Title"}


class TestChannelSetCLI:
    """Test channel set CLI command."""

    @responses.activate
    def test_channel_set_active(self):
        """Test channel set command with --active flag."""
        responses.add(
            "PATCH",
            "https://api.restream.io/v2/user/channel/123456",
            status=204,
        )

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(cli, ["channel", "set", "123456", "--active"])

        assert result.exit_code == 0
        assert "Channel 123456 enabled successfully" in result.output

    @responses.activate
    def test_channel_set_inactive(self):
        """Test channel set command with --inactive flag."""
        responses.add(
            "PATCH",
            "https://api.restream.io/v2/user/channel/123456",
            status=204,
        )

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(cli, ["channel", "set", "123456", "--inactive"])

        assert result.exit_code == 0
        assert "Channel 123456 disabled successfully" in result.output

    def test_channel_set_no_flag(self):
        """Test channel set command without active/inactive flag."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(cli, ["channel", "set", "123456"])

        assert result.exit_code == 1
        assert "Please specify --active or --inactive" in result.output

    @responses.activate
    def test_channel_set_not_found(self):
        """Test channel set command with non-existent channel."""
        responses.add(
            "PATCH",
            "https://api.restream.io/v2/user/channel/999999",
            json={"message": "Channel not found"},
            status=404,
        )

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(cli, ["channel", "set", "999999", "--active"])

        assert result.exit_code == 1
        assert "Channel not found: 999999" in result.output


class TestChannelMetaCLI:
    """Test channel meta CLI commands."""

    @responses.activate
    def test_channel_meta_get_human_readable(self):
        """Test channel meta get command with human-readable output."""
        meta_data = {
            "title": "Test Channel Title",
            "description": "Test channel description",
        }

        responses.add(
            "GET",
            "https://api.restream.io/v2/user/channel-meta/123456",
            json=meta_data,
            status=200,
        )

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(cli, ["channel", "meta", "get", "123456"])

        assert result.exit_code == 0
        assert "Channel Metadata:" in result.output
        assert "Title: Test Channel Title" in result.output
        assert "Description: Test channel description" in result.output

    @responses.activate
    def test_channel_meta_get_json_output(self):
        """Test channel meta get command with JSON output."""
        meta_data = {
            "title": "Test Channel Title",
            "description": "Test channel description",
        }

        responses.add(
            "GET",
            "https://api.restream.io/v2/user/channel-meta/123456",
            json=meta_data,
            status=200,
        )

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(
                    cli, ["channel", "meta", "get", "123456", "--json"]
                )

        assert result.exit_code == 0
        output_data = json.loads(result.output.strip())
        assert output_data["title"] == "Test Channel Title"
        assert output_data["description"] == "Test channel description"

    @responses.activate
    def test_channel_meta_get_not_found(self):
        """Test channel meta get command with non-existent channel."""
        responses.add(
            "GET",
            "https://api.restream.io/v2/user/channel-meta/999999",
            json={"message": "Channel not found"},
            status=404,
        )

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(cli, ["channel", "meta", "get", "999999"])

        assert result.exit_code == 1
        assert "Channel not found: 999999" in result.output

    @responses.activate
    def test_channel_meta_set_with_description(self):
        """Test channel meta set command with title and description."""
        responses.add(
            "PATCH",
            "https://api.restream.io/v2/user/channel-meta/123456",
            status=204,
        )

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(
                    cli,
                    [
                        "channel",
                        "meta",
                        "set",
                        "123456",
                        "--title",
                        "New Title",
                        "--description",
                        "New Description",
                    ],
                )

        assert result.exit_code == 0
        assert "Channel 123456 metadata updated successfully" in result.output

    @responses.activate
    def test_channel_meta_set_title_only(self):
        """Test channel meta set command with title only."""
        responses.add(
            "PATCH",
            "https://api.restream.io/v2/user/channel-meta/123456",
            status=204,
        )

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(
                    cli,
                    ["channel", "meta", "set", "123456", "--title", "New Title Only"],
                )

        assert result.exit_code == 0
        assert "Channel 123456 metadata updated successfully" in result.output

    @responses.activate
    def test_channel_meta_set_not_found(self):
        """Test channel meta set command with non-existent channel."""
        responses.add(
            "PATCH",
            "https://api.restream.io/v2/user/channel-meta/999999",
            json={"message": "Channel not found"},
            status=404,
        )

        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir)
            tokens_file = config_path / "tokens.json"
            tokens_file.parent.mkdir(parents=True, exist_ok=True)
            tokens_file.write_text('{"access_token": "fake-token"}')

            with patch.object(config, "CONFIG_PATH", config_path):
                result = runner.invoke(
                    cli, ["channel", "meta", "set", "999999", "--title", "New Title"]
                )

        assert result.exit_code == 1
        assert "Channel not found: 999999" in result.output
