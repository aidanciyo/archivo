// Uso: node render.js engine/UT1.html outDir fps fStart fEnd  → out/f00000.jpg ...
const { chromium } = require("playwright");
const path = require("path"), fs = require("fs");
(async () => {
  const [html, out, fpsS, a, b] = process.argv.slice(2);
  const fps = parseFloat(fpsS), f0 = parseInt(a), f1 = parseInt(b);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ args: ["--allow-file-access-from-files", "--font-render-hinting=none", "--disable-gpu-vsync"] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on("pageerror", (e) => console.log("pageerror:", e.message));
  await page.goto("file://" + path.resolve(html));
  await page.waitForFunction(() => window.ENGINE_READY === true || window.ENGINE_ERROR, null, { timeout: 60000 });
  const err = await page.evaluate(() => window.ENGINE_ERROR);
  if (err) { console.log("ENGINE_ERROR", err); process.exit(1); }
  const t0 = Date.now();
  let n = 0;
  for (let f = f0; f < f1; f++) {
    const file = path.join(out, `f${String(f).padStart(5, "0")}.jpg`);
    if (fs.existsSync(file) && fs.statSync(file).size > 1000) continue;
    await page.evaluate((x) => window.renderFrame(x), f / fps);
    const buf = await page.screenshot({ type: "jpeg", quality: 93 });
    fs.writeFileSync(file + ".tmp", buf); fs.renameSync(file + ".tmp", file);
    n++;
    if (n % 300 === 0) console.log(`${path.basename(html)} ${f}/${f1} ${((Date.now() - t0) / n).toFixed(0)} ms/f`);
  }
  console.log(`done ${path.basename(html)} [${f0},${f1}) ${n} frames, ${n ? ((Date.now() - t0) / n).toFixed(0) : 0} ms/frame`);
  await browser.close();
})();
