const { chromium } = require('playwright');
const { PDFDocument } = require('pdf-lib');
const fs = require('fs').promises;

const inputUrl = process.argv[2];
if (!inputUrl) {
  console.error('No URL provided');
  process.exit(1);
}

const MAX_LINKS = 150;                // capture up to 75 linked pages
const VIEWPORT = { width: 1280, height: 720 };

// ---------- random 5 lowercase letters ----------
function randomFiveLetters() {
  return Array.from({ length: 5 }, () =>
    String.fromCharCode(97 + Math.floor(Math.random() * 26))
  ).join('');
}

// ---------- wait for page to be fully loaded ----------
async function waitForStable(page) {
  // wait for network idle (no ongoing requests for 500ms) with a generous timeout
  await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {
    console.warn('Network did not become fully idle – continuing…');
  });
  // extra fixed delay to let images/animations finish rendering
  await page.waitForTimeout(3000);
}

// ---------- capture a URL → PDF buffer (full page, as seen) ----------
async function captureUrl(context, url) {
  const page = await context.newPage();
  try {
    // use 'load' to wait for all resources (images, CSS, etc.)
    await page.goto(url, { waitUntil: 'load', timeout: 30000 });
    await waitForStable(page);

    // scroll to trigger lazy images
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

    // short extra pause after scrolling to let newly loaded images settle
    await page.waitForTimeout(2000);

    // capture the entire page as one continuous PDF
    return await page.pdf({
      fullPage: true,
      printBackground: true,
      margin: { top: '0px', bottom: '0px', left: '0px', right: '0px' }
    });
  } catch (err) {
    console.error(`Failed to capture ${url} – ${err.message}`);
    return null;
  } finally {
    await page.close();
  }
}

// ---------- extract unique links from a page ----------
async function extractLinks(page) {
  return page.evaluate(() => {
    const links = Array.from(document.querySelectorAll('a[href]'))
      .map(a => a.href)                           // absolute URL
      .filter(href => href.startsWith('http'));    // ignore javascript:, mailto: etc.
    // deduplicate while preserving order
    return [...new Set(links)];
  });
}

// ---------- main ----------
(async () => {
  console.log('Launching browser…');
  const browser = await chromium.launch({ headless: true });

  const context = await browser.newContext({
    viewport: VIEWPORT,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
  });

  // 1. main page
  console.log(`Capturing main page: ${inputUrl}`);
  const mainPdfBuf = await captureUrl(context, inputUrl);
  if (!mainPdfBuf) {
    console.error('Main page capture failed');
    await browser.close();
    process.exit(1);
  }

  // 2. extract all unique links from the main page
  let page;
  try {
    page = await context.newPage();
    await page.goto(inputUrl, { waitUntil: 'load', timeout: 30000 });
    await waitForStable(page);
    const allLinks = await extractLinks(page);
    await page.close();

    // remove hash fragments and keep only the first occurrence (preserving order)
    const seen = new Set();
    const uniqueLinks = allLinks
      .map(link => link.split('#')[0])  // strip hash
      .filter(link => {
        if (seen.has(link)) return false;
        seen.add(link);
        return true;
      })
      .slice(0, MAX_LINKS);

    console.log(`Found ${uniqueLinks.length} unique links (capped at ${MAX_LINKS})`);

    // 3. capture each linked page (same context → user‑like session)
    const linkedPdfBufs = [];
    for (const link of uniqueLinks) {
      console.log(`Capturing linked page: ${link}`);
      const buf = await captureUrl(context, link);
      if (buf) linkedPdfBufs.push(buf);
    }

    // 4. merge all PDFs
    const mergedPdf = await PDFDocument.create();
    const pdfsToMerge = [mainPdfBuf, ...linkedPdfBufs];

    for (const buf of pdfsToMerge) {
      const srcDoc = await PDFDocument.load(buf);
      const copiedPages = await mergedPdf.copyPages(srcDoc, srcDoc.getPageIndices());
      copiedPages.forEach(p => mergedPdf.addPage(p));
    }

    const finalPdfBytes = await mergedPdf.save();

    // 5. filename: hostname-random.pdf
    const hostname = new URL(inputUrl).hostname.replace(/^www\./, '');
    const randomPart = randomFiveLetters();
    const filename = `${hostname}-${randomPart}.pdf`;
    console.log(`Generated filename: ${filename}`);

    // 6. save and export filename for the upload step
    await fs.writeFile('output.pdf', finalPdfBytes);
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
