const { chromium } = require('playwright');
const { PDFDocument } = require('pdf-lib');
const fs = require('fs').promises;

const inputUrl = process.argv[2];            // <-- renamed to avoid shadowing URL
if (!inputUrl) {
  console.error('No URL provided');
  process.exit(1);
}

const MAX_LINKS = 20;
const VIEWPORT = { width: 1280, height: 720 };

function randomFiveLetters() {
  return Array.from({ length: 5 }, () =>
    String.fromCharCode(97 + Math.floor(Math.random() * 26))
  ).join('');
}

async function waitForStable(page) {
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {
    console.warn('Network did not become fully idle – continuing…');
  });
}

async function captureUrl(context, url) {
  const page = await context.newPage();
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await waitForStable(page);

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

    return await page.pdf({
      format: 'A4',
      printBackground: true,
      margin: { top: '20px', bottom: '20px', left: '20px', right: '20px' }
    });
  } catch (err) {
    console.error(`Failed to capture ${url} – ${err.message}`);
    return null;
  } finally {
    await page.close();
  }
}

async function extractLinks(page) {
  return page.evaluate(() => {
    const links = Array.from(document.querySelectorAll('a[href]'))
      .map(a => a.href)
      .filter(href => href.startsWith('http'));
    return [...new Set(links)];
  });
}

(async () => {
  console.log('Launching browser…');
  const browser = await chromium.launch({ headless: true });

  const context = await browser.newContext({
    viewport: VIEWPORT,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
  });

  console.log(`Capturing main page: ${inputUrl}`);
  const mainPdfBuf = await captureUrl(context, inputUrl);
  if (!mainPdfBuf) {
    console.error('Main page capture failed');
    await browser.close();
    process.exit(1);
  }

  let page;
  try {
    page = await context.newPage();
    await page.goto(inputUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await waitForStable(page);
    const allLinks = await extractLinks(page);
    await page.close();

    const mainOrigin = new URL(inputUrl).origin;          // now works – URL is global class
    const uniqueLinks = [...new Set(
      allLinks
        .filter(link => link.startsWith(mainOrigin))
        .map(link => link.split('#')[0])
    )].slice(0, MAX_LINKS);

    console.log(`Found ${uniqueLinks.length} unique internal links (capped at ${MAX_LINKS})`);

    const linkedPdfBufs = [];
    for (const link of uniqueLinks) {
      console.log(`Capturing linked page: ${link}`);
      const buf = await captureUrl(context, link);
      if (buf) linkedPdfBufs.push(buf);
    }

    const mergedPdf = await PDFDocument.create();
    const pdfsToMerge = [mainPdfBuf, ...linkedPdfBufs];

    for (const buf of pdfsToMerge) {
      const srcDoc = await PDFDocument.load(buf);
      const copiedPages = await mergedPdf.copyPages(srcDoc, srcDoc.getPageIndices());
      copiedPages.forEach(p => mergedPdf.addPage(p));
    }

    const finalPdfBytes = await mergedPdf.save();

    const hostname = new URL(inputUrl).hostname.replace(/^www\./, '');
    const randomPart = randomFiveLetters();
    const filename = `${hostname}-${randomPart}.pdf`;
    console.log(`Generated filename: ${filename}`);

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
