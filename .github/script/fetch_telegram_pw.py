#!/usr/bin/env python3
"""
Scrape public Telegram channels with Playwright.
- Adds a Hijri‑Shamsi update timestamp for each script run.
- Downloads photos, videos, AND documents (all file types).
- Sorts messages by ID (newest first) across channels.
- Handles file size limit with archive pages.
- Deduplicates posts based on (channel, post_id) to prevent repeats.
- Centers media and shows captions in right‑to‑left (RTL) for Persian.
- Shows a notice when no new posts are found in an update cycle.
"""

import asyncio
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import jdatetime
import requests
from playwright.async_api import async_playwright

# ---- Paths ----
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

CHANNELS_FILE = REPO_ROOT / "telegram" / "channels.json"
STATE_FILE    = REPO_ROOT / "telegram" / "last_ids.json"
OUTPUT_FILE   = REPO_ROOT / "telegram.md"
CONTENT_DIR   = REPO_ROOT / "telegram" / "content"

IRAN_TZ = ZoneInfo("Asia/Tehran")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

MSG_START = "<!-- MSG START -->"
MSG_END   = "<!-- MSG END -->"
NAV_START = "<!-- NAV START -->"
NAV_END   = "<!-- NAV END -->"

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
def safe_filename(name: str, max_length: int = 100) -> str:
    """Truncate filename to a safe length, preserving the extension."""
    if len(name) <= max_length:
        return name
    stem, dot, ext = name.rpartition(".")
    if not dot:                     # no extension
        return name[:max_length]
    keep = max_length - len(ext) - 4  # room for '...' + dot
    if keep <= 0:                   # extension itself too long
        return name[:max_length]
    prefix = stem[:keep // 2]
    suffix = stem[-(keep - keep // 2):]
    return f"{prefix}...{suffix}.{ext}"


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


def build_nav_footer(next_page_rel: str | None, prev_page_rel: str | None) -> str:
    lines = []
    if prev_page_rel:
        lines.append(f"[صفحه قبل]({prev_page_rel})")
    if next_page_rel:
        lines.append(f"[صفحه بعد]({next_page_rel})")
    if not lines:
        lines.append("*پایان پیام‌ها*")
    return "\n\n".join(lines)


def wrap_page(message_block: str, next_rel: str | None, prev_rel: str | None) -> str:
    nav_footer = build_nav_footer(next_rel, prev_rel)
    page = HEADER_TEMPLATE.replace(f"{MSG_START}\n{MSG_END}",
                                   f"{MSG_START}\n{message_block}\n{MSG_END}")
    page = page.replace(f"{NAV_START}\n{NAV_END}",
                        f"{NAV_START}\n{nav_footer}\n{NAV_END}")
    return page


def extract_message_md(md_text: str) -> str | None:
    start = md_text.find(MSG_START)
    end = md_text.find(MSG_END)
    if start == -1 or end == -1:
        return None
    return md_text[start + len(MSG_START):end].strip()


def get_existing_archives():
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


def parse_post_header(header_line: str):
    line = header_line.strip()
    if not line.startswith("## "):
        return None, None
    m = re.search(r"## (.+?) — post (\d+)", line)
    if m:
        return m.group(1).strip(), int(m.group(2))
    m = re.search(r"post (\d+)\)?\s*—\s*(.+)$", line)
    if m:
        return m.group(2).strip(), int(m.group(1))
    m = re.search(r"## .+? — (.+)$", line)
    if m:
        return m.group(1).strip(), None
    return None, None


def deduplicate_messages(old_block: str, new_ids_set: set[tuple[str, int]]) -> str:
    parts = re.split(r"(?=\n## )", old_block)
    kept = []
    for part in parts:
        first_line = part.split("\n")[0]
        ch, pid = parse_post_header(first_line)
        if pid is not None and ch is not None and (ch, pid) in new_ids_set:
            continue
        kept.append(part)
    return "".join(kept)


# ----------------------------------------------------------------------
# Media download
# ----------------------------------------------------------------------
def download_media(url, channel_name, post_id, media_type='photo', filename=None):
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    # --- choose initial extension based on media_type ---
    ext_map = {'photo': '.jpg', 'video': '.mp4', 'document': '.dat'}
    if filename is None:
        ext = ext_map.get(media_type, '.jpg')
        local_name = f"{channel_name}_{post_id}_{int(time.time())}{ext}"
    else:
        if len(filename) > 100:
            filename = safe_filename(filename, max_length=100)
        local_name = filename

    local_path = CONTENT_DIR / local_name

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()

        # --- use Content-Type to correct the extension ---
        content_type = resp.headers.get('Content-Type', '').lower()
        ext_map_mime = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/webp': '.webp',
            'video/mp4': '.mp4',
            'video/webm': '.webm',
            'video/quicktime': '.mov',
            'application/pdf': '.pdf',
            # add more if needed
        }
        correct_ext = None
        for mime, extension in ext_map_mime.items():
            if mime in content_type:
                correct_ext = extension
                break

        if correct_ext and not local_name.endswith(correct_ext):
            # rename file
            new_local_name = str(Path(local_name).stem) + correct_ext
            local_path = CONTENT_DIR / new_local_name
            local_name = new_local_name
            print(f"    ℹ️ Corrected extension -> {local_name}")

        local_path.write_bytes(resp.content)
        return f"telegram/content/{local_name}"

    except Exception as e:
        print(f"    ⚠️ Media download failed: {e}")
        return None


def download_document(post_url, channel_name, post_id):
    print(f"    📄 Fetching document page: {post_url}")
    try:
        resp = requests.get(post_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        html = resp.text

        match = re.search(
            r'<a\s[^>]*class="tgme_widget_message_document_wrap"[^>]*\shref="([^"]+)"',
            html
        )
        if not match:
            print("    ⚠️ No document download link found on the post page.")
            return None
        doc_url = match.group(1)
        if doc_url.startswith("/"):
            doc_url = "https://t.me" + doc_url

        # Try to get a meaningful filename
        parsed = urlparse(doc_url)
        path = parsed.path
        if path and "/" in path:
            potential_name = path.split("/")[-1]
            if potential_name:
                filename = safe_filename(potential_name, max_length=100)
            else:
                filename = None
        else:
            filename = None

        # Fallback if nothing useful was extracted
        if not filename or not any(c in filename for c in (".", "_")):
            ext = ".dat"
            filename = f"{channel_name}_{post_id}_{int(time.time())}{ext}"

        print(f"    ⬇️ Downloading document: {doc_url} -> {filename}")
        return download_media(doc_url, channel_name, post_id,
                              media_type='document', filename=filename)

    except Exception as e:
        print(f"    ⚠️ Document download failed: {e}")
        return None


# ----------------------------------------------------------------------
# Archive shifting
# ----------------------------------------------------------------------
def shift_archives_for_new_page1(message_block_new_page1: str):
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    old_blocks = {}
    for num, path in get_existing_archives():
        content = path.read_text(encoding="utf-8")
        block = extract_message_md(content)
        if block is None:
            block = content.strip()
        old_blocks[num] = block

    existing = sorted(old_blocks.keys(), reverse=True)
    for num in existing:
        old_path = CONTENT_DIR / f"archive_{num}.md"
        new_path = CONTENT_DIR / f"archive_{num+1}.md"
        if old_path.exists():
            old_path.rename(new_path)

    new_page1_path = CONTENT_DIR / "archive_1.md"
    prev_rel = "archive_2.md" if (2 in [n+1 for n in old_blocks]) else None
    new_page1 = wrap_page(message_block_new_page1,
                          next_rel="../telegram.md",
                          prev_rel=prev_rel)
    new_page1_path.write_text(new_page1, encoding="utf-8")

    total_archives = len(old_blocks) + 1
    for new_num in range(2, total_archives + 1):
        old_num = new_num - 1
        block = old_blocks.get(old_num, "")
        file_path = CONTENT_DIR / f"archive_{new_num}.md"
        next_rel = f"archive_{new_num-1}.md"
        prev_rel = f"archive_{new_num+1}.md" if new_num < total_archives else None
        page = wrap_page(block, next_rel=next_rel, prev_rel=prev_rel)
        file_path.write_text(page, encoding="utf-8")

    print(f"✅ Archives shifted: new archive_1 created, total pages = {total_archives}")


def split_main_page(new_entries_block: str, old_messages_block: str):
    test_page = wrap_page(new_entries_block, next_rel=None, prev_rel=None)
    if len(test_page.encode("utf-8")) <= 950 * 1024:
        shift_archives_for_new_page1(old_messages_block)
        next_rel_main = None
        prev_rel_main = "telegram/content/archive_1.md"
        main_page = wrap_page(new_entries_block,
                              next_rel=next_rel_main,
                              prev_rel=prev_rel_main)
        OUTPUT_FILE.write_text(main_page, encoding="utf-8")
        print("✅ Main page updated, old content moved to archive_1.md")
    else:
        print("⚠️ New entries alone exceed 950KB – splitting inside new entries.")
        half = len(new_entries_block) // 2
        head_block = new_entries_block[:half]
        tail_block = new_entries_block[half:]
        shift_archives_for_new_page1(old_messages_block)
        main_page = wrap_page(head_block, next_rel=None,
                              prev_rel="telegram/content/archive_1.md")
        OUTPUT_FILE.write_text(main_page, encoding="utf-8")
        print("⚠️ Some new messages may be lost due to size limit.")


# ----------------------------------------------------------------------
# Scraping
# ----------------------------------------------------------------------
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

                const textEl = el.querySelector('.tgme_widget_message_text');
                const text = textEl ? textEl.innerText : '';

                let mediaUrl = null, mediaType = null;

                // 1) Video element – most reliable
                const videoTag = el.querySelector('video');
                if (videoTag && videoTag.src && !videoTag.src.startsWith('blob:')) {
                    mediaUrl = videoTag.src;
                    mediaType = 'video';
                }

                // 2) Video wrapper (alternative)
                if (!mediaUrl) {
                    const videoWrap = el.querySelector('.tgme_widget_message_video_wrap');
                    if (videoWrap) {
                        const vid = videoWrap.querySelector('video');
                        if (vid && vid.src && !vid.src.startsWith('blob:')) {
                            mediaUrl = vid.src;
                            mediaType = 'video';
                        } else {
                            // fallback: maybe a background image (poster)
                            const style = videoWrap.getAttribute('style') || '';
                            const match = style.match(/url\\('(.*?)'\\)/);
                            if (match) { mediaUrl = match[1]; mediaType = 'video'; }
                        }
                    }
                }

                // 3) Photo wrap
                if (!mediaUrl) {
                    const photoWrap = el.querySelector('.tgme_widget_message_photo_wrap');
                    if (photoWrap) {
                        const style = photoWrap.getAttribute('style') || '';
                        const match = style.match(/url\\('(.*?)'\\)/);
                        if (match) { mediaUrl = match[1]; mediaType = 'photo'; }
                    }
                }

                // 4) Photo wrap inside a link (video with cover)
                if (!mediaUrl) {
                    const linkPhoto = el.querySelector('a.tgme_widget_message_photo_wrap');
                    if (linkPhoto) {
                        const videoInside = linkPhoto.querySelector('video');
                        if (videoInside && videoInside.src && !videoInside.src.startsWith('blob:')) {
                            mediaUrl = videoInside.src;
                            mediaType = 'video';
                        } else {
                            const style = linkPhoto.getAttribute('style') || '';
                            const match = style.match(/url\\('(.*?)'\\)/);
                            if (match) { mediaUrl = match[1]; mediaType = 'photo'; }
                        }
                    }
                }

                // 5) Document
                if (!mediaUrl) {
                    const docWrap = el.querySelector('a.tgme_widget_message_document_wrap');
                    if (docWrap) {
                        mediaUrl = 'https://t.me/' + channel + '/' + postId;
                        mediaType = 'document';
                    }
                }

                msgs.push({
                    id: postId,
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
                m["_channel"] = clean_name

            all_messages.extend(msgs)
            print(f"  ✅ {ch_name}: fetched {len(msgs)} new messages (after filter)")

        await browser.close()

    # ---- Update timestamp header ----
    now_jalali = jdatetime.datetime.now(IRAN_TZ)
    update_header = f"\n---\n📅 بروزرسانی: {now_jalali.strftime('%Y/%m/%d %H:%M')}\n---\n\n"

    # ---- Build new message entries ----
    new_entries_list = []
    new_ids_set = set()

    for msg in all_messages:
        ch = msg["_channel"]
        pid = msg["id"]
        new_ids_set.add((ch, pid))

        media_md = None
        media_type = msg.get("media_type")
        media_url = msg.get("media_url")

        if media_url and media_type in ("photo", "video"):
            media_md = download_media(media_url, ch, pid, media_type=media_type)
        elif media_url and media_type == "document":
            media_md = download_document(media_url, ch, pid)
            if not media_md:
                media_md = media_url  # fallback link

        # ---- Centered media & RTL caption ----
        header = f"## {ch} — post {pid}\n\n"
        media_html = ""
        if media_md:
            if media_type == "photo":
                media_html = f'<div align="center">\n  <img src="{media_md}" alt="Photo">\n</div>'
            elif media_type == "video":
                media_html = f'<div align="center">\n  <a href="{media_md}">🎬 Download video</a>\n</div>'
            elif media_type == "document":
                media_html = f'<div align="center">\n  <a href="{media_md}">📎 Download file</a>\n</div>'

        caption = msg.get("text", "")
        if not caption:
            if media_type == "photo": caption = "📷 Photo"
            elif media_type == "video": caption = "🎬 Video"
            elif media_type == "document": caption = "📎 Document"
        caption_div = f'<div dir="rtl">\n{caption}\n</div>' if caption else ""

        entry = header + media_html + "\n" + caption_div + "\n\n"
        new_entries_list.append(entry)

    new_entries_block = update_header + "".join(new_entries_list)

    # ---- If no new posts were fetched, show a notice ----
    if not new_entries_list:
        new_entries_block += '<div dir="rtl">\nهیچ پیام جدیدی در این بروزرسانی ارسال نشد.\n</div>\n\n'

    # ---- Load and deduplicate existing messages ----
    old_messages_block = ""
    if OUTPUT_FILE.exists():
        old_raw = OUTPUT_FILE.read_text(encoding="utf-8")
        extracted = extract_message_md(old_raw)
        if extracted is not None:
            old_messages_block = extracted
        else:
            lines = old_raw.split("\n")
            if lines and lines[0].startswith("# "):
                old_messages_block = "\n".join(lines[1:]).strip()
            else:
                old_messages_block = old_raw.strip()

    if old_messages_block.strip() and new_ids_set:
        old_messages_block = deduplicate_messages(old_messages_block, new_ids_set)

    # ---- Combine and handle size limit ----
    if new_entries_block or old_messages_block:
        trial_page = wrap_page(new_entries_block + old_messages_block,
                               next_rel=None, prev_rel=None)
        size = len(trial_page.encode("utf-8"))
        if size > 950 * 1024 and old_messages_block.strip():
            split_main_page(new_entries_block, old_messages_block)
        else:
            archives = get_existing_archives()
            prev_rel_main = None
            if archives:
                prev_rel_main = f"telegram/content/archive_{archives[0][0]}.md"
            main_page = wrap_page(new_entries_block + old_messages_block,
                                  next_rel=None,
                                  prev_rel=prev_rel_main)
            OUTPUT_FILE.write_text(main_page, encoding="utf-8")
            print("✅ Main page updated (no split needed).")
    else:
        if not OUTPUT_FILE.exists():
            OUTPUT_FILE.write_text(wrap_page("", None, None), encoding="utf-8")
            print("ℹ️ No messages yet, empty page created.")

    # ---- Update state ----
    for ch_name in channels:
        clean_name = ch_name.lstrip("@")
        ch_msgs = [m for m in all_messages if m["_channel"] == clean_name]
        if ch_msgs:
            max_id = max(m["id"] for m in ch_msgs)
            state[ch_name] = max(state.get(ch_name, 0), max_id)

    save_state(state)
    print("✅ State saved.")


if __name__ == "__main__":
    asyncio.run(main())
