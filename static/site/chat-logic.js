/* ═══════════ SAHAYAK CHAT LOGIC ═══════════
   Drives the real RAG chatbot on the website. Calls the FastAPI /answer
   endpoint (real scheme documents, cited), tracks a lightweight profile
   from keywords in the user's messages, supports two demo commands, and
   refreshes the profile panel + source count. Question/answer pairs are
   logged server-side when /answer is called.

   Demo commands:
     /demo1  -> tailor needing ~2 lakh for machines (SC, rural)
     /demo2  -> street vendor needing small working capital (OBC, urban)
*/

(function () {
  const canvas = document.getElementById('chatCanvas');
  const input = document.getElementById('chatInput');
  const API = (window.location.protocol === 'https:' ? '' : '') + '/answer';

  let cited = [];
  let lastAnswer = '';
  let lastQuery = '';
  let msgCount = 0;

  /* ───────── small DOM helpers ───────── */
  function appendMsg(role, html) {
    const d = document.createElement('div');
    d.className = 'chat-msg ' + role;
    const avatar = role === 'bot' ? '🤖' : '🙂';
    d.innerHTML = `<div class="msg-avatar">${avatar}</div><div class="msg-bubble">${html}</div>`;
    canvas.appendChild(d);
    canvas.scrollTop = canvas.scrollHeight;
    msgCount++;
    return d;
  }
  function showTyping() {
    const d = document.createElement('div');
    d.className = 'chat-msg bot';
    d.innerHTML = `<div class="msg-avatar">🤖</div><div class="msg-bubble"><div class="typing-dots"><span></span><span></span><span></span></div></div>`;
    canvas.appendChild(d); canvas.scrollTop = canvas.scrollHeight;
    return d;
  }
  function esc(s) {
    return String(s || '').replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }
  function renderMessageWithCitations(text) {
    return esc(text)
      .replace(/\[([A-Za-z0-9_.\-]+)\]/g, '<span class="qr-chip" style="cursor:default;margin:0 3px;">$1</span>');
  }

  /* ───────── smart follow-up suggestions ───────── */
  function suggestFollowUp(profile) {
    const missing = [];
    if (!profile.category) missing.push('जाति वर्ग (SC/ST/OBC/General)');
    if (!profile.business) missing.push('व्यवसाय का प्रकार');
    if (!profile.amount) missing.push('कितनी राशि चाहिए');
    if (!profile.location) missing.push('गाँव या शहर');
    if (!profile.stage) missing.push('नया या पुराना व्यवसाय');

    if (missing.length > 0) {
      return '<div style="margin-top:10px;padding:10px;border-radius:10px;background:#FBF6EF;border:1px solid var(--border);font-size:13px;">' +
        '💡 <b>अभी पूरी जानकारी नहीं मिली।</b> बताइए: ' + missing.slice(0, 3).join(', ') + '?<br>' +
        '<span style="color:var(--muted);">ताकि मैं आपके लिए सबसे सही योजना ढूँढ सकूँ।</span></div>';
    }
    return '';
  }

  function smartSuggestions() {
    const tips = [
      '🔍 <b>Try asking:</b> "मुझे ₹2 लाख का लोन चाहिए, SC हूँ, गाँव से"',
      '🔍 <b>Try asking:</b> "सिलाई मशीन के लिए सरकारी योजना बताओ"',
      '🔍 <b>Try asking:</b> "Street vendor के लिए क्या मिलेगा?"',
      '🔍 <b>Try asking:</b> "महिला उद्यमी के लिए लोन चाहिए"',
    ];
    return tips[Math.floor(Math.random() * tips.length)];
  }

  /* ───────── profile extraction from plain text ───────── */
  function extractProfile(text) {
    const t = (text || '').toLowerCase();
    const p = window.Sahayak.getProfile();
    let changed = [];

    // category
    if (/(\bsc\b|\bscheduled caste\b|अनुसूचित जाति|अनु\.?\s*जाति)/.test(t)) { p.category = 'SC'; changed.push('category'); }
    if (/(\bobc\b|अन्य पिछड़ा|obc|पिछड़ा वर्ग)/.test(t)) { p.category = 'OBC'; changed.push('category'); }
    if (/(\bst\b|\bscheduled tribe\b|अनुसूचित जनजाति)/.test(t)) { p.category = 'ST'; changed.push('category'); }
    if (/(minority|अल्पसंख्यक|muslim|मुस्लिम|sikh|सिख|christian|ईसाई)/.test(t)) { p.category = 'Minority'; changed.push('category'); }
    if (/(general|सामान्य)/.test(t)) { p.category = 'General'; changed.push('category'); }
    if (/(महिला|woman|women|female|महिला|बेटी|बहन|wife|पत्नी)/.test(t)) { p.category = 'Woman'; changed.push('category'); }
    if (/(pwd|disability|विकलांग|दिव्यांग)/.test(t)) { p.category = 'PwD'; changed.push('category'); }

    // business type
    if (/(सिलाई|tailor|sewing|कपड़े|cloth|बुटीक|boutique)/.test(t)) { p.business = 'Tailoring'; changed.push('business'); }
    if (/(गाड़ी|ठेला|thela|vendor|रोडी|street vend|सब्ज़ी|vegetable)/.test(t)) { p.business = 'Street Vending'; changed.push('business'); }
    if (/(दुकान|shop|retail|किराना|general store)/.test(t)) { p.business = 'Retail Shop'; changed.push('business'); }
    if (/(खेती|farm|agriculture|किसान|crop|फ़सल)/.test(t)) { p.business = 'Agriculture'; changed.push('business'); }
    if (/(मैन्युफैक्चर|manufactur|उद्योग|factory|कारखाना)/.test(t)) { p.business = 'Manufacturing'; changed.push('business'); }
    if (/(डेयरी|dairy|दूध|milk)/.test(t)) { p.business = 'Dairy'; changed.push('business'); }
    if (/(मछली|fish|fishery|मत्स्य)/.test(t)) { p.business = 'Fishery'; changed.push('business'); }

    // stage
    if (/(नया|new bus|start|first time|शुरू|पहली बार|fresh)/.test(t)) { p.stage = 'New venture'; changed.push('stage'); }
    if (/(बढ़ाना|expand|grow|established|चल रहा|existing|running|पुराना)/.test(t)) { p.stage = 'Existing / expanding'; changed.push('stage'); }

    // amount — handle ₹ symbol too
    const amt = t.match(/(\d+(?:\.\d+)?)\s*(लाख|lakh|lac)/);
    if (amt) { p.amount = amt[1] + ' lakh'; changed.push('amount'); }
    const amtT = t.match(/(\d+(?:\.\d+)?)\s*(हज़ार|thousand|k\b)/);
    if (amtT) { p.amount = amtT[1] + ' thousand'; changed.push('amount'); }
    const amtR = t.match(/(?:₹|rs\.?|inr)\s*(\d+(?:\.\d+)?)/);
    if (amtR && !amt && !amtT) {
      const v = parseFloat(amtR[1]);
      if (v >= 100000) p.amount = (v / 100000) + ' lakh';
      else p.amount = v + ' thousand';
      changed.push('amount');
    }

    // location
    if (/(गांव|गाँव|rural|देहात|village)/.test(t)) { p.location = 'Rural'; changed.push('location'); }
    if (/(शहर|urban|city|महानगर)/.test(t)) { p.location = 'Urban'; changed.push('location'); }

    window.Sahayak.setProfile(p);
    refreshProfile();

    // Notify user if profile changed
    if (changed.length > 0 && msgCount > 2) {
      const fieldNames = { category: 'जाति वर्ग', business: 'व्यवसाय', stage: 'स्टेज', amount: 'राशि', location: 'स्थान' };
      const updated = [...new Set(changed)].map(f => fieldNames[f] || f).join(', ');
      appendMsg('bot', '📝 <b>Profile updated:</b> ' + updated + ' — dropdowns updated automatically.');
    }

    return p;
  }

  function buildProfilePayload() {
    const p = window.Sahayak.getProfile();
    const payload = {};
    if (p.category) payload.category = p.category;
    if (p.stage) payload.business_stage = p.stage;
    if (p.business) payload.business_type = p.business;
    if (p.amount) payload.loan_amount = p.amount;
    if (p.location) payload.location = p.location;
    return Object.keys(payload).length ? payload : null;
  }

  function refreshProfile() {
    const p = window.Sahayak.getProfile();
    const setVal = (id, v) => { const el = document.getElementById(id); if (el && el.tagName === 'SELECT') el.value = v || ''; };
    setVal('pCategory', p.category);
    setVal('pBusiness', p.business);
    setVal('pStage', p.stage);
    setVal('pAmount', p.amount);
    setVal('pLocation', p.location);

    const u = window.Sahayak.currentUser();
    const emailEl = document.getElementById('profileEmail');
    if (emailEl) emailEl.textContent = u ? (u.email || 'Signed in') : 'Not signed in (anonymous)';
  }

  function updateProfileField(key, value) {
    const p = window.Sahayak.getProfile();
    if (value) p[key] = value; else delete p[key];
    window.Sahayak.setProfile(p);
    refreshProfile();
  }

  function recordCited(ids) {
    ids.forEach(id => { if (!cited.includes(id)) cited.push(id); });
    const n = document.getElementById('matchCount');
    const detail = document.getElementById('matchDetail');
    if (n) n.textContent = cited.length;
    if (detail) detail.textContent = cited.length ? cited.join(', ') : 'Ask a question to begin';
  }

  /* ───────── send to backend ───────── */
  async function ask(query) {
    const typing = showTyping();
    const user = window.Sahayak.currentUser();
    lastQuery = query;
    try { window.localStorage.setItem('sa_last_query', query); } catch (e) {}
    const body = {
      query,
      profile: buildProfilePayload(),
      user_id: user ? user.id : null,
      user_email: user ? user.email : null,
    };

    try {
      const res = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      typing.remove();

      if (!res.ok) {
        appendMsg('bot', '<b>⚠️ कुछ गड़बड़ हुई।</b><br>' + esc(data.detail || 'Please try again.') +
          '<br><span style="font-size:12px;color:var(--muted);cursor:pointer;" onclick="send()">🔄 Tap to retry</span>');
        return;
      }

      let html = renderMessageWithCitations(data.text || 'No answer returned.');
      lastAnswer = data.text || '';
      if (data.citations && data.citations.length) recordCited(data.citations);

      // needs_prerequisites flag
      if (data.needs_prerequisites) {
        html += suggestFollowUp(window.Sahayak.getProfile());
      }

      // Add smart suggestion after first answer
      if (msgCount <= 3) {
        html += '<div style="margin-top:8px;font-size:12px;color:var(--muted);">' + smartSuggestions() + '</div>';
      }

      appendMsg('bot', html);
      extractProfile(query);
    } catch (e) {
      typing.remove();
      appendMsg('bot', '⚠️ <b>Network error</b> — backend चालू है?<br>' +
        '<span style="font-size:12px;color:var(--muted);">Make sure the server is running on localhost:8000</span>');
    }
  }

  /* ───────── auto-generate Results / Dashboard / Documentation ───────── */
  async function finish() {
    if (!lastAnswer) {
      appendMsg('bot', '💡 पहले एक सवाल पूछिए ताकि मैं आपकी योजनाएँ तैयार कर सकूँ।<br><b>Example:</b> "मुझे ₹2 लाख का लोन चाहिए, SC हूँ"');
      return;
    }

    const p = window.Sahayak.getProfile();
    const missing = [];
    if (!p.category) missing.push('category');
    if (!p.business) missing.push('business');
    if (!p.amount) missing.push('amount');

    if (missing.length > 1) {
      appendMsg('bot', '⚠️ <b>Profile अधूरा है।</b> कृपया ड्रॉपडाउन से ' + missing.join(', ') + ' भर दें, फिर "Finish" दबाएँ।');
      return;
    }

    const user = window.Sahayak.currentUser();
    const btn = document.getElementById('finishBtn');
    if (btn) { btn.disabled = true; btn.innerHTML = '⏳ Generating…'; }

    // Show progress messages
    const progressMsg = appendMsg('bot', '🔄 <b>Step 1/3:</b> Analyzing your profile and question…');

    const body = {
      query: lastQuery || (() => { try { return window.localStorage.getItem('sa_last_query'); } catch (e) { return ''; } })(),
      answer: lastAnswer,
      citations: cited,
      profile: buildProfilePayload(),
      user_id: user ? user.id : null,
      user_email: user ? user.email : null,
      full_name: (user && user.user_metadata && user.user_metadata.full_name) || null,
    };

    try {
      // Update progress
      setTimeout(() => { progressMsg.querySelector('.msg-bubble').innerHTML = '🔄 <b>Step 2/3:</b> Matching schemes and generating recommendations…'; }, 2000);

      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Generation failed');

      progressMsg.querySelector('.msg-bubble').innerHTML = '🔄 <b>Step 3/3:</b> Building your personalized report…';

      try {
        window.localStorage.setItem('sa_generated', JSON.stringify(data));
        window.localStorage.setItem('sa_session_generated', '1');
      } catch (e) {}

      setTimeout(() => {
        progressMsg.querySelector('.msg-bubble').innerHTML = '✅ <b>आपकी रिपोर्ट तैयार है!</b> ' +
          'Matched schemes, document checklist, और next steps सब बन गया। Redirecting…';
        setTimeout(() => { location.href = 'results.html'; }, 1200);
      }, 500);
    } catch (e) {
      if (btn) { btn.disabled = false; btn.innerHTML = '✓ Finish — Get My Results'; }
      progressMsg.querySelector('.msg-bubble').innerHTML = '⚠️ <b>रिपोर्ट बनाने में समस्या:</b> ' + esc(e.message || 'please retry') +
        '<br><span style="font-size:12px;color:var(--muted);cursor:pointer;" onclick="finishSession()">🔄 Tap to retry</span>';
    }
  }

  /* ───────── clear chat ───────── */
  function clearChat() {
    if (msgCount === 0) return;
    canvas.innerHTML = `
      <div class="chat-msg bot">
        <div class="msg-avatar">🤖</div>
        <div class="msg-bubble">Chat cleared. नमस्ते! 🙏 बताइए आप क्या करना चाहते हैं?<br/>
        <span style="font-size:12.5px;color:var(--muted);">Hello! Tell me your business goal and I'll match you with the right schemes.</span></div>
      </div>`;
    cited = []; lastAnswer = ''; lastQuery = ''; msgCount = 0;
    const n = document.getElementById('matchCount');
    const detail = document.getElementById('matchDetail');
    if (n) n.textContent = '0';
    if (detail) detail.textContent = 'Ask a question to begin';
  }

  /* ───────── two demo commands ───────── */
  const DEMOS = {
    demo1: {
      intro: [
        '▶ <b>Demo 1 · सिलाई व्यवसाय</b>',
        'प्रोफ़ाइल: जाति — SC · व्यवसाय — Tailoring · नया व्यवसाय · 2 लाख · Rural',
        'प्रश्न: मुझे 3 सिलाई मशीन और कपड़ा खरीदने के लिए 2 लाख रुपये चाहिए। मैं SC हूँ, गाँव में पहली बार व्यवसाय शुरू कर रहा हूँ। कौन सी सरकारी योजना मदद करेगी?',
      ],
      profile: { category:'SC', business:'Tailoring', stage:'New venture', amount:'2 lakh', location:'Rural' },
      query: 'मुझे 3 सिलाई मशीन और कपड़ा खरीदने के लिए 2 लाख रुपये चाहिए। मैं SC हूँ, गाँव में पहली बार व्यवसाय शुरू कर रहा हूँ। कौन सी सरकारी योजना मदद करेगी?',
    },
    demo2: {
      intro: [
        '▶ <b>Demo 2 · Street Vendor</b>',
        'प्रोफ़ाइल: जाति — OBC · व्यवसाय — Street Vending · 10,000 रुपये · Urban',
        'प्रश्न: मेरे पास सब्ज़ी की गाड़ी है। काम बढ़ाने के लिए 10 हजार का working capital चाहिए। मैं OBC हूँ, शहर में हूँ। कोई योजना मिलेगी?',
      ],
      profile: { category:'OBC', business:'Street Vending', stage:'Existing / expanding', amount:'10 thousand', location:'Urban' },
      query: 'मेरे पास सब्ज़ी की गाड़ी है। काम बढ़ाने के लिए 10 हजार का working capital चाहिए। मैं OBC हूँ, शहर में हूँ। कोई योजना मिलेगी?',
    },
  };

  async function runDemo(name) {
    const d = DEMOS[name];
    if (!d) return;
    window.Sahayak.setProfile(Object.assign(window.Sahayak.getProfile(), d.profile));
    refreshProfile();
    d.intro.forEach(line => appendMsg('bot', line));
    const u = appendMsg('user', d.query);
    u.scrollIntoView();
    await ask(d.query);
  }

  function send() {
    const v = input.value.trim();
    if (!v) return;
    if (v === '/demo1' || v === '/demo2') { runDemo(v.slice(1)); input.value = ''; return; }
    if (v === '/clear' || v === '/reset') { clearChat(); input.value = ''; return; }
    appendMsg('user', v); input.value = '';
    ask(v);
  }

  // expose to inline onclick handlers
  window.send = send;
  window.runDemo = runDemo;
  window.finishSession = finish;
  window.updateProfile = updateProfileField;
  window.clearChat = clearChat;

  // init on load
  document.addEventListener('DOMContentLoaded', () => {
    refreshProfile();
    window.Sahayak.initSession().then(() => refreshProfile());
  });
})();
