/* ═══════════ SAHAYAK SCHEME CATALOG ═══════════
   Display metadata keyed by the RAG chunk_id PREFIX (e.g. "scheme_pmegp_v1").
   The live document TEXT (authoritative explainer body) is fetched from the
   backend /documents endpoint at run time and rendered on the Results and
   Scheme-detail pages. These fields only describe HOW to present a scheme
   (name, icon, ministry, portal link) -- the explainer itself comes from the
   indexed document so it always matches what the chatbot cites.
*/
window.SCHEME_CATALOG = {
  'scheme_standup_india_v1': {
    id: 'standup-india', aliases: ['standup', 'stand-up', 'standupindia'], name: 'Stand-Up India',
    fullName: 'Stand-Up India Scheme',
    icon: '🤝', ministry: 'Ministry of Finance (Dept of Financial Services)',
    category: 'SC / ST / Women', type: 'Bank Loan',
    amount: '₹10 lakh – ₹1 crore',
    portal: 'https://www.standupmitra.in',
  },
  'scheme_pmegp_v1': {
    id: 'pmegp', aliases: ['pmegp'], name: 'PMEGP',
    fullName: 'Prime Minister\'s Employment Generation Programme',
    icon: '🏦', ministry: 'Ministry of MSME (KVIC)',
    category: 'All, incl. SC/ST/OBC/transgender', type: 'Loan + Subsidy',
    amount: 'Up to ₹50L (mfg) / ₹20L (service)',
    portal: 'https://www.kviconline.gov.in/pmegp',
  },
  'scheme_mudra_pmmy_v1': {
    id: 'mudra', aliases: ['mudra', 'pmmy'], name: 'MUDRA Loan',
    fullName: 'Pradhan Mantri MUDRA Yojana (PMMY)',
    icon: '💼', ministry: 'Ministry of Finance (MUDRA)',
    category: 'All', type: 'Working Capital',
    amount: '₹50K – ₹20L (Shishu/Kishor/Tarun/Tarun Plus)',
    portal: 'https://www.mudra.org.in',
  },
  'scheme_nsfdc_v1': {
    id: 'nsfdc', aliases: ['nsfdc', 'entprog'], name: 'NSFDC Schemes',
    fullName: 'National Scheduled Castes Finance & Development Corporation',
    icon: '🏗️', ministry: 'Ministry of Social Justice & Empowerment',
    category: 'SC', type: 'Concessional Loan',
    amount: 'Micro ₹1.25L / Term up to ₹45L',
    portal: 'https://nsfdc.nic.in',
  },
  'scheme_asiiim_v1': {
    id: 'asiiim', aliases: ['asiiim'], name: 'ASIIM',
    fullName: 'Ambedkar Social Innovation & Incubation Mission',
    icon: '🎓', ministry: 'Ministry of Social Justice & Empowerment (VCF-SC)',
    category: 'SC Youth / Divyang', type: 'Equity + Incubation',
    amount: '₹30L over 3 years (+₹15Cr follow-on)',
    portal: 'https://www.vcfsc.in/asiim',
  },
  'scheme_nai_roshni_v1': {
    id: 'nai-roshni', aliases: ['nai-roshni', 'nairoshni'], name: 'Nai Roshni',
    fullName: 'Leadership Development of Minority Women',
    icon: '🌸', ministry: 'Ministry of Minority Affairs',
    category: 'Women (minority)', type: 'Skill Training',
    amount: 'Free (stipend + training)',
    portal: 'https://www.minorityaffairs.gov.in',
  },
  'scheme_ddu_gky_v1': {
    id: 'ddu-gky', aliases: ['ddu-gky', 'ddugky'], name: 'DDU-GKY',
    fullName: 'Deen Dayal Upadhyaya Grameen Kaushalya Yojana',
    icon: '🛠️', ministry: 'Ministry of Rural Development',
    category: 'Rural Youth (15–35/45)', type: 'Skill Training + Placement',
    amount: 'Free + stipend',
    portal: 'https://ddugky.gov.in',
  },
  'scheme_pm_svanidhi_v1': {
    id: 'pm-svanidhi', aliases: ['pm-svanidhi', 'pmsvanidhi', 'svanidhi'], name: 'PM SVANidhi',
    fullName: 'PM Street Vendor\'s AtmaNirbhar Nidhi',
    icon: '🛺', ministry: 'Ministry of Housing & Urban Affairs (MoHUA)',
    category: 'Street Vendors', type: 'Working Capital',
    amount: '₹10K / ₹20K / ₹50K tranches',
    portal: 'https://pmavanidhi.gov.in',
  },
  'scheme_credit_guarantee_v1': {
    id: 'cgtmse', aliases: ['cgtmse', 'credit-guarantee'], name: 'CGTMSE',
    fullName: 'Credit Guarantee Fund Trust for Micro & Small Enterprises',
    icon: '🛡️', ministry: 'Ministry of MSME & SIDBI',
    category: 'MSEs (collateral-free)', type: 'Credit Guarantee',
    amount: 'Cover up to ₹10Cr',
    portal: 'https://www.cgtmse.in',
  },
  'scheme_pm_vishwakarma_v1': {
    id: 'pm-vishwakarma', aliases: ['pm-vishwakarma', 'pmvishwakarma', 'vishwakarma'], name: 'PM Vishwakarma',
    fullName: 'PM Vishwakarma Yojana',
    icon: '🔨', ministry: 'Ministry of MSME',
    category: 'Artisans (18 trades)', type: 'Loan + Toolkit + Training',
    amount: '₹1L + ₹2L loan @ 5%, toolkit ₹15K',
    portal: 'https://www.pmvishwakarma.gov.in',
  },
};

/* Cached live documents (chunk_id prefix -> full text) loaded from /documents. */
window.SCHEME_DOCS = {};

async function loadSchemeDocs() {
  if (Object.keys(window.SCHEME_DOCS).length) return window.SCHEME_DOCS;
  try {
    const res = await fetch('/documents');
    const data = await res.json();
    const docs = {};
    (data.documents || []).forEach(d => {
      const base = (d.chunk_id || '').split('#')[0];
      if (base && !docs[base]) docs[base] = d.text || '';
    });
    window.SCHEME_DOCS = docs;
    return docs;
  } catch (e) {
    return window.SCHEME_DOCS;
  }
}

function schemeByChunkId(chunkId) {
  const base = (chunkId || '').split('#')[0];
  return window.SCHEME_CATALOG[base] || null;
}

/* Resolve a scheme base/chunk-prefix from either a slug (legacy ?id=), a
   chunk prefix (scheme_...), or in-catalog slug/alias. Returns the prefix key. */
function resolveSchemeKey(value) {
  const v = String(value || '').trim();
  if (!v || v === 'pmegp') return 'scheme_pmegp_v1';
  if (window.SCHEME_CATALOG[v]) return v;
  const entry = Object.keys(window.SCHEME_CATALOG).find(k =>
    window.SCHEME_CATALOG[k].id === v ||
    (window.SCHEME_CATALOG[k].aliases || []).includes(v)
  );
  return entry || null;
}
