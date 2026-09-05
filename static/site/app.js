/* ═══════════ SAHAYAK APP — shared JS for inner pages ═══════════
   Handles: header injection, navigation, language toggle, scheme data,
   page rendering. Vanilla, no build step. */

/* ───────── Scheme data (shared) ───────── */
const SCHEME_DATA = [
  {
    id: 'pmegp', name: 'PMEGP', fullName: 'PM Employment Generation Programme',
    icon: '🏦', ministry: 'Ministry of MSME', category: 'SC/ST/OBC', type: 'Loan + Subsidy',
    amount: 'Up to ₹10L', benefit: 'Loan up to ₹10L with 25% margin subsidy',
    desc: 'The PM Employment Generation Programme (PMEGP) is a central credit-linked subsidy programme for generating self-employment through micro-enterprises in the non-farm sector.',
    score: 94, scoreComp: { eligibility: 98, goalFit: 92, financial: 90, category: 95, effort: 88 },
    status: 'eligible', filter: ['funding','loan'], badge: 'eligible',
    documents: ['Caste Certificate','Income Certificate','Business Plan','Bank Statement'],
    heldDocs: ['Aadhaar'],
    why: 'Your tailoring business goal aligns with PMEGP\'s employment generation focus. As an SC entrepreneur with a 2L funding need, you qualify for the full subsidy bracket.',
    source: 'moje.gov.in/schemes/pmegp §4.2',
    eligibility: [
      { rule: 'Category: SC — Matched', st: 'ok' },
      { rule: 'Age: 28 (range 18-45) — Matched', st: 'ok' },
      { rule: 'Business: Startup — Matched', st: 'ok' },
      { rule: 'Income < ₹3L — Matched', st: 'ok' },
      { rule: 'Turnover: Not verified', st: 'pend' }
    ],
    applySteps: ['Gather required documents','Visit nearest CSC or DIC office','Submit application online','Track status via reference number']
  },
  {
    id: 'mudra', name: 'MUDRA Loan', fullName: 'Micro Units Development & Refinance Agency',
    icon: '💼', ministry: 'Ministry of Finance', category: 'All', type: 'Working Capital',
    amount: 'Up to ₹10L', benefit: 'Working capital loans (Shishu ₹50K, Kishor ₹5L, Tarun ₹10L)',
    desc: 'MUDRA provides collateral-free loans to micro and small enterprises in three categories: Shishu (up to ₹50K), Kishor (up to ₹5L), and Tarun (up to ₹10L).',
    score: 88, scoreComp: { eligibility: 90, goalFit: 85, financial: 88, category: 90, effort: 84 },
    status: 'eligible', filter: ['loan'], badge: 'popular',
    documents: ['Aadhaar','Bank Statement','Business Plan'],
    heldDocs: ['Aadhaar'],
    why: 'Your working-capital need fits MUDRA\'s Shishu/Kishor category perfectly. The loan amount matches your stated requirement.',
    source: 'mudra.org.in/eligibility §2',
    eligibility: [
      { rule: 'Category: All — Matched', st: 'ok' },
      { rule: 'Collateral not required', st: 'ok' },
      { rule: 'Age: Any — Matched', st: 'ok' }
    ],
    applySteps: ['Visit any PMJDY-linked bank','Submit loan application','Approval via bank branch']
  },
  {
    id: 'standup', name: 'Stand-Up India', fullName: 'Stand-Up India Scheme',
    icon: '🤝', ministry: 'Ministry of Finance', category: 'SC/ST/Women', type: 'Bank Loan',
    amount: '₹10L – ₹1Cr', benefit: 'Bank loans from ₹10L to ₹1Cr for greenfield enterprises',
    desc: 'Stand-Up India facilitates bank loans between ₹10 lakh and ₹1 crore to at least one SC or ST borrower and one woman borrower per bank branch.',
    score: 72, scoreComp: { eligibility: 60, goalFit: 75, financial: 78, category: 85, effort: 60 },
    status: 'uncertain', filter: ['funding','women'], badge: 'new',
    documents: ['Caste Certificate','Business Plan','Identity Proof'],
    heldDocs: ['Aadhaar'],
    why: 'This scheme targets greenfield enterprises for SC/ST and women. Your category matches, but documents to confirm turnover are pending.',
    source: 'standupmitra.in §3.1',
    eligibility: [
      { rule: 'Category: SC — Matched', st: 'ok' },
      { rule: 'Greenfield business needed', st: 'pend' },
      { rule: 'Turnover not verified', st: 'pend' }
    ],
    applySteps: ['Verify greenfield status','Prepare business plan','Apply via bank branch']
  },
  {
    id: 'asiiim', name: 'ASIIM', fullName: 'Ambedkar Social Innovation & Incubation Mission',
    icon: '🎓', ministry: 'Ministry of Social Justice', category: 'SC Youth', type: 'Incubation',
    amount: '₹30L / 3 yrs', benefit: '₹30L over 3 years for SC youth in incubation',
    desc: 'ASIIM supports SC youth through innovation, incubation, and entrepreneurship with funding of ₹30L over three years.',
    score: 80, scoreComp: { eligibility: 75, goalFit: 85, financial: 70, category: 90, effort: 75 },
    status: 'eligible', filter: ['skill'], badge: 'eligible',
    documents: ['Caste Certificate','Education Proof'],
    heldDocs: ['Aadhaar'],
    why: 'Your goal of skill development and incubation aligns with ASIIM\'s focus on SC youth entrepreneurs.',
    source: 'socialjustice.nic.in/asciim §1',
    eligibility: [
      { rule: 'Category: SC — Matched', st: 'ok' },
      { rule: 'Age: 18-35 — Matched', st: 'ok' },
      { rule: 'SC youth — Matched', st: 'ok' }
    ],
    applySteps: ['Register on incubation portal','Submit proposal','Await selection']
  },
  {
    id: 'nsfdc', name: 'NSFDC Schemes', fullName: 'National SC Finance and Development Corporation',
    icon: '🏗️', ministry: 'National SC Finance & Dev Corp', category: 'SC', type: 'Concessional',
    amount: 'Up to ₹50L', benefit: 'Concessional loans at reduced interest rates',
    desc: 'NSFDC provides financial assistance to SC entrepreneurs in the form of concessional loans at reduced interest rates.',
    score: 34, scoreComp: { eligibility: 20, goalFit: 60, financial: 40, category: 40, effort: 30 },
    status: 'noteligible', filter: ['loan','funding'], badge: 'popular',
    documents: ['Caste Certificate','Bank Statement'],
    heldDocs: [],
    why: 'This scheme is not applicable — business stage exceeds the eligible ceiling for funding.',
    source: 'nsfdc.gov.in/rules §5',
    eligibility: [
      { rule: 'Category: SC — Matched', st: 'ok' },
      { rule: 'Age limit exceeded (45y max, you are 48)', st: 'miss' },
      { rule: 'Turnover exceeds limit', st: 'miss' }
    ],
    applySteps: ['Check age eligibility','Contact NSFDC channel partner']
  },
  {
    id: 'nai-roshni', name: 'Nai Roshni', fullName: 'Leadership Development for Women',
    icon: '🌸', ministry: 'Minority Affairs', category: 'Women', type: 'Skill Training',
    amount: 'Free', benefit: 'Leadership and skill training program for women',
    desc: 'Nai Roshni is a leadership development program for women providing skill training and capacity building.',
    score: 78, scoreComp: { eligibility: 80, goalFit: 75, financial: 85, category: 82, effort: 68 },
    status: 'eligible', filter: ['skill','women'], badge: 'new',
    documents: ['Identity Proof'],
    heldDocs: ['Aadhaar'],
    why: 'As a woman entrepreneur seeking skill development, Nai Roshni\'s capacity-building focus matches your needs.',
    source: 'minorityaffairs.gov.in/nairoshni §2',
    eligibility: [
      { rule: 'Category: Women — Matched', st: 'ok' },
      { rule: 'Skill training need — Matched', st: 'ok' }
    ],
    applySteps: ['Find local training center','Enroll for batch','Complete training']
  },
  {
    id: 'ddu-gky', name: 'DDU-GKY', fullName: 'Deen Dayal Upadhyaya Grameen Kaushalya Yojana',
    icon: '🛠️', ministry: 'Rural Development', category: 'Rural Youth', type: 'Skill Training',
    amount: 'Free + Stipend', benefit: 'Placement-linked skill training for rural youth',
    desc: 'DDU-GKY is a placement-linked skill training initiative providing free training with a stipend to rural youth.',
    score: 82, scoreComp: { eligibility: 80, goalFit: 84, financial: 85, category: 80, effort: 78 },
    status: 'eligible', filter: ['skill'], badge: 'eligible',
    documents: ['Identity Proof','Bank Account'],
    heldDocs: ['Aadhaar'],
    why: 'Your interest in skill development for rural micro-enterprises aligns with DDU-GKY\'s placement-linked training focus.',
    source: 'ddugky.gov.in §2',
    eligibility: [
      { rule: 'Category: Rural youth — Matched', st: 'ok' },
      { rule: 'Age: 15-35 — Matched', st: 'ok' },
      { rule: 'Residence: Rural — Matched', st: 'ok' }
    ],
    applySteps: ['Register at training centre','Complete skill training','Get placement support']
  },
  {
    id: 'entprog', name: 'Entrepreneurship Prog', fullName: 'NSFDC Entrepreneurship Development Program',
    icon: '🚀', ministry: 'National SC Finance & Dev Corp', category: 'SC', type: 'Loan + Mentoring',
    amount: 'Up to ₹1Cr', benefit: 'Soft loans and mentoring for first-time SC entrepreneurs',
    desc: 'The entrepreneurship development program offers soft loans with mentoring support for first-time SC entrepreneurs.',
    score: 76, scoreComp: { eligibility: 72, goalFit: 80, financial: 74, category: 85, effort: 66 },
    status: 'eligible', filter: ['funding','loan'], badge: 'popular',
    documents: ['Caste Certificate','Business Plan'],
    heldDocs: ['Aadhaar'],
    why: 'Your startup goal and SC category match this mentoring-backed entrepreneurship loan program.',
    source: 'nsfdc.gov.in/edp §3',
    eligibility: [
      { rule: 'Category: SC — Matched', st: 'ok' },
      { rule: 'First-time entrepreneur — Matched', st: 'ok' },
      { rule: 'Business plan needed', st: 'pend' }
    ],
    applySteps: ['Prepare business plan','Apply to NSFDC partner','Get mentoring support']
  }
];

const BADGE_TEXT = { eligible:'ELIGIBLE', popular:'Popular', new:'New', uncertain:'UNCERTAIN', noteligible:'NOT ELIGIBLE' };
const SCORE_COLORS = { eligibility:'#22C55E', goalFit:'#3B82F6', financial:'#C08552', category:'#7C3AED', effort:'#6B7280' };
const SB_NAMES = { eligibility:'Eligibility', goalFit:'Goal Fit', financial:'Financial', category:'Category', effort:'Effort' };

/* ───────── Shared i18n ───────── */
const NAV_I18N = {
  'Home': {hi:'होम', en:'Home'},
  'Chat': {hi:'चैट', en:'Chat'},
  'Results': {hi:'परिणाम', en:'Results'},
  'Dashboard': {hi:'डैशबोर्ड', en:'Dashboard'},
  'Documents': {hi:'दस्तावेज़', en:'Documents'}
};

/* ───────── Language ───────── */
function getLang() { try { return localStorage.getItem('sa_lang') || 'hi'; } catch (e) { return 'hi'; } }
function setLangGlobal(lang) {
  try { localStorage.setItem('sa_lang', lang); } catch (e) {}
  document.documentElement.lang = lang;
  document.querySelectorAll('.lang-text').forEach(el => {
    const key = el.dataset.i18n;
    if (NAV_I18N[key] && NAV_I18N[key][lang]) el.textContent = NAV_I18N[key][lang];
  });
  document.querySelectorAll('.lang-btn').forEach(b => b.classList.toggle('active', b.textContent.includes(lang==='hi'?'हिन्दी':'EN')));
}

/* ───────── Header + footer ───────── */
function hasGeneratedSession() {
  try { return window.localStorage.getItem('sa_session_generated') === '1'; } catch (e) { return false; }
}

function buildHeader(activePage) {
  // Flow-gated navigation: Home + Chat are always shown. Results and Dashboard
  // appear only AFTER the user completes a chat session (which triggers the
  // AI to auto-generate their results/dashboard/documentation). The knowledge-
  // base editor (Documents) is intentionally not linked here — it stays in
  // the background for admins.
  const navItems = [
    ['Home', 'index.html', 'Home'],
    ['Chat', 'chat.html', 'Chat']
  ];
  if (hasGeneratedSession()) navItems.push(['Results', 'results.html', 'Results']);
  if (hasGeneratedSession()) navItems.push(['Dashboard', 'dashboard.html', 'Dashboard']);

  const links = navItems.map(([label, href, key]) =>
    `<li><a href="${href}" class="${label === activePage ? 'active-nav' : ''}"><span class="lang-text" data-i18n="${label}">${label}</span></a></li>`
  ).join('');

  document.getElementById('pageHeader').innerHTML = `
    <a href="index.html" class="logo">
      <div class="logo-icon">S</div>
      <div class="logo-text">Sahayak</div>
    </a>
    <ul class="nav-links" id="pageNav">${links}</ul>
    <div class="header-actions">
      <div class="lang-toggle" id="langToggle">
        <div class="lang-pill"></div>
        <button class="lang-btn active" onclick="setLangGlobal('hi')">हिन्दी</button>
        <button class="lang-btn" onclick="setLangGlobal('en')">EN</button>
      </div>
      <a href="login.html" class="btn btn-accent" style="padding:9px 22px;font-size:13px;" id="headerAuth">Start</a>
      <button class="mobile-menu-btn" id="mobileBtn" aria-label="Menu"><span></span><span></span><span></span></button>
    </div>
  `;
  // Reflect auth state on the CTA button.
  const user = window.Sahayak && window.Sahayak.currentUser && window.Sahayak.currentUser();
  const authBtn = document.getElementById('headerAuth');
  if (authBtn) {
    if (user) {
      authBtn.textContent = 'My Dashboard';
      authBtn.href = 'dashboard.html';
    } else {
      authBtn.textContent = 'Sign in';
      authBtn.href = 'login.html';
    }
  }
  setLangGlobal(getLang());
}

function buildFooter() {
  const f = document.getElementById('pageFooter');
  if (!f) return;
  f.innerHTML = `
    <div class="af-inner">
      <div class="logo-text" style="margin-bottom:8px;">Sahayak</div>
      <div style="display:flex;gap:24px;flex-wrap:wrap;">
        <a href="chat.html">Chat</a><a href="results.html">Results</a>
        <a href="dashboard.html">Dashboard</a>
      </div>
      <span>© 2026 Sahayak · MoSJE</span>
    </div>
  `;
}

/* ───────── Mobile menu ───────── */
function initMobileMenu() {
  const m = document.getElementById('mobileBtn');
  const n = document.getElementById('pageNav') || document.getElementById('navLinks');
  if (m && n) m.addEventListener('click', () => n.classList.toggle('open'));
}

/* ───────── Scroll reveal ───────── */
function initReveal() {
  const io = new IntersectionObserver(entries => {
    entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('visible'); io.unobserve(en.target); } });
  }, { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
}
