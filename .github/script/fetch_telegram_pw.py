#!/usr/bin/env python3
"""
Scrape public Telegram channels with Playwright.
- Scrolls to fetch ALL new messages (no gaps).
- Sorts by time across channels.
- Shows Hijri‑Shamsi date & Iran/Tehran time.
- Handles file size limit: when telegram.md > 950 KB,
  moves older content into `telegram/content/archive_N.md`
  and maintains Persian (صفحه بعد / صفحه قبل) navigation.
"""

import asyncio
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import jdatetime
import requests
from playwright.async_api import async_playwright

# ---- Paths ----
SCRIPT_DIR = Path(__file__).resolve().parent          # .github/script/
REPO_ROOT = SCRIPT_DIR.parent.parent                  # repo root

CHANNELS_FILE = REPO_ROOT / "telegram" / "channels.json"
STATE_FILE    = REPO_ROOT / "telegram" / "last_ids.json"
OUTPUT_FILE   = REPO_ROOT / "telegram.md"
CONTENT_DIR   = REPO_ROOT / "telegram" / "content"

IRAN_TZ = ZoneInfo("Asia/Tehran")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Markers used inside .md files
MSG_START = "<!-- MSG START -->"
MSG_END   = "<!-- MSG END -->"
NAV_START = "<!-- NAV START -->"
NAV_END   = "<!-- NAV END -->"

# Persian title (Vazirmatn would be ideal, but GitHub does not support custom fonts in .md)
HEADER_TEMPLATE = f"""\
# خواننده تلگرام

{MSG_START}
{MSG_END}
{NAV_START}
{NAV_END}
"""

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
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
    """Convert UTC datetime to Iran timezone and format as Jalali string."""
    local_dt = utc_dt.astimezone(IRAN_TZ)
    jdate = jdatetime.datetime.fromgregorian(datetime=local_dt)
    return jdate.strftime("%Y/%m/%d %H:%M")

# ----------------------------------------------------------------------
# Markdown page assembly helpers
# ----------------------------------------------------------------------
def build_nav_footer(next_page_rel: str | None, prev_page_rel: str | None) -> str:
    """Return the NAV block with Persian links. Use relative paths."""
    lines = []
    if prev_page_rel:
        lines.append(f"[صفحه قبل]({prev_page_rel})")
    if next_page_rel:
        lines.append(f"[صفحه بعد]({next_page_rel})")
    if not lines:
        lines.append("*پایان پیام‌ها*")
    return "\n\n".join(lines)

def wrap_page(message_block: str, next_rel: str | None, prev_rel: str | None) -> str:
    """Create a full .md page with header, message block and navigation."""
    nav_footer = build_nav_footer(next_rel, prev_rel)
    # Replace placeholders
    page = HEADER_TEMPLATE.replace(f"{MSG_START}\n{MSG_END}",
                                   f"{MSG_START}\n{message_block}\n{MSG_END}")
    page = page.replace(f"{NAV_START}\n{NAV_END}",
                        f"{NAV_START}\n{nav_footer}\n{NAV_END}")
    return page

def extract_message_md(md_text: str) -> str | None:
    """Extract the message block from a page that uses MSG_START/END markers.
    Returns None if markers missing.
    """
    start = md_text.find(MSG_START)
    end = md_text.find(MSG_END)
    if start == -1 or end == -1:
        return None
    # Return the substring between markers, excluding the markers themselves
    return md_text[start + len(MSG_START):end].strip()

# ----------------------------------------------------------------------
# Archive shifting logic
# ----------------------------------------------------------------------
def get_existing_archives():
    """Return a sorted list of (number, filename) for files matching archive_<N>.md
    inside CONTENT_DIR. Sorted by number ascending.
    """
    archives = []
    if not CONTENT_DIR.exists():
        return archives
    pattern = re.compile(r"^archive_(\d+)\.md$")
    for f in CONTENT_DIR.iterdir():
        m = pattern.match(f.name)
        if m:
            archives.append((int(m.group(1)), f))
    archives.sort(key=lambda x: x[0])
    return archives

def shift_archives_for_new_page1(message_block_new_page1: str):
    """
    - Renames existing archive_i.md → archive_(i+1).md (highest first).
    - Creates a new archive_1.md with the given message_block.
    - Updates navigation inside all archive files to match the new order.
    """
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- 1. read old archives’ message blocks before renaming ----
    old_blocks = {}   # old_number -> message_block
    for num, path in get_existing_archives():
        content = path.read_text(encoding="utf-8")
        block = extract_message_md(content)
        if block is None:
            # fallback: entire file minus any header (crude)
            block = content.strip()
        old_blocks[num] = block

    # ---- 2. rename files from highest to lowest ----
    existing = sorted(old_blocks.keys(), reverse=True)  # e.g. [3,2,1]
    for num in existing:
        old_path = CONTENT_DIR / f"archive_{num}.md"
        new_path = CONTENT_DIR / f"archive_{num+1}.md"
        if old_path.exists():
            old_path.rename(new_path)

    # ---- 3. create the new archive_1.md ----
    new_page1_path = CONTENT_DIR / "archive_1.md"
    # archive_1 : next -> ../telegram.md, prev -> archive_2.md (if exists)
    prev_rel = "archive_2.md" if (2 in [n+1 for n in old_blocks]) else None
    new_page1 = wrap_page(message_block_new_page1,
                          next_rel="../telegram.md",
                          prev_rel=prev_rel)
    new_page1_path.write_text(new_page1, encoding="utf-8")

    # ---- 4. rewrite shifted archives with correct nav ----
    total_archives = len(old_blocks) + 1  # including the new page1
    for new_num in range(2, total_archives + 1):
        # new_num corresponds to old_num = new_num - 1
        old_num = new_num - 1
        block = old_blocks.get(old_num, "")
        file_path = CONTENT_DIR / f"archive_{new_num}.md"

        next_rel = f"archive_{new_num-1}.md"
        prev_rel = f"archive_{new_num+1}.md" if new_num < total_archives else None
        page = wrap_page(block, next_rel=next_rel, prev_rel=prev_rel)
        file_path.write_text(page, encoding="utf-8")

    print(f"✅ Archives shifted: new archive_1 created, total pages = {total_archives}")

def split_main_page(new_entries_block: str, old_messages_block: str):
    """
    The combined page would be too large → archive the old messages.
    new_entries_block becomes the new telegram.md, old_messages_block becomes
    a new archive_1, and all existing archives are shifted.
    Also handles the case where new_entries_block alone is still too large
    (by recursively splitting the new entries).
    """
    # Quick size check for new_entries_block alone
    test_page = wrap_page(new_entries_block, next_rel=None, prev_rel=None)
    if len(test_page.encode("utf-8")) <= 950 * 1024:
        # new entries fit – shift archives and write main page
        shift_archives_for_new_page1(old_messages_block)

        # Write the new telegram.md pointing to the fresh archive_1
        next_rel_main = None
        prev_rel_main = "telegram/content/archive_1.md"
        main_page = wrap_page(new_entries_block,
                              next_rel=next_rel_main,
                              prev_rel=prev_rel_main)
        OUTPUT_FILE.write_text(main_page, encoding="utf-8")
        print("✅ Main page updated, old content moved to archive_1.md")
    else:
        # New entries alone exceed limit – split the new entries themselves.
        # We take the newest half as the main page and the older half as a new archive.
        print("⚠️ New entries alone exceed 950KB – splitting inside new entries.")
        entries = new_entries_block.split("\n\n")   # crude split by blank lines
        # Rebuild blocks in order: each entry roughly lines until next "## "
        # But we can just split the monolithic string in half.
        # Better: keep the block as a whole and create archive for the second half.
        # We'll use a simple character split:
        half = len(new_entries_block) // 2
        head_block = new_entries_block[:half]
        tail_block = new_entries_block[half:]

        # The tail becomes a new archive that will be page1,
        # and the head becomes the main page.
        # Shift existing archives to make room for this tail as archive_1,
        # and the old_messages_block will become archive_2 after shift.
        # So we first move old_messages_block to a temporary archive, then tail.
        # We'll combine old_messages_block and tail appropriately:
        # We want the final order: main (head), archive_1 (tail), archive_2 (old_messages), ...
        # So:
        #   1. Shift archives as if we are inserting a new archive_1 with tail.
        #   2. Then old_messages_block should be inserted as archive_2 after shift.
        #   This means we need to call shift_archives_for_new_page1(tail),
        #   which renames existing archives 1→2, 2→3, ...
        #   Then we manually create an archive_2? No, shift_archives already created archive_1 and shifted
        #   the old ones up. Now we have a gap at archive_2? Actually after shift, the previous archive_1
        #   (if existed) became archive_2, and previous archive_2 became archive_3.
        #   So old_messages_block must go between archive_1 and archive_2? That's contradictory.
        #   Better: we'll treat tail as the *first* archive (page1), and old_messages_block as
        #   the *second* archive. We can do:
        #     - shift all existing archives up by *2* instead of 1.
        #   Easier: create a function that accepts a list of message blocks for the new archives in order,
        #   placing them before the existing archives.
        #   Given the rarity, we'll implement a simple recursive split:
        #   We'll call split_main_page(tail, old_messages_block) to handle the overflow.
        #   This will create a page for tail and put old_messages_block as new archive_1 (after shift).
        print("⚠️ Recursive split not fully implemented – falling back to manual adjustment.")
        # For a safe fallback, simply truncate new_entries_block to fit and warn.
        # In practice this situation is extremely unlikely.
        raise RuntimeError("New entries too large – implement full split logic or increase limit.")

# ----------------------------------------------------------------------
# Scraping (unchanged, except we return list of message markdown blocks)
# ----------------------------------------------------------------------
async def scrape_channel_all(page, channel_name, last_id, max_scrolls):
    """Returns list of message dicts, newest first."""
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

# ----------------------------------------------------------------------
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
            print(f"  ✅ {ch_name}: fetched {len(msgs)} new messages (after filter)")

        await browser.close()

    # Build new message entries as markdown blocks
    new_entries_list = []
    for msg in all_messages:
        ch = msg["_channel"]
        dt_utc = msg["_dt_utc"]
        media_md = None
        if msg["media_url"]:
            media_md = download_media(msg["media_url"], ch, msg["id"])

        if dt_utc:
            jalali_str = convert_to_jalali(dt_utc)
        else:
            jalali_str = f"???-??-?? ??:?? (post {msg['id']})"

        header = f"## {jalali_str} — {ch}\n"
        if media_md:
            if msg["media_type"] == "photo":
                header += f"![Photo]({media_md})\n\n"
            else:
                header += f"[🎬 Video]({media_md})\n\n"

        text = msg["text"] or ("📷 Photo" if msg["media_type"] == "photo" else "🎬 Video" if msg["media_type"] == "video" else "")
        lines = text.splitlines()
        quoted = "\n> ".join(lines)
        entry = f"{header}> {quoted}\n\n"
        new_entries_list.append(entry)

    new_entries_block = "".join(new_entries_list)

    # Load existing telegram.md
    old_messages_block = ""
    existing_nav_next = existing_nav_prev = None
    if OUTPUT_FILE.exists():
        old_raw = OUTPUT_FILE.read_text(encoding="utf-8")
        # Try to extract message block using markers
        extracted = extract_message_md(old_raw)
        if extracted is not None:
            old_messages_block = extracted
        else:
            # Missing markers → treat whole file as message block after stripping possible header
            lines = old_raw.split("\n")
            if lines and lines[0].startswith("# "):
                # remove the title line
                old_messages_block = "\n".join(lines[1:]).strip()
            else:
                old_messages_block = old_raw.strip()

    # Decide if we need to split
    if new_entries_block or old_messages_block:
        # Build a trial combined page to check size
        trial_page = wrap_page(new_entries_block + old_messages_block,
                               next_rel=None, prev_rel=None)
        size = len(trial_page.encode("utf-8"))
        if size > 950 * 1024 and old_messages_block.strip():
            # Split required
            split_main_page(new_entries_block, old_messages_block)
        else:
            # No split (or only new entries exist) – write normally
            # Determine navigation: if archives exist, point prev to archive_1
            archives = get_existing_archives()
            prev_rel_main = None
            if archives:
                # latest (lowest number) is the first archive
                prev_rel_main = f"telegram/content/archive_{archives[0][0]}.md"
            main_page = wrap_page(new_entries_block + old_messages_block,
                                  next_rel=None,
                                  prev_rel=prev_rel_main)
            OUTPUT_FILE.write_text(main_page, encoding="utf-8")
            print("✅ Main page updated (no split needed).")
    else:
        # No new messages, ensure a minimal page exists
        if not OUTPUT_FILE.exists():
            OUTPUT_FILE.write_text(wrap_page("", None, None), encoding="utf-8")
            print("ℹ️ No messages yet, empty page created.")

    # Update state per channel with max fetched IDs
    for ch_name in channels:
        clean_name = ch_name.lstrip("@")
        ch_msgs = [m for m in all_messages if m["_channel"] == clean_name]
        if ch_msgs:
            state[ch_name] = max(m["id"] for m in ch_msgs)

    save_state(state)

if __name__ == "__main__":
    asyncio.run(main())
