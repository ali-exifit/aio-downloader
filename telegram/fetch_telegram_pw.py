#!/usr/bin/env python3
"""
Scrape public Telegram channels using Playwright (headless browser).
No API credentials needed. Outputs telegram.md at repo root.
"""
import asyncio, json, re, time, requests
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, unquote

from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).parent                # telegram/
CHANNELS_FILE = BASE_DIR / "channels.json"
STATE_FILE = BASE_DIR / "last_ids.json"
OUTPUT_FILE = BASE_DIR.parent / "telegram.md"   # repo root
CONTENT_DIR = BASE_DIR / "content"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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

def download_media(url, channel_name, post_id):
    """Download a media file and return a relative Markdown link."""
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    # Determine extension from URL (often Telegram gives .jpg or .mp4 directly)
    ext = ".jpg"
    if any(k in url.lower() for k in [".mp4", "video", "stream"]):
        ext = ".mp4"
    local_name = f"{channel_name}_{post_id}_{int(time.time())}{ext}"
    local_path = CONTENT_DIR / local_name
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        local_path.write_bytes(resp.content)
        return f"telegram/content/{local_name}"
    except Exception as e:
        print(f"    ⚠️ Media download failed: {e}")
        return None

async def scrape_channel(page, channel_name, last_id):
    """Open the public preview, wait for messages, extract new ones (newest first)."""
    url = f"https://t.me/s/{channel_name}"
    print(f"  🌐 Navigating to {url} ...")
    await page.goto(url, wait_until="networkidle", timeout=30000)

    # Wait for at least one message wrap to appear
    try:
        await page.wait_for_selector("[data-post]", timeout=15000)
    except:
        print("    ❌ No messages found (timeout). Page might be empty or blocked.")
        return []

    # Extract all message containers that have a data-post attribute
    messages = await page.evaluate("""() => {
        const containers = document.querySelectorAll('[data-post]');
        const msgs = [];
        containers.forEach(el => {
            const dataPost = el.getAttribute('data-post');
            if (!dataPost) return;
            const parts = dataPost.split('/');
            if (parts.length < 2) return;
            const channel = parts[0];
            const postId = parseInt(parts[1]);
            if (isNaN(postId)) return;

            // Date
            const timeEl = el.querySelector('time');
            const datetime = timeEl ? timeEl.getAttribute('datetime') : '';

            // Text
            const textEl = el.querySelector('.tgme_widget_message_text');
            const text = textEl ? textEl.innerText : '';

            // Media (photo or video)
            let mediaUrl = null;
            let mediaType = null;
            const photoWrap = el.querySelector('.tgme_widget_message_photo_wrap');
            if (photoWrap) {
                const style = photoWrap.getAttribute('style') || '';
                const match = style.match(/url\\('(.*?)'\\)/);
                if (match) {
                    mediaUrl = match[1];
                    mediaType = 'photo';
                }
            }
            if (!mediaUrl) {
                const videoTag = el.querySelector('video');
                if (videoTag && videoTag.src) {
                    mediaUrl = videoTag.src;
                    mediaType = 'video';
                }
            }

            if (!mediaUrl) {
                // Sometimes media is wrapped as a background of a link with class tgme_widget_message_photo_wrap
                const linkPhoto = el.querySelector('a.tgme_widget_message_photo_wrap');
                if (linkPhoto) {
                    const style = linkPhoto.getAttribute('style') || '';
                    const match = style.match(/url\\('(.*?)'\\)/);
                    if (match) {
                        mediaUrl = match[1];
                        mediaType = 'photo';
                    }
                }
            }

            msgs.push({
                id: postId,
                datetime: datetime,
                text: text,
                media_url: mediaUrl,
                media_type: mediaType
            });
        });
        return msgs;
    }""")

    # Filter new messages and sort newest first
    new_msgs = [m for m in messages if m["id"] > last_id]
    new_msgs.sort(key=lambda x: x["id"], reverse=True)

    # Remove exact duplicates (same id) that may appear due to multiple containers
    seen_ids = set()
    unique = []
    for m in new_msgs:
        if m["id"] not in seen_ids:
            seen_ids.add(m["id"])
            unique.append(m)
    return unique

async def main():
    channels = load_channels()
    state = load_state()
    is_first_run = not state

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        all_entries = []

        for ch_name in channels:
            clean_name = ch_name.lstrip("@")
            last_id = state.get(ch_name, 0)

            msgs = await scrape_channel(page, clean_name, last_id)
            if not msgs:
                print(f"  ℹ️ No new messages for {ch_name}")
                continue

            # Update state with the highest (newest) message id
            state[ch_name] = msgs[0]["id"]

            for msg in msgs:
                # Parse datetime
                dt = datetime.now(timezone.utc)
                if msg["datetime"]:
                    try:
                        dt = datetime.fromisoformat(msg["datetime"]).astimezone(timezone.utc)
                    except:
                        pass

                # Download media if present
                media_md = None
                if msg["media_url"]:
                    media_md = download_media(msg["media_url"], clean_name, msg["id"])

                # Build markdown block
                dt_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                header = f"## {dt_str} — {clean_name}\n"
                if media_md:
                    if msg["media_type"] == "photo":
                        header += f"![Photo]({media_md})\n\n"
                    else:
                        header += f"[🎬 Video]({media_md})\n\n"

                text = msg["text"] or (("📷 Photo" if msg["media_type"]=="photo" else "🎬 Video") if msg["media_type"] else "")
                lines = text.splitlines()
                quoted = "\n> ".join(lines)
                entry = f"{header}> {quoted}\n\n"
                all_entries.append(entry)

            print(f"  ✅ {ch_name}: added {len(msgs)} new messages")

        await browser.close()

    # Write output file
    if not OUTPUT_FILE.exists():
        save_md("# Telegram Channel Archive\n\n")

    if all_entries:
        existing = load_existing_md()
        combined = "".join(all_entries) + existing
        save_md(combined)
        print(f"✅ Total new messages added: {len(all_entries)}")
    else:
        print("ℹ️ No new messages across all channels.")

    save_state(state)

if __name__ == "__main__":
    asyncio.run(main())
