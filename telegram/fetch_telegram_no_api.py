#!/usr/bin/env python3
"""
Scrape public Telegram channels (no API credentials) and download media.
Outputs telegram.md at the repository root.
"""
import json
import os
import re
import time
import requests
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent                # telegram/ folder
CHANNELS_FILE = BASE_DIR / "channels.json"
STATE_FILE = BASE_DIR / "last_ids.json"
OUTPUT_FILE = BASE_DIR.parent / "telegram.md"   # repo root
CONTENT_DIR = BASE_DIR / "content"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def load_channels():
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_existing_md():
    if OUTPUT_FILE.exists():
        return OUTPUT_FILE.read_text(encoding="utf-8")
    return ""

def save_md(content):
    OUTPUT_FILE.write_text(content, encoding="utf-8")

def download_media(url, channel_name, post_id, media_type="photo"):
    """Download a media file and return the relative markdown link path."""
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    ext = ".jpg" if media_type == "photo" else ".mp4"
    local_name = f"{channel_name}_{post_id}_{int(time.time())}{ext}"
    local_path = CONTENT_DIR / local_name

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        local_path.write_bytes(resp.content)
        # Relative path from repo root (telegram.md's location)
        return f"telegram/content/{local_name}"
    except Exception as e:
        print(f"  ⚠️ Failed to download {media_type} from {url}: {e}")
        return None

def extract_messages_from_html(html, channel_name, last_id):
    """Parse t.me/s/... HTML and return list of message dicts (newest first)."""
    soup = BeautifulSoup(html, "lxml")
    messages = []

    for msg_div in soup.find_all("div", class_="tgme_widget_message_wrap"):
        data_post = msg_div.get("data-post")
        if not data_post:
            continue
        try:
            chan, post_id_str = data_post.split("/")
            post_id = int(post_id_str)
        except (ValueError, IndexError):
            continue
        if post_id <= last_id:
            continue

        time_tag = msg_div.find("time")
        dt_str = time_tag.get("datetime") if time_tag else ""
        try:
            dt = datetime.fromisoformat(dt_str).astimezone(timezone.utc)
        except:
            dt = datetime.now(timezone.utc)

        text_div = msg_div.find("div", class_="tgme_widget_message_text")
        text = text_div.get_text("\n", strip=True) if text_div else ""

        media_link = None
        media_type = None

        photo_link = msg_div.find("a", class_="tgme_widget_message_photo_wrap")
        if photo_link:
            style = photo_link.get("style", "")
            bg_match = re.search(r"url\('(.*?)'\)", style)
            if bg_match:
                media_link = bg_match.group(1)
                media_type = "photo"

        if not media_link:
            video_tag = msg_div.find("video")
            if video_tag:
                media_link = video_tag.get("src")
                media_type = "video"

        if not text and media_link:
            text = "📷 Photo" if media_type == "photo" else "🎬 Video"

        messages.append({
            "id": post_id,
            "date": dt,
            "text": text,
            "media_url": media_link,
            "media_type": media_type,
        })

    messages.sort(key=lambda x: x["id"], reverse=True)
    return messages

def format_message(msg, channel_name):
    """Convert a message dict into a markdown block."""
    dt_str = msg["date"].strftime("%Y-%m-%d %H:%M:%S UTC")
    header = f"## {dt_str} — {channel_name}\n"

    if msg["media_url"] and msg["media_type"]:
        local_path = download_media(msg["media_url"], channel_name, msg["id"], msg["media_type"])
        if local_path:
            if msg["media_type"] == "photo":
                # Inline image display
                media_md = f"![Photo]({local_path})\n\n"
            else:
                # Video: clickable link (embedding not possible on GitHub)
                media_md = f"[🎬 Video]({local_path})\n\n"
            header += media_md

    lines = msg["text"].splitlines()
    quoted = "\n> ".join(lines) if lines else ""
    return f"{header}> {quoted}\n\n"

def main():
    channels = load_channels()
    state = load_state()

    all_new_entries = []

    for ch_name in channels:
        clean_name = ch_name.lstrip("@")
        url = f"https://t.me/s/{clean_name}"
        print(f"📡 Fetching {url} ...")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f"  ❌ Failed to fetch {url}: {e}")
            continue

        last_id = state.get(ch_name, 0)
        messages = extract_messages_from_html(resp.text, clean_name, last_id)

        if not messages:
            print(f"  ℹ️ No new messages for {ch_name}")
            continue

        state[ch_name] = messages[0]["id"]

        for msg in messages:
            entry = format_message(msg, clean_name)
            all_new_entries.append(entry)

        time.sleep(1)

    if all_new_entries:
        existing_md = load_existing_md()
        combined = "".join(all_new_entries) + existing_md
        save_md(combined)
        print(f"✅ Added {len(all_new_entries)} new messages.")
    else:
        print("ℹ️ No new messages across all channels.")

    save_state(state)

if __name__ == "__main__":
    main()
