// Render pmax_vs_radius.svg to PNG with the preinstalled Chromium.
// NODE_PATH=$(npm root -g) node render.js
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 780 }, deviceScaleFactor: 2 });
  await page.goto('file://' + path.join(__dirname, 'pmax_vs_radius.svg'));
  await page.screenshot({ path: path.join(__dirname, 'pmax_vs_radius.png') });
  await browser.close();
})();
