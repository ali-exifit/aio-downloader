#!/usr/bin/env python3
"""
Scrape public Telegram channels with Playwright.
Generates a self-contained index.html (RTL, Vazirmatn font) to avoid
GitHub's 1 MB Markdown rendering limit.
"""
import asyncio, json, re, time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
import jdatetime
from playwright.async_api import async_playwright

# ---- paths ----
SCRIPT_DIR = Path(__file__).resolve().parent          # .github/script/
REPO_ROOT = SCRIPT_DIR.parent.parent                  # repo root

CHANNELS_FILE = REPO_ROOT / "telegram" / "channels.json"
STATE_FILE    = REPO_ROOT / "telegram" / "last_ids.json"
OUTPUT_HTML   = REPO_ROOT / "index.html"              # served by GitHub Pages
CONTENT_DIR   = REPO_ROOT / "telegram" / "content"

IRAN_TZ = ZoneInfo("Asia/Tehran")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ---- HTML template ----
HTML_TEMPLATE = """<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>آرشیو کانال‌های تلگرام</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Vazirmatn', sans-serif;
    background: #f5f5f5;
    color: #222;
    line-height: 1.8;
  }
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }
  .header {
    text-align: center;
    padding: 2rem 0;
    border-bottom: 2px solid #ddd;
    margin-bottom: 2rem;
  }
  .header h1 { font-size: 1.8rem; }
  .post {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.07);
    margin-bottom: 2rem;
    padding: 1.5rem;
  }
  .post-header {
    font-weight: bold;
    margin-bottom: 0.8rem;
    color: #555;
    font-size: 0.9rem;
  }
  .post-text {
    white-space: pre-wrap;
    margin-bottom: 1rem;
  }
  .media img, .media video {
    max-width: 100%;
    border-radius: 8px;
    margin-bottom: 0.5rem;
  }
  .separator {
    border: none;
    border-top: 1px solid #eee;
    margin: 2rem 0;
  }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📢 آرشیو کانال‌های تلگرام</h1>
    <p>آخرین پیام‌ها از کانال‌های منتخب</p>
  </div>
  <!-- INSERT_NEW_ENTRIES_HERE -->
  <hr class="separator">
  <!-- OLD_ENTRIES_BELOW -->
</div>
</body>
</html>"""

# ---- helper functions ----
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

def download_media(url, channel_name, post_id):
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
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

def convert_to_jalali(utc_dt: datetime) -> str:
    """UTC datetime → Jalali string (Iran time)."""
    local_dt = utc_dt.astimezone(IRAN_TZ)
    jdate = jdatetime.datetime.fromgregorian(datetime=local_dt)
    return jdate.strftime("%Y/%m/%d %H:%M")

def build_post_html(msg):
    """Generate HTML for one message."""
    ch = msg["_channel"]
    dt_utc = msg["_dt_utc"]
    media_rel = None
    if msg["media_url"]:
        media_rel = download_media(msg["media_url"], ch, msg["id"])

    if dt_utc:
        date_str = convert_to_jalali(dt_utc)
    else:
        date_str = f"???-??-?? ??:?? (post {msg['id']})"

    html = f'<div class="post">\n'
    html += f'  <div class="post-header">📅 {date_str} &nbsp;|&nbsp; 📣 @{ch}</div>\n'

    if media_rel:
        if msg.get("media_type") == "video":
            html += f'  <div class="media"><video controls src="{media_rel}"></video></div>\n'
        else:
            html += f'  <div class="media"><img src="{media_rel}" alt="Photo"></div>\n'

    text = msg["text"] or ""
    if not text:
        if msg.get("media_type") == "photo":
            text = "📷 عکس"
        elif msg.get("media_type") == "video":
            text = "🎬 ویدیو"
    lines = text.splitlines()
    safe_lines = [line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for line in lines]
    joined = "<br>".join(safe_lines)
    html += f'  <div class="post-text">{joined}</div>\n'
    html += f'</div>\n'
    return html

# ---- Playwright scraping ----
async def scrape_channel_all(page, channel_name, last_id, max_scrolls):
    url = f"https://t.me/s/{channel_name}"
    print(f"  🌐 Loading {url} ...")
    await page.goto(url, wait_until="networkidle", timeout=30000)

    try:
        await page.wait_for_selector("[data-post]", timeout=15000)
    except:
        print("    ❌ No messages found on initial page.")
        return []

    all_messages = []
    seen_ids = set()

    for scroll_count in range(1, max_scrolls + 1):
        current_msgs = await page.evaluate("""() => {
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

                const timeEl = el.querySelector('time');
                const datetime = timeEl ? timeEl.getAttribute('datetime') : '';

                const textEl = el.querySelector('.tgme_widget_message_text');
                const text = textEl ? textEl.innerText : '';

                let mediaUrl = null, mediaType = null;
                const photoWrap = el.querySelector('.tgme_widget_message_photo_wrap');
                if (photoWrap) {
                    const style = photoWrap.getAttribute('style') || '';
                    const match = style.match(/url\\('(.*?)'\\)/);
                    if (match) { mediaUrl = match[1]; mediaType = 'photo'; }
                }
                if (!mediaUrl) {
                    const videoTag = el.querySelector('video');
                    if (videoTag && videoTag.src) { mediaUrl = videoTag.src; mediaType = 'video'; }
                }
                if (!mediaUrl) {
                    const linkPhoto = el.querySelector('a.tgme_widget_message_photo_wrap');
                    if (linkPhoto) {
                        const style = linkPhoto.getAttribute('style') || '';
                        const match = style.match(/url\\('(.*?)'\\)/);
                        if (match) { mediaUrl = match[1]; mediaType = 'photo'; }
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

        new_added = 0
        for m in current_msgs:
            if m["id"] not in seen_ids:
                seen_ids.add(m["id"])
                all_messages.append(m)
                new_added += 1

        print(f"    Scroll {scroll_count}: total unique={len(all_messages)}, new this scroll={new_added}")

        if all_messages:
            oldest_id = min(msg["id"] for msg in all_messages)
            if oldest_id <= last_id:
                print(f"    Reached last_id ({last_id}) – stopping scroll.")
                break

        if new_added == 0:
            print("    No new messages added – end of history.")
            break

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

        try:
            await page.wait_for_function(
                f"document.querySelectorAll('[data-post]').length > {len(seen_ids)}",
                timeout=5000
            )
        except:
            print("    No further messages loaded after scroll.")
            break

    filtered = [m for m in all_messages if m["id"] > last_id]
    filtered.sort(key=lambda x: x["id"], reverse=True)
    return filtered

# ---- main ----
async def main():
    channels = load_channels()
    state = load_state()
    is_first_run = not state
    scroll_limit = 15 if is_first_run else 50

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        all_messages = []
        for ch_name in channels:
            clean_name = ch_name.lstrip("@")
            last_id = state.get(ch_name, 0)
            msgs = await scrape_channel_all(page, clean_name, last_id, max_scrolls=scroll_limit)
            if not msgs:
                print(f"  ℹ️ No new messages for {ch_name}")
                continue

            for m in msgs:
                dt_utc = None
                if m.get("datetime"):
                    try:
                        dt_utc = datetime.fromisoformat(m["datetime"]).astimezone(ZoneInfo("UTC"))
                    except:
                        print(f"    ⚠️ Cannot parse datetime '{m['datetime']}' for post {m['id']}")
                else:
                    print(f"    ⚠️ No datetime element for post {m['id']}")
                m["_dt_utc"] = dt_utc
                m["_channel"] = clean_name

            all_messages.extend(msgs)
            print(f"  ✅ {ch_name}: fetched {len(msgs)} new messages")

        await browser.close()

    if not all_messages:
        print("ℹ️ No new messages across all channels.")
        save_state(state)
        return   # <-- important: do NOT create an empty index.html

    # Separate dated / undated
    dated   = [m for m in all_messages if m["_dt_utc"] is not None]
    undated = [m for m in all_messages if m["_dt_utc"] is None]

    dated.sort(key=lambda m: m["_dt_utc"], reverse=True)
    undated.sort(key=lambda m: m["id"], reverse=True)
    sorted_messages = dated + undated

    # Build HTML for new posts
    new_entries_html = ""
    for msg in sorted_messages:
        new_entries_html += build_post_html(msg)

    # Read existing HTML (if any) and extract the old entries part
    if OUTPUT_HTML.exists():
        existing = OUTPUT_HTML.read_text(encoding="utf-8")
        marker = "<!-- OLD_ENTRIES_BELOW -->"
        if marker in existing:
            idx = existing.index(marker)
            old_part = existing[idx:]   # includes marker and everything after
        else:
            old_part = existing
    else:
        old_part = ""

    # Assemble final HTML: template header + new entries + old entries
    final_html = HTML_TEMPLATE.replace("<!-- INSERT_NEW_ENTRIES_HERE -->", new_entries_html)
    final_html = final_html.replace("<!-- OLD_ENTRIES_BELOW -->", old_part)

    OUTPUT_HTML.write_text(final_html, encoding="utf-8")

    # Update state
    for ch_name in channels:
        clean_name = ch_name.lstrip("@")
        ch_msgs = [m for m in all_messages if m["_channel"] == clean_name]
        if ch_msgs:
            state[ch_name] = max(m["id"] for m in ch_msgs)

    print(f"✅ Added {len(sorted_messages)} new messages to index.html")
    save_state(state)

if __name__ == "__main__":
    asyncio.run(main())
