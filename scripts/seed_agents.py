"""Registers the CAM/FSR/BSA stub agent cards against a running backend.

Usage: python scripts/seed_agents.py [backend_base_url]
Default backend_base_url is http://localhost:8000.
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

CARDS_DIR = Path(__file__).resolve().parent.parent / "stub_agents" / "agent_cards"
CARD_FILES = ["cam.json", "fsr.json", "bsa.json"]


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
    for filename in CARD_FILES:
        card = json.loads((CARDS_DIR / filename).read_text())
        post_agent(base_url, card)


if __name__ == "__main__":
    main()
