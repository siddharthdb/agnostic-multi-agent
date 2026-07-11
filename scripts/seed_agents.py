"""Registers the CAM/FSR/BSA stub agent cards against a running backend.

Usage: python scripts/seed_agents.py [backend_base_url]
Default backend_base_url is http://localhost:8000.

The cards ship with `localhost:900X` endpoint/health URLs for local dev, where every
process shares one network namespace. In docker-compose, each stub is its own container
reachable only by service name, so this script rewrites the host:port of `endpoint_url`
and `health_check_url` when the matching `{CAM,FSR,BSA}_BASE_URL` env var is set (e.g.
`CAM_BASE_URL=http://cam-stub:8000`), preserving the original path.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

CARDS_DIR = Path(__file__).resolve().parent.parent / "stub_agents" / "agent_cards"
CARD_FILES = {"cam.json": "CAM_BASE_URL", "fsr.json": "FSR_BASE_URL", "bsa.json": "BSA_BASE_URL"}


def rewrite_host(url: str, base_url: str) -> str:
    """Swap `url`'s scheme+netloc for `base_url`'s, keeping `url`'s path/query."""
    parsed = urlsplit(url)
    base = urlsplit(base_url)
    return urlunsplit((base.scheme, base.netloc, parsed.path, parsed.query, parsed.fragment))


def post_agent(base_url: str, card: dict) -> None:
    body = json.dumps(card).encode()
    req = urllib.request.Request(
        f"{base_url}/agents",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"registered {card['name']} -> id={result['id']}")
    except urllib.error.HTTPError as e:
        print(f"failed to register {card['name']}: {e.code} {e.read().decode()}")


def main() -> None:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    for filename, env_var in CARD_FILES.items():
        card = json.loads((CARDS_DIR / filename).read_text())
        stub_base_url = os.environ.get(env_var)
        if stub_base_url:
            card["endpoint_url"] = rewrite_host(card["endpoint_url"], stub_base_url)
            if card.get("health_check_url"):
                card["health_check_url"] = rewrite_host(card["health_check_url"], stub_base_url)
        post_agent(base_url, card)


if __name__ == "__main__":
    main()
