# aio-downloader — All-in-One GitHub Actions Downloader

**[راهنمای فارسی (Persian)](#راهنمای-فارسی)**

> A collection of **GitHub Actions workflows** that let you download videos, images, and files from **hundreds of websites** (YouTube, Instagram, X/Twitter, and many more via yt‑dlp), **any direct URL**, **archive public Telegram channels**, and **capture any website as a PDF** – all from your browser, **without running any software on your own computer**.

## Features

| Workflow | What it does |
|---|---|
| **Universal Leecher (yt‑dlp)** | Downloads videos/audio from **YouTube and 1,800+ other sites**. Use simple quality presets **or** any raw `yt-dlp` arguments if you are an advanced user. Supports video‑only, audio‑only, playlists, and more. |
| **Instagram Downloader** | Downloads **all media** from Instagram posts, reels, stories, highlights, and profiles – including mixed carousels. Handles both images and videos. |
| **X (Twitter) Downloader** | Downloads **all media** (images, videos) from X/Twitter posts and profiles. Requires login cookies. Uses `gallery-dl` under the hood. |
| **Direct Downloader** | Downloads **any file** from a direct URL using `aria2c` (16 parallel connections, ultra-fast). Splits files >99 MB into multi‑part ZIPs. |
| **Telegram Channel Archiver** | Scrapes **public Telegram channels** every 15 minutes (cron) or on manual trigger. Saves all new messages, photos, and videos as a Markdown archive in your repo. No API key needed. |
| **Website Capture** | Visits any public website, **follows up to 20 internal links**, captures every page as an A4 PDF, and merges everything into one polished document. Uses Playwright + Chromium behind the scenes. |
| **AIO Cleaner** | One manual workflow to **clean up storage** for all platforms. You choose exactly what to delete: Telegram media, YouTube files, X files, Instagram files, Website captures, or **all at once**. |

✅ **All downloads are automatically split into 99 MB parts, zipped, and uploaded back to your repository** – you can download them anytime from GitHub.
✅ **No server, no VPS, and no local installation required** – everything runs on GitHub's free infrastructure.
✅ **Cookies are stored securely** as GitHub Secrets – never exposed in logs or code.
✅ **Batch downloading** – paste up to 10+ Instagram or X links at once.
✅ **Concurrent runs** – trigger multiple workflows simultaneously; each run is independent.

---

## Requirements (Before You Start)

- A **GitHub account** (free)
- A **browser** (Chrome/Firefox/Edge) with the extension **"Get cookies.txt LOCALLY"** to export login cookies (for YouTube, Instagram, X)
- (Optional) An **Instagram account** for private/story content
- An **X (Twitter) account** (required for the X downloader)
- For Telegram and Website Capture: **nothing extra** – they work without login or API keys.

---

## How to Fork and Set Up

### Step 1: Fork the repository
Click the **"Fork"** button at the top‑right of this page.

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

> **Note:** YouTube and Instagram may require login cookies for some content. X (Twitter) **REQUIRES** login cookies. Telegram and Website Capture work without any cookies.

### 1. Export Cookies from Your Browser – Use a Private/Incognito Window!
- **Open a new private/incognito window** in your browser.
- Install the extension **"Get cookies.txt LOCALLY"** (Chrome Web Store or Firefox Add‑ons).
- In that private window, log into **youtube.com** (for YouTube), **instagram.com** (for Instagram), or **x.com** (for X).
- Click the extension icon and choose **"Export"** (Netscape format).
- Save the `.txt` file somewhere safe.
- **Close the private window completely** – this ensures the exported session is not kept open elsewhere.

### 2. Add Cookies as GitHub Secrets
1. In your forked repository, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Create a secret named **`YOUTUBE_COOKIES`** and paste the entire contents of your YouTube `cookies.txt`.
4. Create a secret named **`INSTAGRAM_COOKIES`** and paste your Instagram `cookies.txt`.
5. Create a secret named **`X_COOKIES`** and paste your X (Twitter) `cookies.txt`.

> ⚠️ **Never commit cookie files directly to the repository.** The workflow creates a temporary file from the secrets.

---

## How to Use Every Workflow

### 1. Universal Leecher (yt‑dlp) – YouTube & 1,800+ Sites

This workflow uses `yt-dlp`, the most powerful video downloader. You can use **simple quality presets** or, if you are an expert, **full raw `yt-dlp` arguments**.

#### Simple Mode (Quality Presets)

1. Go to **Actions** → select **"youtube-downloader"**
2. Click **"Run workflow"**
3. Enter one or more entries, each on a new line (or comma‑separated). Format: `URL v/a resolution fps` (fps optional).

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
- If you omit `v/a`, it defaults to **video max quality**

4. Click **"Run workflow"** → output appears in the **`youtube/`** folder.

#### Advanced / Raw Mode (For Expert Users)

If you need features like `--playlist-reverse`, `--dateafter`, `--cookies-from-browser`, or any other yt‑dlp option, **just pass them directly** as the input. The workflow will detect raw options and skip the simple parser.

**Example (raw):**

```
https://www.youtube.com/playlist?list=PL... --playlist-reverse --dateafter 20250101
```

You can find the **complete list of supported sites** here:  
🔗 [yt‑dlp Supported Sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

> 💡 **What can you download?** YouTube, Vimeo, Twitch, Dailymotion, TikTok, Facebook videos, Twitter videos, Reddit, BBC, CNN, … – over 1,800 sites.

---

### 2. Instagram Downloader

1. Go to **Actions** → select **"instagram-downloader"**
2. Click **"Run workflow"**
3. Paste Instagram links – separated by commas, spaces, or newlines.

**Example:**

```
https://www.instagram.com/p/DX2y7oLDFOb/, https://www.instagram.com/reel/DVRXhn0gjL3/, https://www.instagram.com/p/DX6US4uCNGb/
```

4. Click **"Run workflow"** → output appears as a ZIP in the **`instagram/`** folder.  
   Up to 10+ links are bundled into one ZIP.

---

### 3. X (Twitter) Downloader

1. Go to **Actions** → select **"x-downloader"**
2. Click **"Run workflow"**
3. Paste X links – separated by commas, spaces, or newlines.

**Example:**

```
https://x.com/username/status/123456789, https://x.com/otheruser/status/987654321
```

> ⚠️ **`X_COOKIES` secret is mandatory.** (See the cookies section above.)

4. Click **"Run workflow"** → the ZIP appears in the **`x/`** folder.

---

### 4. Direct Downloader

1. Go to **Actions** → select **"direct-downloader"**
2. Click **"Run workflow"**
3. Paste direct download URLs (e.g., `.zip`, `.mp4`, `.apk`, `.pdf`), separated by commas, spaces, or newlines.

**Example:**

```
https://example.com/path/to/large-file.zip, https://example.com/another-file.mp4
```

4. Click **"Run workflow"** → files appear in **`direct/`** folder (split into 99 MB parts if needed).

---

### 5. Telegram Channel Archiver

Scrapes **public Telegram channels** and stores messages, photos, and videos as a Markdown archive. It can run **automatically every 15 minutes** or **manually whenever you want**.

> If the automatic cron ever stops (e.g., GitHub disables scheduled runs on inactive forks), you can **always trigger it manually** – manual runs are 100% reliable.

#### How It Works (Step by Step)

1. Reads your channel list from `telegram/channels.json`.
2. Launches a Chromium browser (Playwright) and visits `https://t.me/s/<channel>`.
3. Scrolls to fetch all new messages since the last check.
4. Extracts message text, UTC times, photos (CSS background‑url), and videos (`<video>` tags).
5. Downloads all media into `telegram/content/`.
6. Converts UTC times to Iran/Tehran timezone and Jalali (Hijri‑Shamsi) calendar dates.
7. Sorts all messages from all channels by time (newest first).
8. Writes everything into `telegram.md` at the root of your repo with Markdown formatting.
9. Saves the last message ID per channel in `telegram/last_ids.json` so only new content is fetched next time.
10. Commits and pushes the changes with a 5‑retry loop.

#### Viewing Your Archive

Open `telegram.md` in your repository. GitHub renders Markdown natively – you’ll see formatted text, embedded images, and clickable video links. All dates are in Jalali calendar with Tehran timezone.

**Example output:**

```
# Telegram Channel Archive

## 1404/02/16 14:30 — channelname
![Photo](telegram/content/channelname_12345_1712345678.jpg)

> This is the message text

## 1404/02/16 14:15 — otherchannel
[🎬 Video](telegram/content/otherchannel_67890_1712345678.mp4)

> Another message
```

#### Add or Remove Channels

Edit `telegram/channels.json` directly on GitHub (click the **pencil icon** ✏️).  
Add or remove usernames (with or without `@`). Only **public** channels work.

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
  "kianmeli1"
]
```

Commit the changes – the next run (automatic or manual) picks them up.

#### Trigger Manually

1. **Actions** → **"telegram-fetcher"**
2. **"Run workflow"** → **"Run workflow"**

---

### 6. Website Capture (NEW)

Turns any **public website** into a single, polished PDF document. It uses **Playwright + Chromium** to render pages exactly like a real user would see them – including JavaScript, CSS, images, and dynamic content.

Perfect for:
- Archiving news articles, blog posts, or documentation for offline reading.
- Creating printable copies of web content.
- Preserving pages that may change or disappear.

#### How It Works

1. You provide a URL.
2. The workflow launches Chromium and captures the main page as an A4 PDF (with print backgrounds, proper margins).
3. It extracts **up to 20 internal links** from the same domain.
4. Each linked page is visited and captured as a PDF.
5. All PDFs are merged into one file using `pdf-lib` – main page first, then internal pages.
6. The merged PDF is saved to `website/` with a descriptive name like `hostname-random5chars.pdf`.
7. The file is committed and pushed to your repository.

#### How to Use

1. Go to **Actions** → select **"website-capture"**
2. Click **"Run workflow"**
3. Enter the full URL (must start with `https://`).

**Examples:**

```
https://example.com/article/my-post
https://developer.mozilla.org/en-US/docs/Web/JavaScript
https://github.com/ProAlit/aio-downloader
```

4. Click **"Run workflow"** – within 5–10 minutes the PDF appears in the **`website/`** folder.

> ⚠️ **Limitations:**  
> - Only public sites (no login walls).  
> - Maximum 20 internal links are followed.  
> - 30‑minute timeout per capture.  
> - JavaScript‑heavy single‑page apps may not render perfectly.  
> - No cookies needed!

---

### 7. AIO Cleaner – Manage Your Storage

All downloads go into your repository and can quickly eat into GitHub’s **5 GB soft limit**. The **AIO Cleaner** lets you wipe the downloads of any platform with one click.

#### What It Cleans

| Platform | What gets deleted |
|---|---|
| **Telegram** | The `telegram/content/` folder (media) and `telegram.md` (archive). Your channel list and message‑tracking files are kept. |
| **YouTube / Universal** | The entire `youtube/` folder. |
| **Instagram** | The entire `instagram/` folder. |
| **X (Twitter)** | The entire `x/` folder. |
| **Website** | The entire `website/` folder (captured PDFs). |
| **Leecher** | The entire `leecher/` folder. |

#### How to Run

1. Go to **Actions** → select **"aio-cleaner"**
2. Click **"Run workflow"**
3. You’ll see six checkboxes:
   - ✅ **Clean ALL platforms** – wipe everything.
   - ✅ **Clean Telegram**
   - ✅ **Clean Youtube**
   - ✅ **Clean X**
   - ✅ **Clean Instagram**
   - ✅ **Clean Website**
4. Tick the platforms you want to clean, then click **"Run workflow"**.  
   Example: Tick only **Clean Website** to remove all captured PDFs.

> ⚠️ Deletion is permanent. Make sure you have saved any important files first.

The cleaner runs in seconds and commits the deletions automatically. Check your repository size at **Settings → Repository → Repository size** regularly.

---

## ⏱️ Limitations & Tips

- **GitHub Free Tier:** up to 6 hours per job (public repos get unlimited minutes).
- Files > **99 MB** are split into multi‑part ZIP archives (`.z01`, `.z02` …). Use **7‑Zip** or **WinRAR** to extract.
- Very large batches should be split into smaller groups.
- **X (Twitter) downloader requires cookies.**
- **Telegram archiver only works with public channels.**
- **Website Capture** works only on public sites; up to 20 internal links are followed.
- Use the **AIO Cleaner** regularly to keep storage under control.

---

## Support

⭐ If this project is useful to you, please **give the repo a star** – it helps others discover it.

🐛 **Found a bug? Have a suggestion?**  
Open an issue [here](https://github.com/ProAlit/aio-downloader/issues).  
For faster help, include:
- The workflow name you were running.
- The input you used (without your cookies!).
- The error message or log (copy it from the Actions tab).

---

## License

MIT License

---

# راهنمای فارسی

## aio-downloader — دانلودر همه کاره با GitHub Actions

> مجموعه ای از **گردش کارهای GitHub Actions** که به شما امکان می دهند ویدیوها، تصاویر و فایل ها را از **صدها وبسایت** (یوتیوب، اینستاگرام، X/توییتر و بسیاری دیگر از طریق yt‑dlp)، **هر لینک مستقیم**، **آرشیو کانال های عمومی تلگرام** و **ذخیره هر وبسایت به صورت PDF** دانلود کنید – همه از مرورگرتان، **بدون اجرای هیچ نرم افزاری روی کامپیوترتان**.

## ویژگی ها

| گردش کار | کاربرد |
|---|---|
| **دانلودر جهانی (yt‑dlp)** | دانلود ویدیو/صدا از **یوتیوب و بیش از ۱,۸۰۰ سایت دیگر**. می توانید از پیش فرض های ساده کیفیت استفاده کنید **یا** اگر کاربر حرفه ای هستید، آرگومان های کامل `yt-dlp` را وارد کنید. |
| **دانلودر اینستاگرام** | دانلود **تمام محتوا** از پست ها، ریلزها، استوری ها، هایلایت ها و پروفایل ها – شامل کاروسل های ترکیبی. |
| **دانلودر X (توییتر)** | دانلود تمام عکس ها و ویدیوها از توییت ها و پروفایل های X. نیاز به کوکی ورود دارد. |
| **دانلودر مستقیم** | دانلود **هر فایلی** از لینک مستقیم با `aria2c` (۱۶ اتصال موازی). فایل های بزرگتر از ۹۹ مگابایت به ZIP چند بخشی تقسیم می شوند. |
| **آرشیو کانال تلگرام** | اسکن **کانال های عمومی تلگرام** هر ۱۵ دقیقه (یا دستی) و ذخیره پیام ها، عکس ها و ویدیوها به صورت بایگانی Markdown. بدون نیاز به API. |
| **ضبط وبسایت** | از یک وبسایت عمومی بازدید می کند، **تا ۲۰ لینک داخلی** را دنبال می کند، هر صفحه را به PDF با اندازه A4 تبدیل و همه را در یک فایل ادغام می کند. از Playwright + Chromium استفاده می کند. |
| **پاک کننده جامع (AIO Cleaner)** | یک گردش کار دستی برای **پاکسازی فضای ذخیره سازی** همه پلتفرم ها. شما انتخاب می کنید چه چیزی حذف شود: محتوای تلگرام، یوتیوب، X، اینستاگرام، وبسایت، یا **همه با هم**. |

✅ تمام دانلودها به طور خودکار به قطعات ۹۹ مگابایتی تقسیم، فشرده و در مخزن شما آپلود می شوند.
✅ بدون نیاز به سرور، VPS یا نصب نرم افزار – همه چیز روی زیرساخت رایگان GitHub اجرا می شود.
✅ کوکی ها به صورت امن در GitHub Secrets ذخیره می شوند – هرگز در لاگ ها یا کد نمایش داده نمی شوند.
✅ دانلود دسته جمعی – تا ۱۰+ لینک اینستاگرام یا X همزمان.
✅ اجرای همزمان – می توانید چندین گردش کار را همزمان اجرا کنید.

---

## پیش نیازها (قبل از شروع)

- یک **حساب GitHub** (رایگان)
- یک **مرورگر** (Chrome/Firefox/Edge) با افزونه **"Get cookies.txt LOCALLY"** برای استخراج کوکی های ورود
- (اختیاری) یک **حساب اینستاگرام** برای محتوای خصوصی/استوری
- یک **حساب X (توییتر)** (برای دانلودر X الزامی است)
- برای تلگرام و ضبط وبسایت: **هیچ چیز اضافی لازم نیست** – بدون ورود یا API کار می کنند.

---

## نحوه فورک کردن و راه اندازی

### مرحله ۱: فورک کردن مخزن
روی دکمه **"Fork"** در بالای صفحه کلیک کنید.

### مرحله ۲: فعال کردن GitHub Actions
1. به مخزن فورک شده خود بروید → **Settings** → **Actions** → **General**
2. در بخش **"Actions permissions"** گزینه **"Allow all actions and reusable workflows"** را انتخاب کنید.
3. روی **Save** کلیک کنید.

### مرحله ۳: دادن دسترسی نوشتن به GitHub Actions (مهم!)
1. همان مسیر → **"Workflow permissions"**
2. گزینه **"Read and write permissions"** را انتخاب کنید.
3. روی **Save** کلیک کنید.

> ⚠️ اگر این مرحله را انجام ندهید، گردش کار هنگام آپلود فایل های ZIP با خطا مواجه می شود.

---

## نحوه اضافه کردن کوکی ها (برای یوتیوب، اینستاگرام و X)

> توجه: یوتیوب و اینستاگرام ممکن است برای برخی محتواها به کوکی نیاز داشته باشند. X (توییتر) **حتماً** به کوکی نیاز دارد. تلگرام و ضبط وبسایت بدون کوکی کار می کنند.

### ۱. استخراج کوکی ها از مرورگر – حتماً از پنجره ناشناس/خصوصی استفاده کنید!
- **یک پنجره جدید ناشناس/خصوصی** در مرورگر خود باز کنید.
- افزونه **"Get cookies.txt LOCALLY"** را نصب کنید.
- در همان پنجره خصوصی وارد **youtube.com**، **instagram.com** یا **x.com** شوید.
- روی آیکون افزونه کلیک کنید و **"Export"** (فرمت Netscape) را انتخاب کنید.
- فایل `.txt` را در جای امنی ذخیره کنید.
- **پنجره خصوصی را کاملاً ببندید** – این اطمینان می دهد که نشست صادر شده در جای دیگری باز نمی ماند.

### ۲. اضافه کردن کوکی ها به عنوان GitHub Secrets
1. در مخزن فورک شده، به **Settings** → **Secrets and variables** → **Actions** بروید.
2. روی **"New repository secret"** کلیک کنید.
3. یک secret با نام **`YOUTUBE_COOKIES`** بسازید و محتوای فایل یوتیوب را بچسبانید.
4. یک secret با نام **`INSTAGRAM_COOKIES`** بسازید و محتوای فایل اینستاگرام را بچسبانید.
5. یک secret با نام **`X_COOKIES`** بسازید و محتوای فایل X را بچسبانید.

> ⚠️ هرگز فایل های کوکی را مستقیماً در مخزن commit نکنید. گردش کار از secrets استفاده می کند.

---

## راهنمای کامل هر گردش کار

### ۱. دانلودر جهانی (yt‑dlp) – یوتیوب و ۱,۸۰۰+ سایت

این گردش کار از `yt-dlp` قدرتمندترین ابزار دانلود ویدیو استفاده می کند. می توانید از **پیش فرض های ساده** یا **آرگومان های کامل `yt-dlp`** (برای کاربران حرفه ای) استفاده کنید.

#### حالت ساده (پیش فرض های کیفیت)

1. به **Actions** بروید → **"youtube-downloader"** را انتخاب کنید.
2. روی **"Run workflow"** کلیک کنید.
3. یک یا چند ورودی وارد کنید (هر خط جداگانه یا با کاما). فرمت: `URL v/a رزولوشن fps` (fps اختیاری).

**مثال ها:**

```
https://www.youtube.com/watch?v=VIDEO_ID v max
https://www.youtube.com/watch?v=VIDEO_ID v 1080 60
https://www.youtube.com/watch?v=VIDEO_ID a max
https://www.youtube.com/watch?v=VIDEO_ID v 4k, https://www.youtube.com/watch?v=VIDEO_ID a 128
```

- `v` = ویدیو، `a` = صدا
- رزولوشن: `max`, `min`, `1080`, `2k`, `4k` و غیره
- FPS: اختیاری
- اگر `v/a` را وارد نکنید، به طور پیش فرض **حداکثر کیفیت ویدیو** انتخاب می شود.

4. روی **"Run workflow"** کلیک کنید → خروجی در پوشه **`youtube/`** قرار می گیرد.

#### حالت پیشرفته / خام (برای کاربران حرفه ای)

اگر به گزینه هایی مانند `--playlist-reverse`, `--dateafter`, `--cookies-from-browser` یا هر گزینه دیگر yt‑dlp نیاز دارید، **می توانید آن ها را مستقیماً وارد کنید**. گردش کار گزینه های خام را تشخیص داده و پردازش می کند.

**مثال (خام):**

```
https://www.youtube.com/playlist?list=PL... --playlist-reverse --dateafter 20250101
```

لیست کامل سایت های پشتیبانی شده:  
🔗 [yt‑dlp Supported Sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

> 💡 **چه سایت هایی را می توان دانلود کرد؟** یوتیوب، Vimeo، Twitch، Dailymotion، TikTok، فیسبوک، توییتر، Reddit، BBC، CNN و ... – بیش از ۱,۸۰۰ سایت.

---

### ۲. دانلودر اینستاگرام

1. **Actions** → **"instagram-downloader"**
2. روی **"Run workflow"** کلیک کنید.
3. لینک های اینستاگرام را با کاما، فاصله یا خط جدید جدا کنید.

**مثال:**

```
https://www.instagram.com/p/DX2y7oLDFOb/, https://www.instagram.com/reel/DVRXhn0gjL3/, https://www.instagram.com/p/DX6US4uCNGb/
```

4. روی **"Run workflow"** کلیک کنید → فایل ZIP در پوشه **`instagram/`** قرار می گیرد.  
   تا ۱۰+ لینک در یک ZIP بسته بندی می شوند.

---

### ۳. دانلودر X (توییتر)

1. **Actions** → **"x-downloader"**
2. روی **"Run workflow"** کلیک کنید.
3. لینک های X را با کاما، فاصله یا خط جدید جدا کنید.

**مثال:**

```
https://x.com/username/status/123456789, https://x.com/otheruser/status/987654321
```

> ⚠️ **کوکی `X_COOKIES` الزامی است** (بخش کوکی ها را ببینید).

4. روی **"Run workflow"** کلیک کنید → ZIP در پوشه **`x/`** قرار می گیرد.

---

### ۴. دانلودر مستقیم

1. **Actions** → **"direct-downloader"**
2. روی **"Run workflow"** کلیک کنید.
3. لینک های مستقیم (مثلاً `.zip`, `.mp4`, `.apk`, `.pdf`) را بچسبانید.

**مثال:**

```
https://example.com/path/to/large-file.zip, https://example.com/another-file.mp4
```

4. روی **"Run workflow"** کلیک کنید → فایل ها در **`direct/`** (تقسیم شده در صورت >99MB).

---

### ۵. آرشیو کانال تلگرام

کانال های عمومی تلگرام را اسکن کرده و پیام ها، عکس ها و ویدیوها را به صورت بایگانی Markdown ذخیره می کند. می تواند **خودکار (هر ۱۵ دقیقه)** یا **دستی** اجرا شود.

> اگر زمان بندی خودکار متوقف شد، می توانید همیشه آن را **دستی** اجرا کنید – اجرای دستی کاملاً قابل اعتماد است.

#### نحوه کار (گام به گام)

1. خواندن لیست کانال ها از `telegram/channels.json`.
2. راه اندازی مرورگر Chromium (Playwright) و بازدید از `https://t.me/s/<channel>`.
3. اسکرول برای دریافت پیام های جدید.
4. استخراج متن، زمان UTC، عکس ها و ویدیوها.
5. دانلود رسانه ها در `telegram/content/`.
6. تبدیل زمان ها به منطقه زمانی تهران و تقویم جلالی.
7. مرتب سازی همه پیام ها از جدید به قدیم.
8. نوشتن در `telegram.md` با فرمت Markdown.
9. ذخیره آخرین شناسه پیام در `telegram/last_ids.json`.
10. Commit و push (با ۵ بار تلاش مجدد).

#### مشاهده بایگانی

فایل `telegram.md` را در مخزن باز کنید. GitHub مارک داون را نمایش می دهد – متن های نقل قول، تصاویر و لینک ویدیوها. تاریخ ها به تقویم جلالی با زمان تهران است.

#### افزودن/حذف کانال

فایل `telegram/channels.json` را ویرایش کنید (آیکون مداد ✏️). فقط کانال های **عمومی** کار می کنند.

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
  "kianmeli1"
]
```

#### اجرای دستی

1. **Actions** → **"telegram-fetcher"**
2. **"Run workflow"** → **"Run workflow"**

---

### ۶. ضبط وبسایت (جدید)

هر وبسایت **عمومی** را به یک فایل PDF واحد و باکیفیت تبدیل می کند. از **Playwright + Chromium** استفاده می کند تا صفحات را دقیقاً مانند یک کاربر واقعی نمایش دهد.

#### نحوه استفاده

1. **Actions** → **"website-capture"**
2. روی **"Run workflow"** کلیک کنید.
3. آدرس کامل (با `https://`) را وارد کنید.

**مثال ها:**

```
https://example.com/article/my-post
https://developer.mozilla.org/en-US/docs/Web/JavaScript
https://github.com/ProAlit/aio-downloader
```

4. کلیک کنید – ظرف ۵–۱۰ دقیقه PDF در پوشه **`website/`** ظاهر می شود.

> ⚠️ **محدودیت ها:**  
> - فقط سایت های عمومی (بدون دیوار ورود).  
> - حداکثر ۲۰ لینک داخلی دنبال می شود.  
> - مهلت ۳۰ دقیقه ای.  
> - صفحات مبتنی بر JavaScript سنگین ممکن است کامل رندر نشوند.  
> - بدون نیاز به کوکی!

---

### ۷. پاک کننده جامع (AIO Cleaner)

فضای مخزن شما با دانلودها پر می شود. این گردش کار به شما اجازه می دهد هر پلتفرم را با یک کلیک پاک کنید.

#### چه چیزهایی پاک می شوند

| پلتفرم | آنچه حذف می شود |
|---|---|
| **تلگرام** | پوشه `telegram/content/` و فایل `telegram.md` |
| **یوتیوب / جهانی** | کل پوشه `youtube/` |
| **اینستاگرام** | کل پوشه `instagram/` |
| **X (توییتر)** | کل پوشه `x/` |
| **وبسایت** | کل پوشه `website/` |
| **لیچر** | کل پوشه `leecher/` |

#### نحوه اجرا

1. **Actions** → **"aio-cleaner"**
2. روی **"Run workflow"** کلیک کنید.
3. چک باکس های مورد نظر را تیک بزنید (یا **Clean ALL platforms** برای همه).
4. روی **"Run workflow"** کلیک کنید.

> ⚠️ حذف دائمی است. مطمئن شوید فایل های مهم را قبلاً ذخیره کرده اید.

---

## ⏱️ محدودیت ها و نکات

- حساب رایگان GitHub تا ۶ ساعت برای هر کار (مخازن عمومی دقیقه نامحدود دارند).
- فایل های >۹۹ MB به ZIP چند بخشی تقسیم می شوند (7‑Zip / WinRAR برای استخراج).
- دسته های خیلی بزرگ را به گروه های کوچکتر تقسیم کنید.
- **دانلودر X به کوکی نیاز دارد.**
- **آرشیو تلگرام فقط کانال های عمومی.**
- **ضبط وبسایت** فقط سایت های عمومی؛ حداکثر ۲۰ لینک.
- از **AIO Cleaner** به طور منظم برای مدیریت فضا استفاده کنید.

---

## پشتیبانی

⭐ اگر این پروژه برایتان مفید است، لطفاً **به مخزن ستاره بدهید** – به دیگران کمک می کند آن را پیدا کنند.

🐛 **باگ یا پیشنهاد؟**  
یک issue [اینجا](https://github.com/ProAlit/aio-downloader/issues) باز کنید.  
برای رسیدگی سریع تر، لطفاً این موارد را ذکر کنید:
- نام گردش کاری که اجرا کردید.
- ورودی هایی که استفاده کردید (بدون کوکی هایتان!).
- پیام خطا یا لاگ (از تب Actions کپی کنید).

---

## مجوز

MIT License
