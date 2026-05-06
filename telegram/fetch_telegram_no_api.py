#!/usr/bin/env python3
"""
Scrape public Telegram channels (no API credentials) and download their media.
Outputs telegram.md at the repository root.
"""
import json
import re
import time
import requests
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent                # telegram/
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
        return f"telegram/content/{local_name}"
    except Exception as e:
        print(f"  ⚠️ Failed to download {media_type} from {url}: {e}")
        return None

def fetch_page(channel_name, before=None):
    """Fetch a single page of the channel's public preview."""
    url = f"https://t.me/s/{channel_name}"
    if before:
        url += f"?before={before}"
    print(f"  📡 Fetching {url} ...")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text

def extract_messages_from_html(html, channel_name, last_id):
    """Parse t.me/s/... HTML and return list of message dicts (newest first)."""
    soup = BeautifulSoup(html, "lxml")
    messages = []

    # Use CSS selector that works with multiple classes
    for msg_div in soup.select(".tgme_widget_message_wrap"):
        data_post = msg_div.get("data-post")
        if not data_post:
            continue
        try:
            _, post_id_str = data_post.split("/")
            post_id = int(post_id_str)
        except (ValueError, IndexError):
            continue

        if post_id <= last_id:
            continue

        # Timestamp
        time_tag = msg_div.find("time")
        dt_str = time_tag.get("datetime") if time_tag else ""
        try:
            dt = datetime.fromisoformat(dt_str).astimezone(timezone.utc)
        except Exception:
            dt = datetime.now(timezone.utc)

        # Text content – try the dedicated text class first, fallback to the bubble
        text_div = msg_div.select_one(".tgme_widget_message_text")
        if not text_div:
            text_div = msg_div.select_one(".tgme_widget_message_bubble")
        text = text_div.get_text("\n", strip=True) if text_div else ""

        # Media detection
        media_link = None
        media_type = None

        photo_link = msg_div.select_one(".tgme_widget_message_photo_wrap")
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

    # Sort newest first
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
                header += f"![Photo]({local_path})\n\n"
            else:
                header += f"[🎬 Video]({local_path})\n\n"

    lines = msg["text"].splitlines()
    quoted = "\n> ".join(lines) if lines else ""
    return f"{header}> {quoted}\n\n"

def main():
    channels = load_channels()
    state = load_state()
    is_first_run = not state   # empty dict = first run

    all_new_entries = []

    for ch_name in channels:
        clean_name = ch_name.lstrip("@")
        last_id = state.get(ch_name, 0)

        # ---- Pagination for first run: fetch up to 3 pages ----
        pages_to_fetch = 3 if is_first_run else 1
        before = None
        new_msgs = []
        for _ in range(pages_to_fetch):
            try:
                html = fetch_page(clean_name, before)
            except Exception as e:
                print(f"  ❌ Failed to fetch {ch_name}: {e}")
                break

            msgs = extract_messages_from_html(html, clean_name, last_id)
            if not msgs:
                break

            new_msgs.extend(msgs)
            before = msgs[-1]["id"]   # next page starts before the oldest message we just got
            time.sleep(1)

        if not new_msgs:
            print(f"  ℹ️ No new messages for {ch_name}")
            continue

        # Update state with the highest message id
        state[ch_name] = new_msgs[0]["id"]

        for msg in new_msgs:
            entry = format_message(msg, clean_name)
            all_new_entries.append(entry)

    # Ensure telegram.md always exists, even if empty
    if not OUTPUT_FILE.exists():
        save_md("# Telegram Channel Archive\n\n")

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
