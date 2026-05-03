import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load(rel_path):
    with open(REPO_ROOT / rel_path, encoding="utf-8") as f:
        return json.load(f)


def test_plugin_manifest_exists():
    assert (REPO_ROOT / ".claude-plugin" / "plugin.json").is_file()


def test_plugin_manifest_required_fields():
    data = _load(".claude-plugin/plugin.json")
    assert data["name"] == "pinpoint"
    assert data["version"] == "0.1.0"
    assert isinstance(data.get("description"), str) and data["description"]
    assert data["license"] == "MIT"


def test_marketplace_manifest_exists():
    assert (REPO_ROOT / ".claude-plugin" / "marketplace.json").is_file()


def test_marketplace_lists_pinpoint():
    data = _load(".claude-plugin/marketplace.json")
    assert "plugins" in data and isinstance(data["plugins"], list)
    names = [p["name"] for p in data["plugins"]]
    assert "pinpoint" in names
