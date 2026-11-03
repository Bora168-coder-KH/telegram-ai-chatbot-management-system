// Drive the real dashboard as Dara and save screenshots + highlight boxes (in image pixels).
// Usage: node admin.js A | B
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE = 'http://127.0.0.1:8765';
const DIR = path.join(__dirname, 'shots');
const BOXES = path.join(__dirname, 'boxes.json');
const DSF = 1.25; // 1536x864 CSS px -> 1920x1080 image px (like 125% browser zoom)
fs.mkdirSync(DIR, { recursive: true });
const boxes = fs.existsSync(BOXES) ? JSON.parse(fs.readFileSync(BOXES)) : {};

async function shot(page, name, targets = {}) {
  await page.waitForTimeout(400);
  const b = {};
  for (const [key, loc] of Object.entries(targets)) {
    const r = await loc.first().boundingBox();
    if (r) b[key] = [r.x, r.y, r.width, r.height].map((v) => Math.round(v * DSF));
    else console.warn('no box', name, key);
  }
  boxes[name] = b;
  await page.screenshot({ path: path.join(DIR, name + '.png') });
  console.log('shot', name, JSON.stringify(b));
}

async function center(page, sel) {
  await page.addStyleTag({ content: 'main { padding-bottom: 420px !important; }' });
  await page.locator(sel).first().evaluate((el) => el.scrollIntoView({ block: 'center' }));
}
async function top(page, sel) {
  await page.locator(sel).first().evaluate((el) => { el.scrollIntoView({ block: 'start' }); window.scrollBy(0, -24); });
}

async function login(page, email, password) {
  await page.goto(BASE + '/login');
  await page.fill('input[name=email]', email);
  await page.fill('input[name=password]', password);
  return page;
}

async function phaseA(page) {
  await login(page, 'dara@university.example', 'demo-password-1');
  await shot(page, 'login', { form: page.locator('form').first() });
  await page.click('button:has-text("Log in")');
  await page.waitForURL('**/dashboard');
  await page.waitForTimeout(1200);
  await shot(page, 'dashboard-top', { cards: page.locator('section.cards').first() });
  await page.evaluate(() => window.scrollBy(0, 560));
  await shot(page, 'dashboard-charts', {});
  await center(page, 'tr:has-text("is there a bus to campus")');
  await shot(page, 'dashboard-unanswered', {
    row: page.locator('tr:has-text("is there a bus to campus")'),
    addfaq: page.locator('tr:has-text("is there a bus to campus") a:has-text("Add FAQ")'),
  });
  // Conversations queue
  await page.evaluate(() => window.scrollTo(0, 0));
  await shot(page, 'nav-conversations', { nav: page.locator('nav a:has-text("Conversations")') });
  await page.click('nav a:has-text("Conversations")');
  await page.waitForLoadState('networkidle');
  await shot(page, 'conversations', { row: page.locator('tr:has-text("Sok Sokha")') });
  await page.click('tr:has-text("Sok Sokha") a:has-text("Open")');
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => document.querySelectorAll('*').forEach((el) => { if (el.scrollHeight > el.clientHeight + 10 && getComputedStyle(el).overflowY !== 'visible') el.scrollTop = 0; }));
  await shot(page, 'conversation-start', {});
  await page.evaluate(() => document.querySelectorAll('*').forEach((el) => { if (el.scrollHeight > el.clientHeight + 10 && getComputedStyle(el).overflowY !== 'visible') el.scrollTop = el.scrollHeight; }));
  await shot(page, 'conversation-top', { detected: page.locator('h3:has-text("Detected") + dl') });
  await page.locator('h3:has-text("Detected")').scrollIntoViewIfNeeded();
  await shot(page, 'conversation-detected', { detected: page.locator('h3:has-text("Detected") + dl') });
  // Reply
  const reply = 'Hello Sokha! Thank you for your question. Our staff will send you the campus bus information today.';
  await page.locator('textarea[name=text]').scrollIntoViewIfNeeded();
  await page.fill('textarea[name=text]', reply);
  await shot(page, 'conversation-reply-typed', { box: page.locator('form.reply'), send: page.locator('button:has-text("Send reply")') });
  await page.click('button:has-text("Send reply")');
  await page.waitForTimeout(800);
  await shot(page, 'conversation-reply-sent', { resolved: page.locator('button:has-text("Resolved")') });
  await page.click('button:has-text("Resolved")');
  await page.waitForTimeout(800);
  await shot(page, 'conversation-resolved', { status: page.locator('#handoff-panel .badge').first() });
  // Add FAQ from the dashboard's unanswered list
  await page.goto(BASE + '/dashboard');
  await center(page, 'tr:has-text("is there a bus to campus")');
  await shot(page, 'dashboard-addfaq', { addfaq: page.locator('tr:has-text("is there a bus to campus") a:has-text("Add FAQ")') });
  await page.click('tr:has-text("is there a bus to campus") a:has-text("Add FAQ")');
  await page.waitForLoadState('networkidle');
  await shot(page, 'faq-prefilled', { question: page.locator('input[name=question]') });
  await page.fill('textarea[name=answer]', 'Yes. A free campus bus leaves the city stop every hour from 7:00 to 17:00. (Demo answer)');
  await page.selectOption('select[name=category]', 'General').catch(() => {});
  await page.selectOption('select[name=language]', 'en').catch(() => {});
  await page.fill('input[name=keywords]', 'bus to campus, shuttle bus, campus bus');
  await shot(page, 'faq-filled', { answer: page.locator('textarea[name=answer]'), keywords: page.locator('input[name=keywords]'), add: page.locator('form button:has-text("Add FAQ")') });
  await page.click('form button:has-text("Add FAQ")');
  await page.waitForTimeout(800);
  await shot(page, 'faq-added', { row: page.locator('tr:has-text("campus bus")').first() });
}

async function phaseB(page) {
  await login(page, 'dara@university.example', 'demo-password-1');
  await page.click('button:has-text("Log in")');
  await page.waitForURL('**/dashboard');
  // FAQ page overview (SC-015)
  await page.goto(BASE + '/faq');
  await shot(page, 'faq-page', { form: page.locator('form').first(), toggle: page.locator('button:has-text("Disable")').first() });
  // Broadcast
  await page.goto(BASE + '/broadcast');
  const msg = 'Reminder: the help desk is open Monday to Friday, 8:00 to 17:00. (Demo message)';
  await page.fill('textarea[name=message]', msg);
  await shot(page, 'broadcast-preview', { message: page.locator('textarea[name=message]'), audience: page.locator('select[name=audience]'), send: page.locator('button:has-text("Send / schedule")') });
  await page.click('button:has-text("Send / schedule")');
  await page.waitForTimeout(2500);
  await page.goto(BASE + '/broadcast');
  await page.locator('h2:has-text("History")').scrollIntoViewIfNeeded();
  await shot(page, 'broadcast-history', { history: page.locator('h2:has-text("History") + *') });
  // Reports
  await page.goto(BASE + '/reports');
  await shot(page, 'reports', { pdf: page.locator('a:has-text("Export PDF")'), excel: page.locator('a:has-text("Export Excel")') });
  const href = await page.locator('a:has-text("Export PDF")').getAttribute('href');
  const res = await page.request.get(BASE + href);
  fs.writeFileSync(path.join(DIR, 'report.pdf'), await res.body());
  // Settings: roles + create a Viewer account
  await page.goto(BASE + '/settings');
  await top(page, 'h2:has-text("Roles and permissions")');
  await shot(page, 'settings-roles', { roles: page.locator('h2:has-text("Roles and permissions") ~ *').first() });
  await top(page, 'h2:has-text("Admin accounts and agents")');
  const nf = page.locator('form:has(h3:has-text("New account"))');
  await nf.locator('input[name=name]').fill('Viewer Demo');
  await nf.locator('input[name=email]').fill('viewer@university.example');
  await nf.locator('input[name=password]').fill('viewer-pass-1');
  const newForm = page.locator('form:has(h3:has-text("New account"))');
  await newForm.locator('select[name=role_id]').selectOption({ label: 'Viewer' });
  await newForm.locator('input[name=is_agent]').uncheck();
  await shot(page, 'settings-new-viewer', { form: page.locator('form:has(h3:has-text("New account"))') });
  await page.click('button:has-text("Create account")');
  await page.waitForLoadState('networkidle');
  await top(page, 'h2:has-text("Admin accounts and agents")');
  await shot(page, 'settings-accounts', { viewer: page.locator('tr:has-text("Viewer Demo")') });
  // Log out, log in as Viewer
  await page.click('button:has-text("Log out")');
  await login(page, 'viewer@university.example', 'viewer-pass-1');
  await page.click('button:has-text("Log in")');
  await page.waitForURL('**/dashboard');
  await shot(page, 'viewer-dashboard', { nav: page.locator('nav') });
  await page.click('nav a:has-text("Users")');
  await page.waitForLoadState('networkidle');
  await shot(page, 'viewer-users', { nav: page.locator('nav'), row: page.locator('tbody tr').first() });
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1536, height: 864 }, deviceScaleFactor: DSF });
  page.on('dialog', (d) => d.accept());
  const CDN = path.join(__dirname, '..', 'cdn', 'node_modules');
  await page.route('https://unpkg.com/htmx.org**', (r) => r.fulfill({ path: path.join(CDN, 'htmx.org/dist/htmx.min.js'), contentType: 'application/javascript' }));
  await page.route('https://cdn.jsdelivr.net/npm/chart.js**', (r) => r.fulfill({ path: path.join(CDN, 'chart.js/dist/chart.umd.js'), contentType: 'application/javascript' }));
  try {
    if (process.argv[2] === 'A') await phaseA(page); else await phaseB(page);
  } finally {
    fs.writeFileSync(BOXES, JSON.stringify(boxes, null, 1));
    await browser.close();
  }
})();
