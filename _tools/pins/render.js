// Renders pin images from a JSON job file: node render.js <jobs.json>
// Each job: {out, theme, kind: "quote"|"list", kicker, text | title+items+cta}
const { chromium } = require("playwright");
const fs = require("fs");
const os = require("os");
const path = require("path");

const here = __dirname;
const root = path.resolve(here, "..", "..");
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

const css = `
@font-face { font-family: Lora; src: url(file://${here}/fonts/Lora.ttf); font-weight: 400 700; }
* { box-sizing: border-box; margin: 0; }
body { width: 1000px; height: 1500px; font-family: Inter, sans-serif; -webkit-font-smoothing: antialiased; }
.pin { width: 1000px; height: 1500px; position: relative; overflow: hidden; color: #fff; display: flex; flex-direction: column; padding: 110px 90px 90px; }
.night { background: radial-gradient(120% 80% at 30% 10%, #3b3f8f 0%, #1a1636 60%, #0d0b1f 100%); }
.brand { background: linear-gradient(160deg, #667eea 0%, #764ba2 100%); }
.blush { background: linear-gradient(160deg, #f6d1c1 0%, #e8a6b8 45%, #9a7ad0 100%); color: #2a2148; }
.glow { position: absolute; width: 900px; height: 900px; border-radius: 50%; background: radial-gradient(closest-side, rgba(255,255,255,.18), rgba(255,255,255,0)); top: -250px; right: -300px; }
.stars { position: absolute; inset: 0; background-image: radial-gradient(1.5px 1.5px at 20% 30%, rgba(255,255,255,.8), transparent), radial-gradient(1px 1px at 70% 20%, rgba(255,255,255,.7), transparent), radial-gradient(1.5px 1.5px at 40% 75%, rgba(255,255,255,.6), transparent), radial-gradient(1px 1px at 85% 60%, rgba(255,255,255,.7), transparent), radial-gradient(1px 1px at 10% 85%, rgba(255,255,255,.6), transparent), radial-gradient(2px 2px at 60% 45%, rgba(255,255,255,.5), transparent), radial-gradient(1px 1px at 30% 55%, rgba(255,255,255,.6), transparent), radial-gradient(1.5px 1.5px at 90% 15%, rgba(255,255,255,.7), transparent); }
.kicker { position: relative; font-size: 30px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; opacity: .85; }
.quote { position: relative; flex: 1; display: flex; align-items: center; font-family: Lora, serif; font-weight: 500; font-size: 92px; line-height: 1.18; letter-spacing: -.01em; }
.quote.long { font-size: 78px; }
.quote span::before { content: "\\201C"; display: block; font-size: 180px; line-height: .6; opacity: .45; margin-bottom: 30px; }
.title { position: relative; font-family: Lora, serif; font-weight: 600; font-size: 96px; line-height: 1.05; margin: 26px 0 50px; }
.list { position: relative; list-style: none; padding: 0; flex: 1; }
.list li { font-family: Lora, serif; font-size: 44px; line-height: 1.3; padding: 26px 0 26px 56px; border-top: 1px solid rgba(255,255,255,.22); position: relative; }
.blush .list li { border-top-color: rgba(42,33,72,.18); }
.list li::before { content: "\\2726"; position: absolute; left: 0; top: 30px; font-size: 30px; opacity: .8; }
.foot { position: relative; display: flex; align-items: center; gap: 22px; margin-top: 40px; }
.foot img { width: 76px; height: 76px; border-radius: 18px; box-shadow: 0 10px 30px rgba(0,0,0,.25); }
.foot b { display: block; font-size: 32px; }
.foot b span { font-weight: 500; opacity: .75; }
.foot small { font-size: 28px; font-weight: 600; opacity: .9; }
.cta { position: relative; margin-top: 10px; display: inline-block; background: #fff; color: #4b3a8f; font-weight: 700; font-size: 34px; padding: 22px 38px; border-radius: 60px; align-self: flex-start; }
.blush .cta { background: #2a2148; color: #fff; }
`;

function pinHtml(j) {
  const deco = j.theme === "night" ? '<div class="stars"></div>' : j.theme === "brand" ? '<div class="glow"></div>' : "";
  const foot = `<div class="foot"><img src="file://${root}/app-icon.png"><div><b>Daily Affirmations <span>· Free on the App Store</span></b><small>acanalab.com/dailyaffirmationsapp</small></div></div>`;
  const body = j.kind === "quote"
    ? `<div class="quote${j.text.length > 48 ? " long" : ""}"><span>${esc(j.text)}</span></div>`
    : `<div class="title">${esc(j.title)}</div><ul class="list">${j.items.map((i) => `<li>${esc(i)}</li>`).join("")}</ul><div class="cta">${esc(j.cta)} →</div>`;
  return `<div class="pin ${j.theme}">${deco}<div class="kicker">${esc(j.kicker)}</div>${body}${foot}</div>`;
}

(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" }).catch(() => chromium.launch());
  const page = await browser.newPage({ viewport: { width: 1000, height: 1500 } });
  const tmp = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "pins-")), "pin.html");
  for (const j of jobs) {
    fs.writeFileSync(tmp, `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>${pinHtml(j)}</body></html>`);
    await page.goto("file://" + tmp, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: j.out, type: "jpeg", quality: 88 });
  }
  await browser.close();
})();
