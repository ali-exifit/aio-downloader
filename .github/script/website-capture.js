const { chromium } = require('playwright');
const { PDFDocument } = require('pdf-lib');
const fs = require('fs').promises;
const crypto = require('crypto');

const URL = process.argv[2];
if (!URL) {
  console.error('No URL provided');
  process.exit(1);
}

const MAX_LINKS = 20;                // cap to avoid huge PDFs
const VIEWPORT = { width: 1280, height: 720 };

// ---------- Helper: random 5 lowercase letters ----------
function randomFiveLetters() {
  return Array.from({ length: 5 }, () =>
    String.fromCharCode(97 + Math.floor(Math.random() * 26))
  ).join('');
}

// ---------- Wait for page to be fully loaded ----------
async function waitForStable(page) {
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {
    console.warn('Network did not become fully idle – continuing…');
  });
}

// ---------- Capture a URL → PDF buffer (full page) ----------
async function captureUrl(context, url) {
  const page = await context.newPage();
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await waitForStable(page);

    // Auto‑scroll to trigger lazy‑loaded images
    await page.evaluate(async () => {
      await new Promise(resolve => {
        let totalHeight = 0;
        const distance = 300;
        const timer = setInterval(() => {
          window.scrollBy(0, distance);
          totalHeight += distance;
          if (totalHeight >= document.body.scrollHeight) {
            clearInterval(timer);
            resolve();
          }
        }, 200);
      });
    });

    const pdfBuffer = await page.pdf({
      format: 'A4',
      printBackground: true,
      margin: { top: '20px', bottom: '20px', left: '20px', right: '20px' }
    });
    return pdfBuffer;
  } catch (err) {
    console.error(`Failed to capture ${url} – ${err.message}`);
    return null;
  } finally {
    await page.close();
  }
}

// ---------- Extract unique links from a page ----------
async function extractLinks(page) {
  return page.evaluate(() => {
    const links = Array.from(document.querySelectorAll('a[href]'))
      .map(a => a.href)                           // resolved absolute URL
      .filter(href => href.startsWith('http'));    // ignore javascript:, mailto: etc.
    return [...new Set(links)];
  });
}

// ---------- Main ----------
(async () => {
  console.log('Launching browser…');
  const browser = await chromium.launch({ headless: true });

  // Use a persistent context to mimic a real user session (cookies, localStorage)
  const context = await browser.newContext({
    viewport: VIEWPORT,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
  });

  // 1. Capture main page
  console.log(`Capturing main page: ${URL}`);
  const mainPdfBuf = await captureUrl(context, URL);
  if (!mainPdfBuf) {
    console.error('Main page capture failed');
    await browser.close();
    process.exit(1);
  }

  // 2. Extract same‑origin links from the main page
  let page;
  try {
    page = await context.newPage();
    await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await waitForStable(page);
    const allLinks = await extractLinks(page);
    await page.close();

    const mainOrigin = new URL(URL).origin;
    const uniqueLinks = [...new Set(
      allLinks
        .filter(link => link.startsWith(mainOrigin))  // same domain
        .map(link => link.split('#')[0])              // remove hash
    )].slice(0, MAX_LINKS);

    console.log(`Found ${uniqueLinks.length} unique internal links (capped at ${MAX_LINKS})`);

    // 3. Capture each linked page **within the same context** (user‑like navigation)
    const linkedPdfBufs = [];
    for (const link of uniqueLinks) {
      console.log(`Capturing linked page: ${link}`);
      const buf = await captureUrl(context, link);
      if (buf) linkedPdfBufs.push(buf);
    }

    // 4. Merge all PDFs
    const mergedPdf = await PDFDocument.create();
    const pdfsToMerge = [mainPdfBuf, ...linkedPdfBufs];

    for (const buf of pdfsToMerge) {
      const srcDoc = await PDFDocument.load(buf);
      const copiedPages = await mergedPdf.copyPages(srcDoc, srcDoc.getPageIndices());
      copiedPages.forEach(p => mergedPdf.addPage(p));
    }

    const finalPdfBytes = await mergedPdf.save();

    // 5. Generate filename: hostname‑random.pdf
    const hostname = new URL(URL).hostname.replace(/^www\./, '');
    const randomPart = randomFiveLetters();
    const filename = `${hostname}-${randomPart}.pdf`;
    console.log(`Generated filename: ${filename}`);

    // 6. Save the PDF temporarily and export the filename for the next step
    await fs.writeFile('output.pdf', finalPdfBytes);
    // Append the filename to $GITHUB_ENV so the upload step can use it
    await fs.appendFile(process.env.GITHUB_ENV, `FILENAME=${filename}\n`);

    console.log('Done.');
  } catch (err) {
    console.error(err);
    process.exit(1);
  } finally {
    await context.close();
    await browser.close();
  }
})();
