# aio-downloader — All-in-One GitHub Actions Downloader

**[راهنمای فارسی (Persian)](#راهنمای-فارسی)**

> A collection of **GitHub Actions workflows** that let you download videos, images, and files from **YouTube**, **Instagram**, **X (Twitter)**, **any direct URL**, **archive public Telegram channels**, and now **capture any website as a PDF** — all from your browser, **without running any software on your own computer**.

## Features

| Workflow | What it does |
|---|---|
| **YouTube Downloader** | Downloads YouTube videos in your chosen resolution (including 4K) with optional FPS selection. Supports video-only and audio-only modes. Handles multiple URLs in a single run, each with its own arguments. |
| **Instagram Downloader** | Downloads **all media** from Instagram posts, reels, stories, highlights, and profiles – including mixed carousels. Handles both images and videos. |
| **X (Twitter) Downloader** | Downloads **all media** (images, videos) from X/Twitter posts and profiles. Requires login cookies. Uses `gallery-dl` under the hood. |
| **Direct Downloader** | Downloads **any file** from a direct URL using `aria2c` (16 parallel connections, ultra-fast). Great for large files. |
| **Telegram Channel Archiver** | Scrapes **public Telegram channels** every 15 minutes (cron) or on manual trigger – saves all new messages, photos, and videos as a Markdown archive in your repo. No API key or bot needed — works with Playwright on any public channel. |
| **🆕 Website Capture** | **Capture any website as a PDF** — visits the main page, follows up to 20 internal links, captures every page as A4 PDF, and merges everything into one polished document. Uses Playwright + Chromium behind the scenes. Perfect for archiving articles, documentation, or entire site sections. |
| **AIO Cleaner (All-in-One Cleaner)** | **One manual workflow to clean up storage for all platforms.** You choose exactly what to delete: Telegram media, YouTube files, X (Twitter) files, Instagram files, Website captures, or **all at once**. No more juggling separate cleaners! |

✅ **All downloads are automatically split into 99 MB parts, zipped, and uploaded back to your repository** – you can download them anytime from GitHub.
✅ **No server, no VPS, and no local installation required** – everything runs on GitHub's free infrastructure.
✅ **Cookies are stored securely** as GitHub Secrets – never exposed in logs or code.
✅ **Batch downloading** – paste up to 10+ Instagram or X links at once, separated by commas, spaces, or newlines.
✅ **Concurrent runs** – You can trigger multiple workflow runs at the same time (e.g., download multiple YouTube videos, an Instagram batch, an X batch, capture a website, and multiple direct files – all in parallel). Each run is independent and won't interfere with the others.

---

## Requirements (Before You Start)

- A **GitHub account** (free)
- A **browser** (Chrome/Firefox/Edge) with the extension **"Get cookies.txt LOCALLY"** to export your login cookies (for YouTube, Instagram, X)
- (Optional) An **Instagram account** if you want to download private/story content
- An **X (Twitter) account** (required for the X downloader to work)
- For Telegram: **nothing extra** — the archiver works on any public channel without login or API keys
- For Website Capture: **nothing extra** — works on any public website without login or API keys

---

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

---

## How to Add Cookies (For YouTube, Instagram & X)

> **Note:** YouTube and Instagram may require login cookies for certain content. X (Twitter) **REQUIRES** login cookies – otherwise the downloader will fail. **Telegram and Website Capture work without any cookies.**

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

## 🆕 Website Capture — Full Guide

The Website Capture workflow turns **any public website** into a single, polished PDF document that's saved directly in your repository. It uses **Playwright** with a headless **Chromium** browser to render pages exactly like a real user would see them — including JavaScript, CSS, images, and dynamic content.

It's perfect for:
- Archiving news articles, blog posts, or documentation for offline reading
- Saving entire site sections as a single PDF reference
- Creating printable copies of web content
- Preserving pages that may change or disappear later

### What It Does (Step by Step)

1. **You provide a URL** — any public website address (e.g., `https://example.com/article`).
2. **Launches Chromium** via Playwright and visits the main URL.
3. **Captures the main page** as an A4 PDF with print backgrounds enabled, proper margins, and full scroll-down loading.
4. **Extracts all internal links** (up to 20 unique links from the same domain) from the main page.
5. **Visits each linked page** and captures it as a PDF too.
6. **Merges all PDFs** into a single document using `pdf-lib` — the main page first, then all linked pages in order.
7. **Saves the merged PDF** to the `website/` folder with a descriptive filename: `hostname-random5chars.pdf`.
8. **Commits and pushes** the PDF to your repository with a 5‑retry loop for push conflicts.

### What You Get

A single PDF file in the `website/` folder, named like:

```
website/example-com-xkjsd.pdf
```

The PDF contains:
- **Page 1**: The main URL you entered
- **Pages 2+**: Up to 20 internal pages linked from the main page

All content is rendered with full styling, images, and background graphics — it looks exactly like the live website.

### How to Trigger the Capture

1. Go to **Actions** → select **"website-capture"**
2. Click the **"Run workflow"** button
3. Enter the full URL of the website you want to capture:

**Examples:**

```
https://example.com/article/my-post
https://developer.mozilla.org/en-US/docs/Web/JavaScript
https://github.com/ProAlit/aio-downloader
```

4. Click **"Run workflow"**
5. Within 5–10 minutes (depending on the site), the PDF appears in the **`website/`** folder of your repository.

### What Types of Pages Work Best

| Good for | Not ideal for |
|---|---|
| Blog posts and articles | Single-page apps with infinite scroll |
| Documentation sites | Pages behind login walls |
| News articles | Sites that aggressively block bots |
| Product pages | Very large pages (100+ links) |
| GitHub READMEs / repos | Pages with heavy CAPTCHA |

### Limitations

- **Up to 20 internal links** are followed. If the main page has more internal links, only the first 20 are captured.
- **Only same-domain links** are followed. External links (different websites) are skipped.
- **30‑minute timeout** per capture. Very large sites with many slow-loading pages may not finish.
- **JavaScript‑heavy sites** may not render perfectly (e.g., WebGL, complex animations).
- **Pages behind login** won't work — only public websites are supported.
- **No cookies needed!** Website Capture works without any authentication.

### Viewing Your PDF

1. Navigate to the `website/` folder in your repository.
2. Click the PDF file — GitHub renders PDFs natively in the browser.
3. You can also download the PDF by clicking the **"Download"** button.

### Tips for Best Results

- Use the **full URL** including `https://`.
- For sites with many pages, capture a **specific article or section** rather than the homepage.
- If a site blocks the bot, try capturing a simpler page first to test.
- The PDF filename includes a random 5‑letter suffix to prevent naming conflicts — rename it if you prefer something more descriptive.

---

## Storage Cleaner — Full Guide (The AIO Cleaner)

All downloads go into your repository. Over time, the `youtube/`, `instagram/`, `x/`, `website/`, and `telegram/` folders can fill up and eat into GitHub’s **5 GB storage limit**. Instead of deleting files one by one, you can now use the **AIO Cleaner** workflow to wipe any platform’s downloads in one go.

### What It Cleans

| Platform | What gets deleted |
|---|---|
| **Telegram** | The `telegram/content/` folder (all downloaded photos & videos) and the `telegram.md` archive file. Your channel list (`channels.json`) and message tracking (`last_ids.json`) are kept safe. |
| **YouTube** | The entire `youtube/` folder (all downloaded videos and split ZIP parts). |
| **Instagram** | The entire `instagram/` folder (all downloaded ZIP archives). |
| **X (Twitter)** | The entire `x/` folder (all downloaded media and split ZIP parts). |
| **Website** | The entire `website/` folder (all captured PDF files). |

> ⚠️ **Warning:** Cleaning is **permanent**. Once deleted, those files cannot be recovered from GitHub. Make sure you've saved any important media before running the cleaner.

### How to Run the AIO Cleaner

1. Go to **Actions** → select **"aio-cleaner"**
2. Click the **"Run workflow"** button
3. You will see **six checkboxes**:

   - ✅ **Clean ALL platforms** – check this to wipe everything at once.
   - ✅ **Clean Telegram** – delete Telegram media and archive.
   - ✅ **Clean Youtube** – delete all YouTube downloads.
   - ✅ **Clean X** – delete all X/Twitter downloads.
   - ✅ **Clean Instagram** – delete all Instagram downloads.
   - ✅ **Clean Website** – delete all captured website PDFs.

4. Choose what you want to clean. Examples:

   **Clean only Website captures:**
   - Uncheck all boxes EXCEPT ✅ **Clean Website**
   - Click **"Run workflow"**

   **Clean YouTube + Website together:**
   - Check ✅ **Clean Youtube** and ✅ **Clean Website**
   - Leave others unchecked
   - Click **"Run workflow"**

   **Clean everything (full reset):**
   - Check ✅ **Clean ALL platforms**
   - Click **"Run workflow"**

5. The cleaner runs quickly (usually under 30 seconds). It deletes the selected folders and commits the deletions automatically.

### Viewing Cleaner Results

After the workflow finishes:
- Go to **Actions** → click the completed **"aio-cleaner"** run
- Expand the **"Clean selected platforms"** step
- You'll see a log like:

```
 Deleted telegram/content/
 Deleted telegram.md
 Deleted youtube/ folder
 Deleted website/ folder
```

- The commit message will list what was cleaned.

### When Should You Clean?

- When your repository size approaches **5 GB** (check at **Settings → Repository → Repository size**)
- After you've downloaded and saved any important media locally
- Periodically as maintenance (e.g., once a week or once a month depending on usage)

> 💡 **Tip:** Telegram media accumulates fastest because the archiver runs automatically every 15 minutes. Cleaning Telegram every few days is recommended, while YouTube/Instagram/X/Website can be cleaned less often.

---

## Telegram Channel Archiver — Full Guide

The Telegram Channel Archiver scrapes **public Telegram channels**, downloads all their messages, photos, and videos, and stores them as a Markdown archive in your repository. It can run **automatically every 15 minutes** (via cron schedule) **or manually whenever you want**.

> **If the automatic cron doesn't work** (e.g., due to GitHub disabling scheduled workflows on inactive forks), **you can always trigger it manually** — manual runs are 100% reliable.

### What It Does (Step by Step)

1. **Reads your channel list** from `telegram/channels.json` in your repo.
2. **Launches a Chromium browser** (Playwright) and visits `https://t.me/s/<channel>` for each channel.
3. **Scrolls down** to fetch all new messages since the last check. First run: ~15 scrolls; later runs: up to 50 scrolls to catch up.
4. **Extracts** message text, UTC datetime, photos (CSS background‑url), and videos (`<video>` tags).
5. **Downloads all media** (photos as `.jpg`, videos as `.mp4`) into `telegram/content/`.
6. **Converts UTC times** to Iran/Tehran timezone and Jalali (Hijri‑Shamsi) calendar dates.
7. **Sorts all messages** from all channels by time (newest first).
8. **Writes** everything into `telegram.md` at the root of your repo with Markdown formatting.
9. **Saves the last message ID** per channel in `telegram/last_ids.json` so the next run only fetches new content.
10. **Commits and pushes** the changes with a 5‑retry loop for push conflicts.

### What You Get

A time‑sorted Markdown file (`telegram.md`), like:

```
# Telegram Channel Archive

## 1404/02/16 14:30 — channelname
![Photo](telegram/content/channelname_12345_1712345678.jpg)

> This is the message text

## 1404/02/16 14:15 — otherchannel
[🎬 Video](telegram/content/otherchannel_67890_1712345678.mp4)

> Another message
```

All dates are in the **Jalali calendar** with **Tehran timezone**.

### How to Add or Remove Channels

Edit `telegram/channels.json` directly on GitHub:

1. Go to `telegram/channels.json` → click the **pencil icon** (✏️).
2. Add or remove channel usernames (with or without `@`).

**Example:**

```
[
  "VahidOOnLine",
  "mwarmonitor",
  "pm_afshaa",
  "iaghapour",
  "DEJradio",
  "mamlekate",
  "VahidOnline",
  "kianmeli1",
  "IranIntlTV",
  "FoxNewsChannel",
  "Shin_Persian",
  "Iliaen",
  "CnnBrk", 
  "reutersworldchannel",
  "ManotoTV",
  "FarsiVOA",
  "DW_Farsi",
  "Persian_Trend_Official",
  "RadioFarda",
  "IranianMinds",
  "BBCPersian",
  "IranWire",
  "Hranews"
]
```

> ⚠️ Only **public** channels work. Private channels/groups are not supported.

3. Click **"Commit changes"**. The next run (automatic or manual) picks up your changes.

### How to Trigger the Archiver Manually

1. Go to **Actions** → select **"telegram-fetcher"**.
2. Click **"Run workflow"**.
3. Leave the branch as `main` and click **"Run workflow"**.
4. The archiver scrapes all channels and updates `telegram.md`.

### How It Tracks New Messages

- `telegram/last_ids.json` stores the highest message ID per channel.
- Only messages with an ID **greater than** the stored ID are fetched → no duplicates.
- First run gets ~15 scrolls; subsequent runs go deeper (50 scrolls).

### Viewing Your Archive

Open `telegram.md` in your repo. GitHub renders Markdown natively with formatted text, embedded images, and clickable video links.

---

## How to Use (Other Downloaders)

### YouTube Downloader
1. Go to **Actions** → select **"youtube-downloader"**.
2. Click **"Run workflow"**.
3. Enter one or more entries (newline or comma‑separated). Each: URL, then `v` or `a`, resolution/bitrate, optional FPS.

**Examples:**

```
https://www.youtube.com/watch?v=VIDEO_ID v max
https://www.youtube.com/watch?v=VIDEO_ID v 1080 60
https://www.youtube.com/watch?v=VIDEO_ID a max
https://www.youtube.com/watch?v=VIDEO_ID v 4k, https://www.youtube.com/watch?v=VIDEO_ID a 128
```

- `v` = video, `a` = audio
- Resolution: `max`, `min`, `1080`, `2k`, `4k`, etc.
- FPS: optional (e.g., `60`, `30`)
- Default (if omitted): **video max quality**
4. Click **"Run workflow"** → output in the **`youtube/`** folder.

### Instagram Downloader
1. Go to **Actions** → select **"instagram-downloader"**.
2. Click **"Run workflow"**.
3. Paste Instagram links – separated by commas, spaces, or newlines.

**Example:**

```
https://www.instagram.com/p/DX2y7oLDFOb/, https://www.instagram.com/reel/DVRXhn0gjL3/, https://www.instagram.com/p/DX6US4uCNGb/
```

4. Click **"Run workflow"** → ZIP in the **`instagram/`** folder.

> **Tip:** Up to 10+ links at once — bundled into one ZIP.

### X (Twitter) Downloader
1. Go to **Actions** → select **"x-downloader"**.
2. Click **"Run workflow"**.
3. Paste X links – separated by commas, spaces, or newlines.

**Example:**

```
https://x.com/username/status/123456789, https://x.com/otheruser/status/987654321
```

> ⚠️ **`X_COOKIES` secret is mandatory.** See the cookies section above.

4. Click **"Run workflow"** → ZIP in the **`x/`** folder.

### Direct Downloader
1. Go to **Actions** → select **"direct-downloader"**.
2. Click **"Run workflow"**.
3. Paste direct download URLs – separated by commas, spaces, or newlines.

**Example:**

```
https://example.com/path/to/large-file.zip, https://example.com/another-file.mp4
```

4. Click **"Run workflow"** → files in the **`direct/`** folder (split into 99 MB parts if needed).

---

## Output Folder Structure
``
your-repository/
├── youtube/
│   └── Video Title.mp4.zip  (split if >99 MB)
├── instagram/
│   └── instagram-contents-YYYYMMDD_HHMMSS.zip
├── x/
│   └── x-contents-XXXXXXXX.zip
├── direct/
│   └── filename.zip  (split if >99 MB)
├── website/
│   └── hostname-random5chars.pdf  (captured website as merged PDF)
├── telegram/
│   ├── channels.json  (your channel list)
│   ├── last_ids.json  (message tracking – do not edit)
│   └── content/  (downloaded Telegram media)
├── telegram.md  (the archive: all messages sorted by time)
``
### Inside the Instagram / X ZIPs
``
instagram-content/  (or x_downloads/ for X)
├── instagram_moruhiko_388851...jpg
├── instagram_moruhiko_388851...jpg
├── instagram_israelinpersian_...webp
├── instagram_meme.azaad_...mp4
└── ...
``
All files are flattened into one folder; filenames are prefixed with the uploader's username to avoid collisions.

---

## Workflows Summary

| Workflow | Schedule | How to Use |
|---|---|---|
| **youtube-downloader** | Manual trigger | Paste URLs with optional quality arguments |
| **instagram-downloader** | Manual trigger | Paste Instagram URLs (up to 10+) |
| **x-downloader** | Manual trigger | Paste X/Twitter URLs (requires `X_COOKIES` secret) |
| **direct-downloader** | Manual trigger | Paste direct download URLs |
| **🆕 website-capture** | Manual trigger | Enter a single URL – captures site as merged PDF |
| **telegram-fetcher** | Every 15 min (cron) + Manual trigger | Configure `channels.json`, then run automatically or manually |
| **aio-cleaner** | **Manual trigger** | Check boxes to select what to clean (now includes Website), then run |

---

## ⏱️ Limitations

- **GitHub Free Tier** allows up to **6 hours per job** (public repos get **unlimited minutes**).
- Files larger than **99 MB** are automatically split into multi-part ZIP archives (`.z01`, `.z02`, ...). You need a tool like **7-Zip** or **WinRAR** to extract them.
- For very large Instagram or X batches, consider splitting them into smaller groups.
- **X (Twitter) downloader requires cookies** – it will not work without the `X_COOKIES` secret.
- **Telegram archiver only works with public channels**. Private channels, groups, or channels requiring login are not supported.
- **Website Capture** is limited to **public websites**. Pages behind login, CAPTCHA, or aggressive bot-blocking may fail. Up to **20 internal links** are followed; large sites with hundreds of pages won't be fully captured.
- Telegram media files can accumulate quickly. Use the **AIO Cleaner** regularly to free up space.
- Captured website PDFs can be large (several MB each). Clean the `website/` folder with the AIO Cleaner when you no longer need old captures.

---

## Managing Repository Storage (5 GB Limit)

GitHub repositories have a **5 GB soft limit** (and a hard limit of 100 GB, but it's best to stay under 5 GB for performance). If you download frequently, your `youtube/`, `instagram/`, `x/`, `direct/`, `website/`, and `telegram/content/` folders can fill up quickly.

### The Best Way: Use the AIO Cleaner

The easiest way to manage storage is the **aio-cleaner** workflow described above. It lets you wipe any platform's folder with one click — now including the `website/` folder for captured PDFs.

### Manual Deletion (If You Prefer)

#### Delete a Single File
1. Navigate to the file inside your repository (e.g., `youtube/some-video.zip`).
2. Click the **three dots (`...`)** in the top-right corner.
3. Select **"Delete file"**.
4. At the bottom of the page, click **"Commit changes"** and confirm.

#### Delete an Entire Folder
- First, delete all files inside the folder using the single file steps above.
- Once the folder is empty, navigate to its parent directory.
- Click the **three dots (`...`)** next to the folder name.
- Select **"Delete directory"**.
- Scroll down and click **"Commit changes"**.

> **Tip:** Check your repository size regularly in **Settings** → **Repository** → **Repository size**. If it approaches 5 GB, delete older ZIP files or use the **aio-cleaner** to clear entire folders at once.

---

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

> مجموعهای از **گردشکارهای GitHub Actions** که به شما امکان میدهند ویدیوها، تصاویر و فایلها را از **یوتیوب**، **اینستاگرام**، **X (توییتر)**، **هر لینک مستقیم**، **آرشیو کانال‌های عمومی تلگرام**، و حالا **ذخیره هر وبسایت به صورت PDF** — مستقیماً از مرورگر خود و **بدون اجرای هیچ نرم افزاری روی کامپیوترتان** دانلود کنید.

## ویژگیها

| گردشکار | کاربرد |
|---|---|
| **دانلودر یوتیوب** | دانلود ویدیوهای یوتیوب با رزولوشن دلخواه (تا 4K). پشتیبانی از چند URL در یک اجرا. |
| **دانلودر اینستاگرام** | دانلود تمام محتوا از پستها، ریلزها، استوریها و پروفایلها. |
| **دانلودر X (توییتر)** | دانلود عکس و ویدیو از توییتها و پروفایلها (نیاز به کوکی). |
| **دانلودر مستقیم** | دانلود هر فایل از لینک مستقیم با ۱۶ اتصال موازی و تقسیم فایلهای بزرگ. |
| **آرشیو کانال تلگرام** | اسکن خودکار (هر ۱۵ دقیقه) یا دستی کانالهای عمومی و ذخیره پیامها، عکسها و ویدیوها در یک فایل Markdown. بدون نیاز به API یا ربات. |
| **🆕 ضبط وبسایت (Website Capture)** | **هر وبسایت را به صورت PDF ذخیره کنید** — صفحه اصلی را بازدید کرده، تا ۲۰ لینک داخلی را دنبال کرده، هر صفحه را به صورت PDF با فرمت A4 ذخیره و همه را در یک فایل ادغام میکند. مناسب برای آرشیو مقالات، مستندات یا بخش‌های کامل سایت. |
| **پاککننده جامع (AIO Cleaner)** | **یک گردشکار دستی برای پاکسازی فضای ذخیرهسازی تمام پلتفرمها.** شما انتخاب میکنید چه چیزی حذف شود: محتوای تلگرام، یوتیوب، X، اینستاگرام، وبسایت، یا **همه با هم**. |

✅ تمام دانلودها بهطور خودکار به قطعات ۹۹ مگابایتی تقسیم، فشرده و در مخزن شما آپلود میشوند.
✅ بدون نیاز به سرور، VPS یا نصب نرم افزار.
✅ کوکیها بهصورت امن در GitHub Secrets ذخیره میشوند.
✅ دانلود دستهجمعی — تا ۱۰+ لینک اینستاگرام یا X همزمان.
✅ اجرای همزمان گردشکارها.

---

## پیشنیازها (قبل از شروع)

- یک **حساب GitHub** (رایگان)
- یک **مرورگر** (Chrome/Firefox/Edge) با افزونه **"Get cookies.txt LOCALLY"**
- (اختیاری) یک **حساب اینستاگرام** برای محتوای خصوصی/استوری
- یک **حساب X (توییتر)** (برای دانلودر X الزامی است)
- برای تلگرام: **هیچ چیز اضافی لازم نیست** — آرشیوکننده روی هر کانال عمومی بدون نیاز به ورود یا کلید API کار میکند
- برای ضبط وبسایت: **هیچ چیز اضافی لازم نیست** — روی هر وبسایت عمومی بدون نیاز به ورود یا کلید API کار میکند

---

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
3. گزینه **"Read and write permissions"** را انتخاب کنید.
4. روی **Save** کلیک کنید.

> ⚠️ اگر این مرحله را انجام ندهید، گردشکار هنگام تلاش برای آپلود فایلهای ZIP شکست خواهد خورد.

---

## نحوه اضافه کردن کوکیها (برای یوتیوب، اینستاگرام و X)

> **توجه:** یوتیوب و اینستاگرام ممکن است برای برخی محتواها به کوکی نیاز داشته باشند. X (توییتر) **حتماً** به کوکی نیاز دارد. **تلگرام و ضبط وبسایت بدون هیچ کوکی کار میکنند.**

### ۱. استخراج کوکیها از مرورگر
- افزونه **"Get cookies.txt LOCALLY"** را نصب کنید.
- در مرورگر خود وارد **youtube.com**، **instagram.com** یا **x.com** شوید.
- روی آیکون افزونه کلیک کنید و **"Export"** (فرمت Netscape) را انتخاب کنید.
- فایل `.txt` را ذخیره کنید.

### ۲. اضافه کردن کوکیها به عنوان GitHub Secrets
1. در مخزن فورکشده، به **Settings** → **Secrets and variables** → **Actions** بروید.
2. روی **"New repository secret"** کلیک کنید.
3. یک secret با نام **`YOUTUBE_COOKIES`** بسازید و محتوای فایل یوتیوب را بچسبانید.
4. یک secret با نام **`INSTAGRAM_COOKIES`** بسازید و محتوای فایل اینستاگرام را بچسبانید.
5. یک secret با نام **`X_COOKIES`** بسازید و محتوای فایل X را بچسبانید.

> ⚠️ **هرگز فایلهای کوکی را مستقیماً در مخزن commit نکنید.** گردشکار بهطور خودکار آنها را از secrets میخواند.

---

## 🆕 ضبط وبسایت (Website Capture) — راهنمای کامل

گردشکار ضبط وبسایت، **هر وبسایت عمومی** را به یک فایل PDF واحد و باکیفیت تبدیل کرده و مستقیماً در مخزن شما ذخیره میکند. این گردشکار از **Playwright** با مرورگر **Chromium** بدون رابط کاربری (headless) استفاده میکند تا صفحات را دقیقاً همانطور که یک کاربر واقعی میبیند نمایش دهد — شامل JavaScript، CSS، تصاویر و محتوای پویا.

موارد استفاده عالی:
- آرشیو مقالات خبری، پستهای وبلاگ یا مستندات برای مطالعه آفلاین
- ذخیره بخش‌های کامل یک سایت به عنوان یک فایل PDF مرجع
- ایجاد نسخه‌های قابل چاپ از محتوای وب
- حفظ صفحاتی که ممکن است در آینده تغییر کنند یا حذف شوند

### این گردشکار چه میکند (گام به گام)

1. **شما یک URL وارد میکنید** — هر آدرس وبسایت عمومی (مثلاً `https://example.com/article`).
2. **Chromium را راهاندازی میکند** و از URL اصلی بازدید میکند.
3. **صفحه اصلی را ضبط میکند** به صورت PDF با فرمت A4، با پس‌زمینه‌های چاپی فعال، حاشیه‌های مناسب و بارگذاری کامل با اسکرول.
4. **تمام لینک‌های داخلی را استخراج میکند** (تا ۲۰ لینک یکتا از همان دامنه) از صفحه اصلی.
5. **از هر صفحه لینک‌شده بازدید کرده** و آن را نیز به صورت PDF ضبط میکند.
6. **تمام PDFها را ادغام میکند** در یک فایل واحد با استفاده از `pdf-lib` — صفحه اصلی اول، سپس تمام صفحات لینک‌شده به ترتیب.
7. **فایل PDF ادغام‌شده را ذخیره میکند** در پوشه `website/` با یک نام توصیفی: `hostname-random5chars.pdf`.
8. **تغییرات را commit و push میکند** با یک حلقه ۵ بار تلاش مجدد.

### خروجی

یک فایل PDF در پوشه `website/` با نامی مشابه:

```
website/example-com-xkjsd.pdf
```

PDF شامل:
- **صفحه ۱**: URL اصلی که وارد کردید
- **صفحات ۲+**: تا ۲۰ صفحه داخلی که از صفحه اصلی لینک شده‌اند

تمام محتوا با استایل کامل، تصاویر و گرافیک پس‌زمینه نمایش داده میشود — دقیقاً شبیه وبسایت زنده.

### نحوه اجرای ضبط

1. به **Actions** بروید → **"website-capture"** را انتخاب کنید.
2. روی دکمه **"Run workflow"** کلیک کنید.
3. آدرس کامل وبسایتی که می‌خواهید ضبط کنید را وارد کنید:

**مثال‌ها:**

```
https://example.com/article/my-post
https://developer.mozilla.org/en-US/docs/Web/JavaScript
https://github.com/ProAlit/aio-downloader
```

4. روی **"Run workflow"** کلیک کنید.
5. ظرف ۵–۱۰ دقیقه (بسته به سایت)، PDF در پوشه **`website/`** مخزن شما ظاهر میشود.

### چه صفحاتی بهترین عملکرد را دارند

| مناسب برای | نامناسب برای |
|---|---|
| پست‌های وبلاگ و مقالات | برنامه‌های تک‌صفحه‌ای با اسکرول بی‌نهایت |
| سایت‌های مستندات | صفحات پشت دیوار ورود |
| مقالات خبری | سایت‌هایی که به شدت ربات‌ها را مسدود میکنند |
| صفحات محصول | صفحات بسیار بزرگ (۱۰۰+ لینک) |
| READMEهای GitHub | صفحات با CAPTCHA سنگین |

### محدودیت‌ها

- **حداکثر ۲۰ لینک داخلی** دنبال میشود. اگر صفحه اصلی لینک‌های داخلی بیشتری داشته باشد، فقط ۲۰ تای اول ضبط میشوند.
- **فقط لینک‌های همان دامنه** دنبال میشوند. لینک‌های خارجی (وبسایت‌های دیگر) نادیده گرفته میشوند.
- **مهلت ۳۰ دقیقه‌ای** برای هر ضبط. سایت‌های بسیار بزرگ با صفحات زیاد ممکن است کامل نشوند.
- **صفحات با JavaScript سنگین** ممکن است کامل نمایش داده نشوند.
- **صفحات پشت ورود** کار نمیکنند — فقط وبسایت‌های عمومی پشتیبانی میشوند.
- **بدون نیاز به کوکی!** ضبط وبسایت بدون هیچ احراز هویتی کار میکند.

### مشاهده PDF

1. به پوشه `website/` در مخزن خود بروید.
2. روی فایل PDF کلیک کنید — GitHub PDFها را به صورت بومی در مرورگر نمایش میدهد.
3. همچنین میتوانید PDF را با کلیک روی دکمه **"Download"** دانلود کنید.

### نکات برای بهترین نتیجه

- از **آدرس کامل** شامل `https://` استفاده کنید.
- برای سایت‌های با صفحات زیاد، یک **مقاله یا بخش خاص** را به جای صفحه اصلی ضبط کنید.
- اگر سایتی ربات را مسدود کرد، ابتدا یک صفحه ساده‌تر را برای آزمایش امتحان کنید.
- نام فایل PDF شامل یک پسوند تصادفی ۵ حرفی برای جلوگیری از تداخل نام‌ها است — در صورت تمایل میتوانید آن را تغییر نام دهید.

---

## پاککننده فضای ذخیرهسازی — راهنمای کامل (AIO Cleaner)

همه دانلودها در مخزن شما ذخیره میشوند. به مرور زمان، پوشه‌های `youtube/`، `instagram/`، `x/`، `website/` و `telegram/` میتوانند پر شده و فضای ذخیرهسازی **۵ گیگابایتی** GitHub را مصرف کنند. به جای حذف دستی فایلها، میتوانید از گردشکار **AIO Cleaner** برای پاکسازی هر پلتفرم با یک کلیک استفاده کنید.

### چه چیزهایی پاک میشوند

| پلتفرم | آنچه حذف میشود |
|---|---|
| **تلگرام** | پوشه `telegram/content/` (تمام عکسها و ویدیوهای دانلود شده) و فایل `telegram.md`. لیست کانالها (`channels.json`) و ردیاب پیامها (`last_ids.json`) دستنخورده میمانند. |
| **یوتیوب** | کل پوشه `youtube/` (تمام ویدیوهای دانلود شده). |
| **اینستاگرام** | کل پوشه `instagram/` (تمام فایلهای ZIP دانلود شده). |
| **X (توییتر)** | کل پوشه `x/` (تمام رسانههای دانلود شده). |
| **وبسایت** | کل پوشه `website/` (تمام فایل‌های PDF ضبط شده). |

> ⚠️ **هشدار:** پاکسازی **دائمی** است. پس از حذف، فایلها قابل بازیابی نیستند. قبل از اجرا مطمئن شوید که رسانههای مهم را ذخیره کردهاید.

### نحوه اجرای پاککننده جامع (AIO Cleaner)

1. به **Actions** بروید → **"aio-cleaner"** را انتخاب کنید.
2. روی دکمه **"Run workflow"** کلیک کنید.
3. شش گزینه (چکباکس) خواهید دید:

   - ✅ **Clean ALL platforms** — همه چیز را یکجا پاک میکند.
   - ✅ **Clean Telegram** — رسانهها و آرشیو تلگرام را حذف میکند.
   - ✅ **Clean Youtube** — همه دانلودهای یوتیوب را حذف میکند.
   - ✅ **Clean X** — همه دانلودهای X را حذف میکند.
   - ✅ **Clean Instagram** — همه دانلودهای اینستاگرام را حذف میکند.
   - ✅ **Clean Website** — همه PDFهای ضبط شده وبسایت را حذف میکند.

4. انتخاب کنید چه چیزی پاک شود. مثالها:

   **فقط وبسایت:**
   - فقط ✅ **Clean Website** را تیک بزنید.
   - روی **"Run workflow"** کلیک کنید.

   **یوتیوب + وبسایت با هم:**
   - ✅ **Clean Youtube** و ✅ **Clean Website** را تیک بزنید.
   - بقیه را بدون تیک بگذارید.
   - روی **"Run workflow"** کلیک کنید.

   **همه چیز (پاکسازی کامل):**
   - ✅ **Clean ALL platforms** را تیک بزنید.
   - روی **"Run workflow"** کلیک کنید.

5. پاککننده سریع اجرا میشود (معمولاً زیر ۳۰ ثانیه). پوشههای انتخاب شده را حذف و تغییرات را commit میکند.

### مشاهده نتایج پاکسازی

پس از اتمام:
- به **Actions** بروید → روی اجرای تکمیلشده **"aio-cleaner"** کلیک کنید.
- مرحله **"Clean selected platforms"** را باز کنید.
- گزارشی مشابه این خواهید دید:

```
 Deleted telegram/content/
 Deleted telegram.md
 Deleted youtube/ folder
 Deleted website/ folder
```

### چه زمانی پاکسازی کنیم؟

- وقتی حجم مخزن به **۵ گیگابایت** نزدیک میشود (بررسی در **Settings → Repository → Repository size**).
- پس از ذخیره رسانههای مهم روی کامپیوتر خود.
- بهعنوان نگهداری دورهای (مثلاً هفتگی یا ماهانه بسته به میزان استفاده).

> 💡 **نکته:** رسانههای تلگرام سریعترین رشد را دارند چون آرشیوکننده هر ۱۵ دقیقه اجرا میشود. پاکسازی تلگرام هر چند روز یکبار توصیه میشود، در حالی که یوتیوب/اینستاگرام/X/وبسایت را میتوان با فاصله بیشتری پاک کرد.

---

## آرشیو کانال تلگرام — راهنمای کامل

این گردشکار کانالهای عمومی تلگرام را اسکن کرده و پیامها، عکسها و ویدیوها را در فایل `telegram.md` ذخیره میکند. **میتواند خودکار (cron) یا دستی اجرا شود.**

> **اگر اجرای زمانبندیشده کار نکرد** (مثلاً به دلیل غیرفعال شدن زمانبندی توسط GitHub برای فورکهای غیرفعال)، **همیشه میتوانید آن را دستی اجرا کنید** — اجرای دستی کاملاً قابل اعتماد است.

### این گردشکار چه میکند (گام به گام)

1. خواندن لیست کانالها از `telegram/channels.json`.
2. راهاندازی مرورگر (Playwright) و بازدید از `https://t.me/s/<channel>`.
3. اسکرول برای دریافت پیامهای جدید (اولین اجرا: ۱۵ اسکرول، بعدیها تا ۵۰).
4. استخراج متن، زمان UTC، عکسها و ویدیوها.
5. دانلود رسانهها در `telegram/content/`.
6. تبدیل زمانها به منطقه زمانی تهران و تقویم جلالی.
7. مرتبسازی همه پیامها از جدید به قدیم.
8. نوشتن در `telegram.md` با قالب Markdown.
9. ذخیره آخرین شناسه پیام در `telegram/last_ids.json`.
10. Commit و push (با ۵ بار تلاش مجدد).

### خروجی

فایل `telegram.md` در ریشه مخزن:

```
# Telegram Channel Archive

## ۱۴۰۴/۰۲/۱۶ ۱۴:۳۰ — channelname
![Photo](telegram/content/channelname_12345_1712345678.jpg)

> متن پیام

## ۱۴۰۴/۰۲/۱۶ ۱۴:۱۵ — otherchannel
[🎬 Video](telegram/content/otherchannel_67890_1712345678.mp4)

> پیام دیگر
```

### اضافه/حذف کانال

فایل `telegram/channels.json` را ویرایش کنید (آیکون مداد ✏️).

**مثال:**

```
[
  "VahidOOnLine",
  "mwarmonitor",
  "pm_afshaa",
  "iaghapour",
  "DEJradio",
  "mamlekate",
  "VahidOnline",
  "kianmeli1",
  "IranIntlTV",
  "FoxNewsChannel",
  "Shin_Persian",
  "Iliaen",
  "CnnBrk", 
  "reutersworldchannel",
  "ManotoTV",
  "FarsiVOA",
  "DW_Farsi",
  "Persian_Trend_Official",
  "RadioFarda",
  "IranianMinds",
  "BBCPersian",
  "IranWire",
  "Hranews"
]
```

> ⚠️ فقط کانالهای **عمومی** پشتیبانی میشوند.

### اجرای دستی آرشیوکننده

1. **Actions** → **"telegram-fetcher"**
2. **"Run workflow"** → **"Run workflow"**
3. آرشیو بهروز میشود.

---

## نحوه استفاده از سایر دانلودرها

### دانلودر یوتیوب

**مثالها:**

```
https://www.youtube.com/watch?v=VIDEO_ID v max
https://www.youtube.com/watch?v=VIDEO_ID v 1080 60
https://www.youtube.com/watch?v=VIDEO_ID a max
https://www.youtube.com/watch?v=VIDEO_ID v 4k, https://www.youtube.com/watch?v=VIDEO_ID a 128
```

- `v` = ویدیو، `a` = صدا
- رزولوشن: `max`، `min`، `1080`، `2k`، `4k` و غیره
- FPS: اختیاری
- پیشفرض: **حداکثر کیفیت ویدیو**

### دانلودر اینستاگرام

**مثال:**

```
https://www.instagram.com/p/DX2y7oLDFOb/, https://www.instagram.com/reel/DVRXhn0gjL3/, https://www.instagram.com/p/DX6US4uCNGb/
```

### دانلودر X (توییتر)

**مثال:**

```
https://x.com/username/status/123456789, https://x.com/otheruser/status/987654321
```

> ⚠️ کوکی `X_COOKIES` الزامی است.

### دانلودر مستقیم

**مثال:**

```
https://example.com/path/to/large-file.zip, https://example.com/another-file.mp4
```

---

## ساختار پوشه خروجی
``
your-repository/
├── youtube/
│   └── Video Title.mp4.zip
├── instagram/
│   └── instagram-contents-YYYYMMDD_HHMMSS.zip
├── x/
│   └── x-contents-XXXXXXXX.zip
├── direct/
│   └── filename.zip
├── website/
│   └── hostname-random5chars.pdf
├── telegram/
│   ├── channels.json
│   ├── last_ids.json
│   └── content/
├── telegram.md
``
## خلاصه گردشکارها

| گردشکار | زمانبندی | نحوه استفاده |
|---|---|---|
| **youtube-downloader** | دستی | وارد کردن URL با آرگومانهای کیفیت |
| **instagram-downloader** | دستی | وارد کردن لینکهای اینستاگرام |
| **x-downloader** | دستی | وارد کردن لینکهای X (نیاز به کوکی) |
| **direct-downloader** | دستی | وارد کردن لینکهای دانلود مستقیم |
| **🆕 website-capture** | دستی | وارد کردن یک URL — ذخیره سایت به صورت PDF ادغام‌شده |
| **telegram-fetcher** | هر ۱۵ دقیقه (cron) + دستی | تنظیم `channels.json`، سپس اجرای خودکار یا دستی |
| **aio-cleaner** | **دستی** | انتخاب پلتفرم(های) مورد نظر برای پاکسازی (حالا شامل وبسایت) |

---

## ⏱️ محدودیتها

- **طرح رایگان GitHub** تا **۶ ساعت برای هر کار (job)** اجازه میدهد (مخازن عمومی **دقیقه نامحدود** دارند).
- فایلهای بزرگتر از **۹۹ مگابایت** بهطور خودکار به آرشیوهای ZIP چندبخشی (`.z01`, `.z02`, ...) تقسیم میشوند. برای استخراج به نرم افزاری مانند **7-Zip** یا **WinRAR** نیاز دارید.
- برای دستههای بسیار بزرگ اینستاگرام یا X، آنها را به گروههای کوچکتر تقسیم کنید.
- **دانلودر X (توییتر) حتماً به کوکی نیاز دارد** – بدون `X_COOKIES` کار نخواهد کرد.
- **آرشیو تلگرام فقط کانالهای عمومی** را پشتیبانی میکند.
- **ضبط وبسایت** فقط برای **وبسایت‌های عمومی** کار میکند. صفحات پشت ورود، CAPTCHA یا مسدودکننده‌های قوی ربات ممکن است失敗 شوند. حداکثر **۲۰ لینک داخلی** دنبال میشود؛ سایت‌های بزرگ با صدها صفحه کاملاً ضبط نخواهند شد.
- رسانههای تلگرام به سرعت فضا را پر میکنند. از **AIO Cleaner** بهطور منظم استفاده کنید.
- PDFهای ضبط شده وبسایت ممکن است بزرگ باشند (چند مگابایت هر کدام). پوشه `website/` را با AIO Cleaner زمانی که دیگر به ضبط‌های قدیمی نیاز ندارید پاک کنید.

---

## مدیریت فضای ذخیرهسازی مخزن (محدودیت ۵ گیگابایت)

مخازن GitHub دارای **محدودیت نرم ۵ گیگابایت** هستند. اگر زیاد دانلود کنید، پوشههای `youtube/`، `instagram/`، `x/`، `direct/`، `website/` و `telegram/content/` به سرعت پر میشوند.

### بهترین روش: استفاده از AIO Cleaner

سادهترین راه برای مدیریت فضا استفاده از گردشکار **aio-cleaner** است که در بالا توضیح داده شد — حالا شامل پوشه `website/` برای PDFهای ضبط شده نیز میشود.

### حذف دستی (در صورت تمایل)

#### حذف یک فایل
1. به فایل مورد نظر بروید (مثلاً `youtube/some-video.zip`).
2. روی **سه نقطه (`...`)** کلیک کنید.
3. **"Delete file"** را انتخاب کنید.
4. روی **"Commit changes"** کلیک و تأیید کنید.

#### حذف یک پوشه کامل
- ابتدا تمام فایلهای داخل پوشه را با روش بالا حذف کنید.
- سپس در پوشه والد، روی **سه نقطه (`...`)** کنار نام پوشه کلیک کنید.
- **"Delete directory"** را انتخاب کنید.
- روی **"Commit changes"** کلیک کنید.

> **نکته:** حجم مخزن را در **Settings → Repository → Repository size** بررسی کنید. اگر به ۵ گیگابایت نزدیک شد، فایلهای ZIP قدیمی را پاک کنید یا از **aio-cleaner** برای پاکسازی کل پوشهها استفاده کنید.

---

## مجوز (License)

MIT License

کپی رابت (c) 2025 ProAlit

بدینوسیله به هر شخصی که یک کپی از این نرم افزار و فایلهای مستندات همراه آن («نرم افزار») را دریافت میکند، بهطور رایگان و بدون محدودیت اجازه داده میشود که از نرم افزار استفاده کند، آن را کپی، ویرایش، ادغام، منتشر، توزیع، زیرمجوز دهد و / یا بفروشد، و به افرادی که نرم افزار به آنها ارائه میشود اجازه انجام آن را بدهد، مشروط بر رعایت شرایط زیر:

اعلان کپی رابت فوق و این اعلان مجوز باید در تمام کپیها یا بخشهای عمده نرم افزار گنجانده شود.

نرم افزار «همانگونه که هست» ارائه میشود، بدون هیچگونه ضمانتی، صریح یا ضمنی، شامل اما نه محدود به ضمانتهای تجاری بودن، تناسب برای یک هدف خاص و عدم نقض حقوق. در هیچ صورت نویسندگان یا دارندگان کپی رابت در قبال هرگونه ادعا، خسارت یا مسئولیت دیگری که از استفاده یا در ارتباط با نرم افزار ناشی شود، مسئول نخواهند بود.

## ⭐ اگر این پروژه را دوست دارید لطفاً به مخزن **ستاره** ⭐ بدهید — این کار به دیگران کمک میکند آن را پیدا کنند!

## مشکلات و مشارکتها
باگی پیدا کردید؟ پیشنهادی دارید؟ [یک issue باز کنید](https://github.com/ProAlit/aio-downloader/issues) — بازخورد همیشه خوشآمد است!
