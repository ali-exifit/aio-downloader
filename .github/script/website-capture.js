const { chromium } = require('playwright');
const fs = require('fs').promises;
const { execSync } = require('child_process');

const inputUrl = process.argv[2];
if (!inputUrl) {
  console.error('No URL provided');
  process.exit(1);
}

const MAX_LINKS = 500;               // safety cap for the URL list
const VIEWPORT = { width: 1280, height: 720 };

// ---------- random 5 lowercase letters ----------
function randomFiveLetters() {
  return Array.from({ length: 5 }, () =>
    String.fromCharCode(97 + Math.floor(Math.random() * 26))
  ).join('');
}

// ---------- wait for full load ----------
async function waitForStable(page) {
  await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {
    console.warn('Network did not become fully idle – continuing…');
  });
  await page.waitForTimeout(3000);  // extra time for images/animations
}

// ---------- scroll to trigger lazy images ----------
async function scrollToLoad(page) {
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
  await page.waitForTimeout(2000);
}

// ---------- extract all unique links ----------
async function extractLinks(page) {
  return page.evaluate(() => {
    const links = Array.from(document.querySelectorAll('a[href]'))
      .map(a => a.href)                           // absolute URL
      .filter(href => href.startsWith('http'));    // ignore javascript:, mailto: etc.
    const seen = new Set();
    return links
      .map(link => link.split('#')[0])             // remove hash
      .filter(link => {
        if (seen.has(link)) return false;
        seen.add(link);
        return true;
      });
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

  const page = await context.newPage();
  try {
    // ----- 1. Capture main page with clickable links -----
    await page.goto(inputUrl, { waitUntil: 'load', timeout: 30000 });
    await waitForStable(page);
    await scrollToLoad(page);

    console.log('Saving main page as PDF (links will be clickable)…');
    await page.pdf({
      path: 'main.pdf',
      fullPage: true,
      printBackground: true,
      margin: { top: '0px', bottom: '0px', left: '0px', right: '0px' }
    });

    // ----- 2. Extract all links -----
    const allLinks = await extractLinks(page);
    console.log(`Found ${allLinks.length} unique links.`);

    // Limit to a safe maximum to avoid enormous PDFs
    const limitedLinks = allLinks.slice(0, MAX_LINKS);
    if (allLinks.length > MAX_LINKS) {
      console.log(`(Trimmed to ${MAX_LINKS} for the list.)`);
    }

    // ----- 3. Build a simple HTML page listing all URLs -----
    const listHtml = `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Extracted URLs</title>
<style>
  body { font-family: monospace; margin: 50px; }
  a   { display: block; word-break: break-all; margin-bottom: 8px; }
</style></head>
<body>
<h1>Extracted URLs from ${inputUrl}</h1>
<ol>
${limitedLinks.map(link => `<li><a href="${link}">${link}</a></li>`).join('\n')}
</ol>
</body></html>`;

    // Open the list in a new tab, capture it as PDF
    const listPage = await context.newPage();
    await listPage.setContent(listHtml, { waitUntil: 'load' });
    await listPage.waitForTimeout(1000); // let rendering finish
    await listPage.pdf({
      path: 'list.pdf',
      fullPage: true,
      printBackground: true,
      margin: { top: '20px', bottom: '20px', left: '20px', right: '20px' }
    });
    await listPage.close();

    // ----- 4. Merge both PDFs with ghostscript (keeps links intact) -----
    console.log('Merging with Ghostscript…');
    execSync(
      `gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=output.pdf main.pdf list.pdf`,
      { stdio: 'inherit' }
    );

    // ----- 5. Generate filename -----
    const hostname = new URL(inputUrl).hostname.replace(/^www\./, '');
    const randomPart = randomFiveLetters();
    const filename = `${hostname}-${randomPart}.pdf`;
    console.log(`Generated filename: ${filename}`);

    // Export filename for the upload step
    await fs.appendFile(process.env.GITHUB_ENV, `FILENAME=${filename}\n`);

    // Clean up temporary PDFs
    await fs.unlink('main.pdf');
    await fs.unlink('list.pdf');

    console.log('Done.');
  } catch (err) {
    console.error(err);
    process.exit(1);
  } finally {
    await page.close();
    await context.close();
    await browser.close();
  }
})();
