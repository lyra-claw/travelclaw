#!/usr/bin/env python3
"""Amadeus OAuth - copy of shared auth module."""

import json
import os
import time
from pathlib import Path
from typing import Optional
import requests

STATE_DIR = Path(__file__).parent.parent / "state"
TOKEN_FILE = STATE_DIR / "token.json"

def get_base_url() -> str:
    env = os.environ.get("AMADEUS_ENV", "test").lower()
    return "https://api.amadeus.com" if env == "production" else "https://test.api.amadeus.com"

def get_credentials() -> tuple:
    api_key = os.environ.get("AMADEUS_API_KEY")
    api_secret = os.environ.get("AMADEUS_API_SECRET")
    if not api_key or not api_secret:
        raise EnvironmentError("Missing AMADEUS_API_KEY and AMADEUS_API_SECRET")
    return api_key, api_secret

def load_cached_token() -> Optional[dict]:
    if not TOKEN_FILE.exists():
        return None
    try:
        with open(TOKEN_FILE) as f:
            data = json.load(f)
        if data.get("expires_at", 0) > time.time() + 60:
            return data
    except:
        pass
    return None

def save_token(token_data: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)

def fetch_new_token() -> dict:
    api_key, api_secret = get_credentials()
    base_url = get_base_url()
    response = requests.post(
        f"{base_url}/v1/security/oauth2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials", "client_id": api_key, "client_secret": api_secret},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    expires_in = data.get("expires_in", 1799)
    token_data = {
        "access_token": data["access_token"],
        "expires_at": time.time() + expires_in,
    }
    save_token(token_data)
    return token_data

def get_token() -> str:
    cached = load_cached_token()
    if cached:
        return cached["access_token"]
    return fetch_new_token()["access_token"]
