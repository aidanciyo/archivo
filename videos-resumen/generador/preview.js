// Uso: node preview.js engine/UT1.html outdir t1 t2 ...  → PNG por instante
const { chromium } = require(process.env.PW_PATH || "playwright");
const path = require("path"), fs = require("fs");
(async () => {
  const [html, out, ...ts] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ args: ["--allow-file-access-from-files", "--font-render-hinting=none"] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") console.log("console:", m.text()); });
  page.on("pageerror", (e) => console.log("pageerror:", e.message));
  await page.goto("file://" + path.resolve(html));
  await page.waitForFunction(() => window.ENGINE_READY === true || window.ENGINE_ERROR, null, { timeout: 60000 });
  const err = await page.evaluate(() => window.ENGINE_ERROR);
  if (err) { console.log("ENGINE_ERROR", err); process.exit(1); }
  for (const t of ts) {
    await page.evaluate((x) => window.renderFrame(x), parseFloat(t));
    const f = path.join(out, `t${String(parseFloat(t).toFixed(2)).padStart(7, "0")}.png`);
    await page.screenshot({ path: f });
    console.log(f);
  }
  await browser.close();
})();
