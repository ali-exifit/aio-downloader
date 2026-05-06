# aio-downloader — All-in-One GitHub Actions Downloader

**[راهنمای فارسی (Persian)](#راهنمای-فارسی)**

> A collection of **GitHub Actions workflows** that let you download videos, images, and files from **YouTube**, **Instagram**, **X (Twitter)**, **any direct URL**, and now **archive public Telegram channels** — all from your browser, **without running any software on your own computer**.

## Features

| Workflow | What it does |
|---|---|
| **YouTube Downloader** | Downloads YouTube videos in your chosen resolution (including 4K) with optional FPS selection. Supports video-only and audio-only modes. Now also handles multiple URLs in a single run, each with its own arguments. |
| **Instagram Downloader** | Downloads **all media** from Instagram posts, reels, stories, highlights, and profiles – including mixed carousels. Handles both images and videos. |
| **X (Twitter) Downloader** | Downloads **all media** (images, videos) from X/Twitter posts and profiles. Requires login cookies. Uses `gallery-dl` under the hood. |
| **Direct Downloader** | Downloads **any file** from a direct URL using `aria2c` (16 parallel connections, ultra-fast). Great for large files. |
| **🆕 Telegram Channel Archiver** | Scrapes **public Telegram channels** every 15 minutes and saves all new messages, photos, and videos as a Markdown archive in your repo. No API key or bot needed — works with Playwright on any public channel. |
| **🆕 Telegram Auto-Cleaner** | Automatically deletes old Telegram media (images/videos) from your repo every 3 days to keep storage under control. Runs daily at 00:00 Tehran time. |

✅ **All downloads are automatically split into 99 MB parts, zipped, and uploaded back to your repository** – you can download them anytime from GitHub.
✅ **No server, no VPS, and no local installation required** – everything runs on GitHub's free infrastructure.
✅ **Cookies are stored securely** as GitHub Secrets – never exposed in logs or code.
✅ **Batch downloading** – paste up to 10+ Instagram or X links at once, separated by commas, spaces, or newlines.
✅ **Concurrent runs** – You can trigger multiple workflow runs at the same time (e.g., download multiple YouTube videos, an Instagram batch, an X batch, and multiple direct files – all in parallel). Each run is independent and won't interfere with the others.

## Requirements (Before You Start)

- A **GitHub account** (free)
- A **browser** (Chrome/Firefox/Edge) with the extension **"Get cookies.txt LOCALLY"** to export your login cookies (for YouTube, Instagram, X)
- (Optional) An **Instagram account** if you want to download private/story content
- An **X (Twitter) account** (required for the X downloader to work)
- For Telegram: **nothing extra** — the archiver works on any public channel without login or API keys

## How to Fork and Set Up

### Step 1: Fork the repository
Click the **"Fork"** button at the top-right of this page.

### Step 2: Enable GitHub Actions
1. Go to your forked repository → **Settings** → **Actions** → **General**
2. Under **"Actions permissions"** select **"Allow all actions and reusable workflows"**
3. Click **Save**

### Step 3: Grant Workflow Write Permissions (IMPORTANT!)
1. Still under **Settings** → **Actions** → **General**
2. Scroll down to **"Workflow permissions"**
3. Select **"Read and write permissions"** (Workflows need this to commit and push downloaded files back to your repository.)
4. Click **Save**

> ⚠️ If you skip this step, the workflow will fail when trying to upload the ZIP files.

## How to Add Cookies (For YouTube, Instagram & X)

> **Note:** YouTube and Instagram may require login cookies for certain content. X (Twitter) **REQUIRES** login cookies – otherwise the downloader will fail. **Telegram works without any cookies.**

### 1. Export Cookies from Your Browser
- Install the extension **"Get cookies.txt LOCALLY"** from the Chrome Web Store or Firefox Add-ons.
- Log into **youtube.com** (for the YouTube downloader), **instagram.com** (for the Instagram downloader), or **x.com** (for the X downloader) in your browser.
- Click the extension icon and choose **"Export"** (Netscape format).
- Save the `.txt` file somewhere safe.

### 2. Add Cookies as GitHub Secrets
1. In your forked repository, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Create a secret named **`YOUTUBE_COOKIES`** and paste the entire contents of your YouTube `cookies.txt` file.
4. Create another secret named **`INSTAGRAM_COOKIES`** and paste your Instagram `cookies.txt` contents.
5. Create a secret named **`X_COOKIES`** and paste your X (Twitter) `cookies.txt` contents.

> ⚠️ **Never commit your cookie files directly to the repository.** The workflow automatically reads them from the secrets and creates a temporary file during execution.

---

## 🆕 Telegram Channel Archiver — Full Guide

The Telegram Channel Archiver is a fully automated workflow that scrapes **public Telegram channels**, downloads all their messages, photos, and videos, and stores them as a Markdown archive in your repository. It runs **every 15 minutes** automatically and can also be triggered manually.

### What It Does (Step by Step)

1. **Reads your channel list** from the `telegram/channels.json` file in your repo.
2. **Launches a Chromium browser** (via Playwright) and visits `https://t.me/s/<channel>` for each channel.
3. **Scrolls down** to fetch all new messages since the last check. On the first run it scrolls 15 times; after that, up to 50 scrolls to catch up.
4. **Extracts** message text, UTC datetime, photos (via CSS background-url), and videos (via `<video>` tags).
5. **Downloads all media** (photos as `.jpg`, videos as `.mp4`) into the `telegram/content/` folder.
6. **Converts UTC times** to Iran/Tehran timezone and Jalali (Hijri-Shamsi) calendar dates.
7. **Sorts all messages** from all channels by time (newest first).
8. **Writes** everything into `telegram.md` at the root of your repo with Markdown formatting.
9. **Saves the last message ID** per channel in `telegram/last_ids.json` so the next run only fetches new content.
10. **Commits and pushes** the changes back to your repository with a 5-retry loop to handle push conflicts.

### What You Get

A beautiful, time-sorted Markdown file (`telegram.md`) at the root of your repo that looks like this:

```
# Telegram Channel Archive

## 1404/02/16 14:30 — channelname
![Photo](telegram/content/channelname_12345_1712345678.jpg)

> This is the message text that was posted

## 1404/02/16 14:15 — otherchannel
[🎬 Video](telegram/content/otherchannel_67890_1712345678.mp4)

> Another message text here
```

All dates are in **Jalali calendar** with **Tehran timezone**.

### How to Add or Remove Channels

The channel list is stored in `telegram/channels.json`. You can edit this file directly on GitHub:

1. Navigate to `telegram/channels.json` in your repository.
2. Click the **pencil icon** (✏️) to edit.
3. Add or remove channel usernames (with or without the `@` symbol).

**Example `channels.json`:**

```
[
  "@VahidOOnLine",
  "mwarmonitor",
  "@pm_afshaa",
  "@iaghapour",
  "@DEJradio",
  "mamlekate",
  "VahidOnline",
  "@kianmeli1"
]
```

> **⚠️ Important:** Only add **public** channels. Private channels or groups will not work. Usernames can be with or without the `@` prefix — both work.

4. Click **"Commit changes"** at the bottom of the page.

The next automatic run (within 15 minutes) will pick up your new channels.

### How to Trigger the Archiver Manually

1. Go to **Actions** → Select **"telegram-fetcher-auto"**
2. Click the **"Run workflow"** button
3. Leave the branch as `main` and click **"Run workflow"**
4. The archiver will scrape all channels and update `telegram.md`

### How the Archiver Knows What's New

- The file `telegram/last_ids.json` stores the **highest message ID** seen for each channel.
- On each run, the script only fetches messages with an ID **greater than** the stored ID.
- This means **no duplicate messages** and **incremental updates**.
- The very first run fetches the last 15 scrolls of history; subsequent runs go deeper (up to 50 scrolls).

### Viewing Your Archive

Simply open `telegram.md` in your repository. GitHub renders Markdown natively, so you'll see:
- Formatted text with blockquoted messages
- Embedded images (photos from channels)
- Video links (clickable to view/download)

---

## 🆕 Telegram Auto-Cleaner — Full Guide

Telegram media files (photos and videos) can accumulate quickly and fill up your repository storage. The **Telegram Auto-Cleaner** solves this automatically.

### What It Does

1. **Runs every day at 20:30 UTC** (which is **00:00 Tehran time**).
2. **Checks** when the last clean happened (stored in `telegram/last_clean_date.txt`).
3. **If 3 days have passed** since the last clean, it:
   - Deletes the entire `telegram/content/` folder (all downloaded media).
   - Deletes the `telegram.md` archive file.
   - Updates the clean date to today (Jalali calendar).
4. **If less than 3 days**: does nothing (skips).
5. **Commits and pushes** any deletions to your repository.

### Why Every 3 Days?

This gives you a **3-day window** to view and manually save any important media before it's automatically cleaned. The 3-day cycle keeps your repository storage well under the 5 GB GitHub limit while still giving you time to review content.

### How to Trigger the Cleaner Manually

1. Go to **Actions** → Select **"telegram-cleaner-auto"**
2. Click the **"Run workflow"** button
3. Click **"Run workflow"**

> ⚠️ **Warning:** Running the cleaner manually will **immediately** check if 3 days have passed. If so, it will delete ALL Telegram media and the archive file. Only run manually if you've already saved what you need.

### What Gets Deleted vs What Stays

| Deleted | Stays |
|---|---|
| `telegram/content/` folder (all photos & videos) | `telegram/channels.json` (your channel list) |
| `telegram.md` (the archive file) | `telegram/last_ids.json` (message tracking) |
| | `telegram/last_clean_date.txt` (clean date tracker) |

**Important:** After cleaning, the next archiver run will start fresh — it will re-scrape channels from the last known message ID, so `telegram.md` will be recreated with all new messages since the last fetch.

### Customizing the Clean Cycle

If you want a different interval (e.g., every 7 days instead of 3), edit the workflow file:

1. Go to `.github/workflows/telegram-cleaner-auto.yml`
2. Find this line in the Python code:

```
next_clean = last_date + jdatetime.timedelta(days=3)
```

3. Change `3` to your desired number of days (e.g., `7` for weekly cleaning).
4. Commit the change.

You can also change the schedule by editing the `cron` line at the top of the file:

```
on:
  schedule:
    - cron: "30 20 * * *"   # 20:30 UTC = 00:00 Tehran
```

Use [crontab.guru](https://crontab.guru) to generate a new cron expression if needed.

---

## How to Use (Other Downloaders)

### YouTube Downloader
1. Go to your forked repository → **Actions** → Select **"youtube-downloader"**
2. Click the **"Run workflow"** button
3. In the input box, type one or more entries, each on a new line or separated by commas. Each entry is a URL followed by `v` or `a`, resolution/bitrate, and optional FPS.

**Examples:**

```
https://www.youtube.com/watch?v=VIDEO_ID v max
https://www.youtube.com/watch?v=VIDEO_ID v 1080 60
https://www.youtube.com/watch?v=VIDEO_ID a max
https://www.youtube.com/watch?v=VIDEO_ID v 4k, https://www.youtube.com/watch?v=VIDEO_ID a 128
```

- `v` = video, `a` = audio
- Resolution: `max`, `min`, `1080`, `2k`, `4k`, etc.
- FPS: optional, e.g., `60`, `30`
- If you omit `v/a`, it defaults to **video max quality**
4. Click **"Run workflow"**
5. When the workflow finishes, the output will be in the **`youtube/`** folder of your repository.

### Instagram Downloader
1. Go to **Actions** → Select **"instagram-downloader"**
2. Click **"Run workflow"**
3. In the input box, paste your Instagram links – **separated by commas, spaces, or newlines**

**Example:**

```
https://www.instagram.com/p/DX2y7oLDFOb/, https://www.instagram.com/reel/DVRXhn0gjL3/, https://www.instagram.com/p/DX6US4uCNGb/
```

4. Click **"Run workflow"**
5. When finished, the output ZIP will appear in the **`instagram/`** folder of your repository.

> **Tip:** You can paste up to 10+ links at once – the downloader processes them all and bundles them into a single ZIP file.

### X (Twitter) Downloader
1. Go to **Actions** → Select **"x-downloader"**
2. Click **"Run workflow"**
3. In the input box, paste your X (Twitter) links – **separated by commas, spaces, or newlines**

**Example:**

```
https://x.com/username/status/123456789, https://x.com/otheruser/status/987654321
```

> ⚠️ **You MUST add the `X_COOKIES` secret for this workflow to work.** See "How to Add Cookies" above.

4. Click **"Run workflow"**
5. When finished, the output ZIP will appear in the **`x/`** folder of your repository.

### Direct Downloader
1. Go to **Actions** → Select **"direct-downloader"**
2. Click **"Run workflow"**
3. Paste one or more direct download URLs (e.g., `.zip`, `.mp4`, `.apk`, `.pdf`), separated by commas, spaces, or newlines.

**Example:**

```
https://example.com/path/to/large-file.zip, https://example.com/another-file.mp4
```

4. Click **"Run workflow"**
5. The files will be downloaded with 16 parallel connections and uploaded to the **`direct/`** folder of your repository, split into 99 MB parts if needed.

---

## Output Folder Structure
``
your-repository/
├── youtube/
│   └── Video Title.mp4.zip  (YouTube downloads, split into parts if > 99 MB)
├── instagram/
│   └── instagram-contents-YYYYMMDD_HHMMSS.zip  (All Instagram content bundled together)
├── x/
│   └── x-contents-XXXXXXXX.zip  (X/Twitter downloads, flattened and zipped)
├── direct/
│   └── filename.zip  (Direct downloads, split into parts if > 99 MB)
├── telegram/
│   ├── channels.json  (Your list of channels to archive)
│   ├── last_ids.json  (Last message ID per channel — do not edit)
│   ├── last_clean_date.txt  (Date of last media cleanup)
│   └── content/  (Downloaded photos and videos from Telegram)
├── telegram.md  (The archive: all messages sorted by time, with inline media)
``
### Inside the Instagram / X ZIPs
When you open the Instagram or X ZIP, you'll see:
``
instagram-content/  (or x_downloads/ for X)
├── instagram_moruhiko_388851...jpg
├── instagram_moruhiko_388851...jpg
├── instagram_israelinpersian_...webp
├── instagram_meme.azaad_...mp4
└── ...
``
All files are flattened into a single folder for easy browsing. Filenames are prefixed with the uploader's username to avoid collisions.

## Telegram Workflows Summary

| Workflow | Schedule | What It Does |
|---|---|---|
| **telegram-fetcher-auto** | Every 15 minutes (`*/15 * * * *`) | Scrapes all channels in `channels.json`, downloads new media, updates `telegram.md` |
| **telegram-cleaner-auto** | Daily at 00:00 Tehran (`30 20 * * *`) | Deletes `telegram/content/` and `telegram.md` every 3 days to free up storage |

> Both workflows can also be triggered manually from the **Actions** tab at any time.

## ⏱️ Limitations

- **GitHub Free Tier** allows up to **6 hours per job** (public repos get **unlimited minutes**).
- Files larger than **99 MB** are automatically split into multi-part ZIP archives (`.z01`, `.z02`, ...). You need a tool like **7-Zip** or **WinRAR** to extract them.
- For very large Instagram or X batches, consider splitting them into smaller groups to avoid hitting GitHub's storage limits.
- **X (Twitter) downloader requires cookies** – it will not work without the `X_COOKIES` secret.
- **Telegram archiver** only works with **public** channels. Private channels, groups, or channels requiring login are not supported.
- Telegram media files can fill up storage quickly. The auto-cleaner runs every 3 days; adjust the interval in the workflow file if needed.

## Managing Repository Storage (5 GB Limit)

GitHub repositories have a **5 GB soft limit** (and a hard limit of 100 GB, but it's best to stay under 5 GB for performance). If you download frequently, your `youtube/`, `instagram/`, `x/`, `direct/`, and `telegram/content/` folders can fill up quickly. To avoid issues, clean out old files regularly.

### How to Delete Files or Folders via GitHub Web Interface

#### Delete a Single File
1. Navigate to the file inside your repository (e.g., `youtube/some-video.zip`).
2. Click the **three dots (`...`)** in the top-right corner of the file view.
3. Select **"Delete file"**.
4. At the bottom of the page, click **"Commit changes"** (add a commit message if you like) and confirm.

#### Delete an Entire Folder
- First, delete all files inside the folder using the single file deletion steps above.
- Once the folder is empty, navigate to its parent directory.
- Click the **three dots (`...`)** next to the folder name.
- Select **"Delete directory"**.
- Scroll down and click **"Commit changes"**.

> **Tip:** Check your repository size regularly in **Settings** → **Repository** → **Repository size**. If it approaches 5 GB, delete older ZIP files or clear out entire folders to stay within limits.

## License

MIT License

Copyright (c) 2025 ProAlit

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

# راهنمای فارسی

## aio-downloader — دانلودر همهکاره با GitHub Actions

> مجموعهای از **گردشکارهای GitHub Actions** که به شما امکان میدهند ویدیوها، تصاویر و فایلها را از **یوتیوب**، **اینستاگرام**، **X (توییتر)**، **هر لینک مستقیم**، و حالا **آرشیو کانال‌های عمومی تلگرام** — مستقیماً از مرورگر خود و **بدون اجرای هیچ نرم افزاری روی کامپیوترتان** دانلود کنید.

## ویژگیها

| گردشکار | کاربرد |
|---|---|
| **دانلودر یوتیوب** | دانلود ویدیوهای یوتیوب با رزولوشن دلخواه (از جمله 4K) و انتخاب FPS. پشتیبانی از حالت فقط-ویدیو و فقط-صدا. همچنین میتوانید چندین URL را در یک اجرا با آرگومان‌های مجزا پردازش کنید. |
| **دانلودر اینستاگرام** | دانلود **تمام محتوا** از پستها، ریلزها، استوریها، هایلایتها و پروفایلهای اینستاگرام — شامل کاروسلهای ترکیبی (عکس + ویدیو). |
| **دانلودر X (توییتر)** | دانلود **تمام محتوا** (عکس، ویدیو) از پستها و پروفایلهای X/Twitter. نیاز به کوکی ورود دارد. از `gallery-dl` استفاده می‌کند. |
| **دانلودر مستقیم** | دانلود **هر فایلی** از یک لینک مستقیم با `aria2c` (16 اتصال موازی، بسیار سریع). مناسب برای فایلهای حجیم. |
| **🆕 آرشیو کانال تلگرام** | هر ۱۵ دقیقه **کانال‌های عمومی تلگرام** را اسکن کرده و تمام پیام‌ها، عکس‌ها و ویدیوهای جدید را به صورت آرشیو Markdown در مخزن شما ذخیره می‌کند. بدون نیاز به API یا ربات — با Playwright روی هر کانال عمومی کار می‌کند. |
| **🆕 پاک‌کننده خودکار تلگرام** | هر ۳ روز یکبار (ساعت ۰۰:۰۰ تهران) فایل‌های رسانه‌ای قدیمی تلگرام را از مخزن شما پاک می‌کند تا فضای ذخیره‌سازی کنترل شود. |

✅ **تمام دانلودها بهطور خودکار به قطعات ۹۹ مگابایتی تقسیم، فشرده و در مخزن شما آپلود میشوند** — هر زمان میتوانید آنها را از GitHub دانلود کنید.
✅ **بدون نیاز به سرور، VPS یا نصب نرم افزار** — همه چیز روی زیرساخت رایگان GitHub اجرا میشود.
✅ **کوکیها بهصورت امن در GitHub Secrets ذخیره میشوند** — هرگز در لاگها یا کد نمایش داده نمیشوند.
✅ **دانلود دستهجمعی** — تا ۱۰+ لینک اینستاگرام یا X را همزمان (با کاما، فاصله یا خط جدید جدا کنید) بچسبانید.
✅ **اجرای همزمان** — میتوانید چندین گردشکار را همزمان اجرا کنید (مثلاً چند ویدیو از یوتیوب، یک دسته از اینستاگرام، یک دسته از X و چند فایل مستقیم، همه موازی). هر اجرا مستقل است و تداخلی با بقیه ندارد.

## پیشنیازها (قبل از شروع)

- یک **حساب GitHub** (رایگان)
- یک **مرورگر** (Chrome/Firefox/Edge) با افزونه **"Get cookies.txt LOCALLY"** برای استخراج کوکیهای ورود
- (اختیاری) یک **حساب اینستاگرام** اگر میخواهید محتوای خصوصی/استوری دانلود کنید
- یک **حساب X (توییتر)** (برای استفاده از دانلودر X الزامی است)
- برای تلگرام: **هیچ چیز اضافی لازم نیست** — آرشیوکننده روی هر کانال عمومی بدون نیاز به ورود یا کلید API کار می‌کند

## نحوه فورک کردن و راهاندازی

### مرحله ۱: فورک کردن مخزن
روی دکمه **"Fork"** در بالای صفحه کلیک کنید.

### مرحله ۲: فعال کردن GitHub Actions
1. به مخزن فورکشده خود بروید → **Settings** → **Actions** → **General**
2. در بخش **"Actions permissions"** گزینه **"Allow all actions and reusable workflows"** را انتخاب کنید.
3. روی **Save** کلیک کنید.

### مرحله ۳: دادن دسترسی نوشتن به GitHub Actions (مهم!)
1. همچنان در **Settings** → **Actions** → **General** بمانید.
2. به بخش **"Workflow permissions"** بروید.
3. گزینه **"Read and write permissions"** را انتخاب کنید. (گردشکارها برای commit کردن و push کردن فایلهای دانلود شده به این دسترسی نیاز دارند.)
4. روی **Save** کلیک کنید.

> ⚠️ اگر این مرحله را انجام ندهید، گردشکار هنگام تلاش برای آپلود فایلهای ZIP شکست خواهد خورد.

## نحوه اضافه کردن کوکیها (برای یوتیوب، اینستاگرام و X)

> **توجه:** یوتیوب و اینستاگرام ممکن است برای برخی محتواها به کوکی نیاز داشته باشند. X (توییتر) **حتماً** به کوکی نیاز دارد – در غیر این صورت دانلودر کار نخواهد کرد. **تلگرام بدون هیچ کوکی کار می‌کند.**

### ۱. استخراج کوکیها از مرورگر
- افزونه **"Get cookies.txt LOCALLY"** را از فروشگاه Chrome یا Firefox نصب کنید.
- در مرورگر خود وارد **youtube.com** (برای یوتیوب)، **instagram.com** (برای اینستاگرام) یا **x.com** (برای X) شوید.
- روی آیکون افزونه کلیک کنید و **"Export"** (فرمت Netscape) را انتخاب کنید.
- فایل `.txt` را در جای امنی ذخیره کنید.

### ۲. اضافه کردن کوکیها به عنوان GitHub Secrets
1. در مخزن فورکشده، به **Settings** → **Secrets and variables** → **Actions** بروید.
2. روی **"New repository secret"** کلیک کنید.
3. یک secret با نام **`YOUTUBE_COOKIES`** بسازید و محتوای کامل فایل `cookies.txt` یوتیوب را در آن بچسبانید.
4. یک secret دیگر با نام **`INSTAGRAM_COOKIES`** بسازید و محتوای فایل `cookies.txt` اینستاگرام را در آن بچسبانید.
5. یک secret با نام **`X_COOKIES`** بسازید و محتوای فایل `cookies.txt` ایکس (توییتر) را در آن بچسبانید.

> ⚠️ **هرگز فایلهای کوکی را مستقیماً در مخزن commit نکنید.** گردشکار بهطور خودکار آنها را از secrets خوانده و یک فایل موقت در زمان اجرا ایجاد میکند.

---

## 🆕 آرشیو کانال تلگرام — راهنمای کامل

آرشیوکننده کانال تلگرام یک گردشکار کاملاً خودکار است که **کانال‌های عمومی تلگرام** را اسکن می‌کند، تمام پیام‌ها، عکس‌ها و ویدیوهای آنها را دانلود کرده و به صورت یک آرشیو Markdown در مخزن شما ذخیره می‌کند. این گردشکار **هر ۱۵ دقیقه** به‌طور خودکار اجرا می‌شود و همچنین می‌توانید آن را دستی اجرا کنید.

### این گردشکار چه کاری انجام می‌دهد (گام به گام)

1. **لیست کانال‌های شما** را از فایل `telegram/channels.json` در مخزن می‌خواند.
2. **یک مرورگر Chromium راه‌اندازی می‌کند** (از طریق Playwright) و به آدرس `https://t.me/s/<channel>` برای هر کانال می‌رود.
3. **صفحه را اسکرول می‌کند** تا تمام پیام‌های جدید از آخرین بررسی را دریافت کند. در اولین اجرا ۱۵ اسکرول انجام می‌دهد؛ در اجراهای بعدی تا ۵۰ اسکرول برای عقب‌ نماندن.
4. **استخراج می‌کند** متن پیام، زمان UTC، عکس‌ها (از طریق CSS background-url) و ویدیوها (از طریق تگ `<video>`).
5. **تمام رسانه‌ها را دانلود می‌کند** (عکس‌ها با فرمت `.jpg`، ویدیوها با فرمت `.mp4`) در پوشه `telegram/content/`.
6. **زمان‌های UTC را** به منطقه زمانی ایران/تهران و تقویم جلالی (هجری-شمسی) تبدیل می‌کند.
7. **تمام پیام‌ها** از تمام کانال‌ها را بر اساس زمان مرتب می‌کند (جدیدترین اول).
8. **همه چیز را** در فایل `telegram.md` در ریشه مخزن با قالب‌بندی Markdown می‌نویسد.
9. **آخرین شناسه پیام** را برای هر کانال در `telegram/last_ids.json` ذخیره می‌کند تا اجرای بعدی فقط محتوای جدید را دریافت کند.
10. **تغییرات را commit و push می‌کند** با یک حلقه ۵ بار تلاش مجدد برای مدیریت تداخل‌های push.

### آنچه دریافت می‌کنید

یک فایل Markdown زیبا و مرتب‌شده بر اساس زمان (`telegram.md`) در ریشه مخزن که شبیه این است:

```
# Telegram Channel Archive

## ۱۴۰۴/۰۲/۱۶ ۱۴:۳۰ — channelname
![Photo](telegram/content/channelname_12345_1712345678.jpg)

> این متن پیامی است که ارسال شده

## ۱۴۰۴/۰۲/۱۶ ۱۴:۱۵ — otherchannel
[🎬 Video](telegram/content/otherchannel_67890_1712345678.mp4)

> یک متن پیام دیگر اینجا
```

تمام تاریخ‌ها به **تقویم جلالی** با **منطقه زمانی تهران** هستند.

### نحوه اضافه یا حذف کانال‌ها

لیست کانال‌ها در فایل `telegram/channels.json` ذخیره می‌شود. می‌توانید این فایل را مستقیماً در GitHub ویرایش کنید:

1. به `telegram/channels.json` در مخزن خود بروید.
2. روی **آیکون مداد** (✏️) کلیک کنید تا ویرایش شود.
3. نام کاربری کانال‌ها را اضافه یا حذف کنید (با یا بدون علامت `@`).

**نمونه `channels.json`:**

```
[
  "@VahidOOnLine",
  "mwarmonitor",
  "@pm_afshaa",
  "@iaghapour",
  "@DEJradio",
  "mamlekate",
  "VahidOnline",
  "@kianmeli1"
]
```

> **⚠️ مهم:** فقط کانال‌های **عمومی** را اضافه کنید. کانال‌ها یا گروه‌های خصوصی کار نخواهند کرد. نام‌های کاربری می‌توانند با یا بدون `@` باشند — هر دو کار می‌کنند.

4. روی **"Commit changes"** در پایین صفحه کلیک کنید.

اجرای خودکار بعدی (ظرف ۱۵ دقیقه) کانال‌های جدید شما را دریافت خواهد کرد.

### نحوه اجرای دستی آرشیوکننده

1. به **Actions** بروید → **"telegram-fetcher-auto"** را انتخاب کنید.
2. روی دکمه **"Run workflow"** کلیک کنید.
3. برنچ را روی `main` بگذارید و روی **"Run workflow"** کلیک کنید.
4. آرشیوکننده تمام کانال‌ها را اسکن کرده و `telegram.md` را به‌روزرسانی می‌کند.

### آرشیوکننده از کجا می‌داند چه چیز جدید است

- فایل `telegram/last_ids.json` **بالاترین شناسه پیام** دیده‌شده برای هر کانال را ذخیره می‌کند.
- در هر اجرا، اسکریپت فقط پیام‌هایی با شناسه **بزرگتر از** شناسه ذخیره‌شده را دریافت می‌کند.
- این یعنی **بدون پیام تکراری** و **به‌روزرسانی تدریجی**.
- اولین اجرا ۱۵ اسکرول آخر تاریخچه را دریافت می‌کند؛ اجراهای بعدی عمیق‌تر می‌روند (تا ۵۰ اسکرول).

### مشاهده آرشیو خود

کافیست فایل `telegram.md` را در مخزن خود باز کنید. GitHub مارک‌داون را به صورت بومی نمایش می‌دهد، بنابراین خواهید دید:
- متن‌های قالب‌بندی‌شده با پیام‌های نقل‌قول
- تصاویر جای‌گذاری‌شده (عکس‌های کانال‌ها)
- لینک‌های ویدیو (قابل کلیک برای مشاهده/دانلود)

---

## 🆕 پاک‌کننده خودکار تلگرام — راهنمای کامل

فایل‌های رسانه‌ای تلگرام (عکس‌ها و ویدیوها) می‌توانند به سرعت جمع شده و فضای ذخیره‌سازی مخزن شما را پر کنند. **پاک‌کننده خودکار تلگرام** این مشکل را به صورت خودکار حل می‌کند.

### این گردشکار چه کاری انجام می‌دهد

1. **هر روز ساعت ۲۰:۳۰ UTC** (یعنی **ساعت ۰۰:۰۰ تهران**) اجرا می‌شود.
2. **بررسی می‌کند** که آخرین پاک‌سازی چه زمانی انجام شده (ذخیره‌شده در `telegram/last_clean_date.txt`).
3. **اگر ۳ روز از آخرین پاک‌سازی گذشته باشد**:
   - کل پوشه `telegram/content/` (تمام رسانه‌های دانلودشده) را حذف می‌کند.
   - فایل آرشیو `telegram.md` را حذف می‌کند.
   - تاریخ پاک‌سازی را به امروز (تقویم جلالی) به‌روزرسانی می‌کند.
4. **اگر کمتر از ۳ روز گذشته باشد**: هیچ کاری نمی‌کند (رد می‌شود).
5. **حذف‌ها را commit و push می‌کند** به مخزن شما.

### چرا هر ۳ روز؟

این به شما یک **پنجره ۳ روزه** می‌دهد تا رسانه‌های مهم را قبل از پاک‌سازی خودکار مشاهده و به صورت دستی ذخیره کنید. چرخه ۳ روزه فضای ذخیره‌سازی مخزن شما را به خوبی زیر محدودیت ۵ گیگابایت GitHub نگه می‌دارد و در عین حال به شما زمان کافی برای بررسی محتوا می‌دهد.

### نحوه اجرای دستی پاک‌کننده

1. به **Actions** بروید → **"telegram-cleaner-auto"** را انتخاب کنید.
2. روی دکمه **"Run workflow"** کلیک کنید.
3. روی **"Run workflow"** کلیک کنید.

> ⚠️ **هشدار:** اجرای دستی پاک‌کننده **بلافاصله** بررسی می‌کند که آیا ۳ روز گذشته است یا خیر. اگر گذشته باشد، تمام رسانه‌های تلگرام و فایل آرشیو را حذف خواهد کرد. فقط زمانی دستی اجرا کنید که مطمئن باشید آنچه نیاز دارید را قبلاً ذخیره کرده‌اید.

### چه چیزهایی حذف می‌شوند و چه چیزهایی می‌مانند

| حذف می‌شود | می‌ماند |
|---|---|
| پوشه `telegram/content/` (تمام عکس‌ها و ویدیوها) | `telegram/channels.json` (لیست کانال‌های شما) |
| `telegram.md` (فایل آرشیو) | `telegram/last_ids.json` (ردیابی پیام‌ها) |
| | `telegram/last_clean_date.txt` (ردیاب تاریخ پاک‌سازی) |

**مهم:** پس از پاک‌سازی، اجرای بعدی آرشیوکننده از نو شروع می‌شود — کانال‌ها را از آخرین شناسه پیام شناخته‌شده دوباره اسکن می‌کند، بنابراین `telegram.md` با تمام پیام‌های جدید از آخرین دریافت بازسازی خواهد شد.

### شخصی‌سازی چرخه پاک‌سازی

اگر بازه زمانی متفاوتی می‌خواهید (مثلاً هر ۷ روز به جای ۳ روز)، فایل گردشکار را ویرایش کنید:

1. به `.github/workflows/telegram-cleaner-auto.yml` بروید.
2. این خط را در کد Python پیدا کنید:

```
next_clean = last_date + jdatetime.timedelta(days=3)
```

3. عدد `3` را به تعداد روزهای دلخواه خود تغییر دهید (مثلاً `7` برای پاک‌سازی هفتگی).
4. تغییر را commit کنید.

همچنین می‌توانید زمان‌بندی را با ویرایش خط `cron` در بالای فایل تغییر دهید:

```
on:
  schedule:
    - cron: "30 20 * * *"   # 20:30 UTC = 00:00 Tehran
```

از [crontab.guru](https://crontab.guru) برای تولید عبارت cron جدید در صورت نیاز استفاده کنید.

---

## نحوه استفاده (سایر دانلودرها)

### دانلودر یوتیوب
1. به مخزن فورکشده خود بروید → **Actions** → **"youtube-downloader"** را انتخاب کنید.
2. روی دکمه **"Run workflow"** کلیک کنید.
3. در کادر ورودی، یک یا چند درخواست را وارد کنید، هر کدام در یک خط جداگانه یا با کاما از هم جدا شوند. هر درخواست شامل یک URL و `v` یا `a`، رزولوشن/بیتریت و FPS اختیاری است.

**مثال‌ها:**

```
https://www.youtube.com/watch?v=VIDEO_ID v max
https://www.youtube.com/watch?v=VIDEO_ID v 1080 60
https://www.youtube.com/watch?v=VIDEO_ID a max
https://www.youtube.com/watch?v=VIDEO_ID v 4k, https://www.youtube.com/watch?v=VIDEO_ID a 128
```

- `v` = ویدیو، `a` = صدا
- رزولوشن: `max`، `min`، `1080`، `2k`، `4k` و غیره.
- FPS: اختیاری، مثلاً `60`، `30`
- اگر `v/a` را وارد نکنید، بهطور پیشفرض **حداکثر کیفیت ویدیو** انتخاب میشود.
4. روی **"Run workflow"** کلیک کنید.
5. پس از اتمام، خروجی در پوشه **`youtube/`** مخزن شما قرار میگیرد.

### دانلودر اینستاگرام
1. به **Actions** بروید → **"instagram-downloader"** را انتخاب کنید.
2. روی **"Run workflow"** کلیک کنید.
3. در کادر ورودی، لینکهای اینستاگرام خود را — **با کاما، فاصله یا خط جدید جدا کنید** — بچسبانید.

**مثال:**

```
https://www.instagram.com/p/DX2y7oLDFOb/, https://www.instagram.com/reel/DVRXhn0gjL3/, https://www.instagram.com/p/DX6US4uCNGb/
```

4. روی **"Run workflow"** کلیک کنید.
5. پس از اتمام، فایل ZIP خروجی در پوشه **`instagram/`** مخزن شما ظاهر میشود.

> **نکته:** میتوانید تا ۱۰+ لینک را همزمان بچسبانید — دانلودر همه را پردازش کرده و در یک فایل ZIP واحد بستهبندی میکند.

### دانلودر X (توییتر)
1. به **Actions** بروید → **"x-downloader"** را انتخاب کنید.
2. روی **"Run workflow"** کلیک کنید.
3. در کادر ورودی، لینکهای X (توییتر) خود را — **با کاما، فاصله یا خط جدید جدا کنید** — بچسبانید.

**مثال:**

```
https://x.com/username/status/123456789, https://x.com/otheruser/status/987654321
```

> ⚠️ **حتماً باید secret با نام `X_COOKIES` را اضافه کرده باشید.** به بخش «نحوه اضافه کردن کوکیها» در بالا مراجعه کنید.

4. روی **"Run workflow"** کلیک کنید.
5. پس از اتمام، فایل ZIP خروجی در پوشه **`x/`** مخزن شما ظاهر میشود.

### دانلودر مستقیم
1. به **Actions** بروید → **"direct-downloader"** را انتخاب کنید.
2. روی **"Run workflow"** کلیک کنید.
3. یک یا چند لینک دانلود مستقیم را بچسبانید (مثلاً `.zip`، `.mp4`، `.apk`، `.pdf`)، که با کاما، فاصله یا خط جدید از هم جدا شده باشند.

**مثال:**

```
https://example.com/path/to/large-file.zip, https://example.com/another-file.mp4
```

4. روی **"Run workflow"** کلیک کنید.
5. فایلها با ۱۶ اتصال موازی دانلود و در پوشه **`direct/`** مخزن شما آپلود میشوند (در صورت نیاز به قطعات ۹۹ مگابایتی تقسیم میشوند).

## ساختار پوشه خروجی
``
your-repository/
├── youtube/
│   └── Video Title.mp4.zip  (دانلودهای یوتیوب، در صورت > 99MB به قطعات تقسیم میشوند)
├── instagram/
│   └── instagram-contents-YYYYMMDD_HHMMSS.zip  (تمام محتوای اینستاگرام در یک ZIP)
├── x/
│   └── x-contents-XXXXXXXX.zip  (دانلودهای X/Twitter، فشرده و یکپارچه)
├── direct/
│   └── filename.zip  (دانلودهای مستقیم، در صورت > 99MB به قطعات تقسیم میشوند)
├── telegram/
│   ├── channels.json  (لیست کانال‌های شما برای آرشیو)
│   ├── last_ids.json  (آخرین شناسه پیام هر کانال — ویرایش نکنید)
│   ├── last_clean_date.txt  (تاریخ آخرین پاک‌سازی رسانه‌ها)
│   └── content/  (عکس‌ها و ویدیوهای دانلودشده از تلگرام)
├── telegram.md  (آرشیو: تمام پیام‌ها مرتب‌شده بر اساس زمان، با رسانه‌های inline)
``
### داخل ZIP اینستاگرام و X
هنگام باز کردن ZIP اینستاگرام یا X، خواهید دید:
``
instagram-content/  (یا x_downloads/ برای X)
├── instagram_moruhiko_388851...jpg
├── instagram_moruhiko_388851...jpg
├── instagram_israelinpersian_...webp
├── instagram_meme.azaad_...mp4
└── ...
``
تمام فایلها برای مرور آسان در یک پوشه واحد قرار میگیرند. نام فایلها با نام کاربری آپلودکننده پیشوندگذاری شده تا از تداخل جلوگیری شود.

## خلاصه گردشکارهای تلگرام

| گردشکار | زمان‌بندی | کاری که انجام می‌دهد |
|---|---|---|
| **telegram-fetcher-auto** | هر ۱۵ دقیقه (`*/15 * * * *`) | تمام کانال‌های موجود در `channels.json` را اسکن کرده، رسانه‌های جدید را دانلود و `telegram.md` را به‌روز می‌کند |
| **telegram-cleaner-auto** | روزانه ساعت ۰۰:۰۰ تهران (`30 20 * * *`) | هر ۳ روز یکبار `telegram/content/` و `telegram.md` را برای آزادسازی فضا حذف می‌کند |

> هر دو گردشکار را می‌توانید هر زمان از تب **Actions** به صورت دستی اجرا کنید.

## ⏱️ محدودیتها

- **طرح رایگان GitHub** تا **۶ ساعت برای هر کار (job)** اجازه میدهد (مخازن عمومی **دقیقه نامحدود** دارند).
- فایلهای بزرگتر از **۹۹ مگابایت** بهطور خودکار به آرشیوهای ZIP چندبخشی (`.z01`, `.z02`, ...) تقسیم میشوند. برای استخراج به نرم افزاری مانند **7-Zip** یا **WinRAR** نیاز دارید.
- برای دستههای بسیار بزرگ اینستاگرام یا X، آنها را به گروههای کوچکتر تقسیم کنید تا از محدودیتهای ذخیرهسازی GitHub فراتر نروید.
- **دانلودر X (توییتر) حتماً به کوکی نیاز دارد** – بدون `X_COOKIES` کار نخواهد کرد.
- **آرشیوکننده تلگرام** فقط با کانال‌های **عمومی** کار می‌کند. کانال‌های خصوصی، گروه‌ها یا کانال‌هایی که نیاز به ورود دارند پشتیبانی نمی‌شوند.
- فایل‌های رسانه‌ای تلگرام می‌توانند به سرعت فضا را پر کنند. پاک‌کننده خودکار هر ۳ روز اجرا می‌شود؛ در صورت نیاز بازه زمانی را در فایل گردشکار تنظیم کنید.

## مدیریت فضای ذخیرهسازی مخزن (محدودیت ۵ گیگابایت)

مخازن GitHub دارای **محدودیت نرم ۵ گیگابایت** هستند (حد سخت ۱۰۰ گیگابایت، اما بهتر است زیر ۵ گیگابایت بمانید). اگر زیاد دانلود کنید، پوشههای `youtube/`، `instagram/`، `x/`، `direct/` و `telegram/content/` به سرعت پر میشوند. برای جلوگیری از مشکل، فایلهای قدیمی را به طور منظم پاک کنید.

### نحوه حذف فایلها یا پوشهها از طریق رابط وب GitHub

#### حذف یک فایل
1. به فایل مورد نظر در مخزن خود بروید (مثلاً `youtube/some-video.zip`).
2. روی **سه نقطه (`...`)** در بالای صفحه کلیک کنید.
3. گزینه **"Delete file"** را انتخاب کنید.
4. در پایین صفحه، روی **"Commit changes"** کلیک کنید (در صورت تمایل یک پیام commit بنویسید) و تأیید کنید.

#### حذف یک پوشه کامل
- ابتدا تمام فایلهای داخل پوشه را با استفاده از مراحل حذف تکی بالا پاک کنید.
- وقتی پوشه خالی شد، به مسیر بالادست آن بروید.
- روی **سه نقطه (`...`)** کنار نام پوشه کلیک کنید.
- گزینه **"Delete directory"** را انتخاب کنید.
- به پایین صفحه بروید و روی **"Commit changes"** کلیک کنید.

> **نکته:** حجم مخزن خود را به طور مرتب در **Settings** → **Repository** → **Repository size** بررسی کنید. اگر به ۵ گیگابایت نزدیک شد، فایلهای ZIP قدیمی را پاک کنید یا کل پوشهها را خالی کنید.

## مجوز (License)

MIT License

کپی رابت (c) 2025 ProAlit

بدینوسیله به هر شخصی که یک کپی از این نرم افزار و فایلهای مستندات همراه آن («نرم افزار») را دریافت میکند، بهطور رایگان و بدون محدودیت اجازه داده میشود که از نرم افزار استفاده کند، آن را کپی، ویرایش، ادغام، منتشر، توزیع، زیرمجوز دهد و / یا بفروشد، و به افرادی که نرم افزار به آنها ارائه میشود اجازه انجام آن را بدهد، مشروط بر رعایت شرایط زیر:

اعلان کپی رابت فوق و این اعلان مجوز باید در تمام کپیها یا بخشهای عمده نرم افزار گنجانده شود.

نرم افزار «همانگونه که هست» ارائه میشود، بدون هیچگونه ضمانتی، صریح یا ضمنی، شامل اما نه محدود به ضمانتهای تجاری بودن، تناسب برای یک هدف خاص و عدم نقض حقوق. در هیچ صورت نویسندگان یا دارندگان کپی رابت در قبال هرگونه ادعا، خسارت یا مسئولیت دیگری که از استفاده یا در ارتباط با نرم افزار ناشی شود، مسئول نخواهند بود.

## ⭐ اگر این پروژه را دوست دارید لطفاً به مخزن **ستاره** ⭐ بدهید — این کار به دیگران کمک میکند آن را پیدا کنند!

## مشکلات و مشارکتها
باگی پیدا کردید؟ پیشنهادی دارید؟ [یک issue باز کنید](https://github.com/ProAlit/aio-downloader/issues) — بازخورد همیشه خوش آمد است!
