/* ═══════════ SAHAYAK SITE CONFIG & AUTH ═══════════
   Supabase integration for login, session, and Q&A history.

   Kept as a separate file so every inner page can pull the auth state
   without repeating config. Also holds a tiny localStorage profile store
   used by the chat page so the dashboard can render a real profile. */
(function (window) {
  const SUPABASE_URL = 'https://tyolutcefkrlyddlxmob.supabase.co';
  const SUPABASE_ANON_KEY = 'sb_publishable_tiJBbLZVSr4NR3EXxMjJuA_9Vs2MeoN';

  let supabase = window.supabase
    ? window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
    : null;

  const sessionKey = 'sa_session';
  const profileKey = 'sa_profile';
  const historyKey = 'sa_history';

  /* ───────── Session helpers ───────── */
  async function initSession() {
    if (!supabase) return null;
    let session = await supabase.auth.getSession();
    if (!session.data.session && loadLocalSession()) {
      session = loadLocalSession();
    }
    return session.data.session || session || null;
  }

  function currentUser() {
    try {
      const s = window.localStorage.getItem(sessionKey);
      if (!s) return null;
      return JSON.parse(s).user || null;
    } catch (e) { return null; }
  }

  function loadLocalSession() {
    try {
      const s = window.localStorage.getItem(sessionKey);
      return s ? { data: { session: JSON.parse(s) } } : null;
    } catch (e) { return null; }
  }

  function saveSession(session) {
    if (session) window.localStorage.setItem(sessionKey, JSON.stringify(session));
    else window.localStorage.removeItem(sessionKey);
  }

  /* ───────── Profile store ───────── */
  function getProfile() {
    try { return JSON.parse(window.localStorage.getItem(profileKey)) || {}; }
    catch (e) { return {}; }
  }
  function setProfile(p) { window.localStorage.setItem(profileKey, JSON.stringify(p)); }
  function updateProfile(obj) { setProfile(Object.assign(getProfile(), obj)); }

  /* ───────── History (dashboard fallback) ───────── */
  function getHistory() {
    try { return JSON.parse(window.localStorage.getItem(historyKey)) || []; }
    catch (e) { return []; }
  }

  window.Sahayak = {
    supabase, SUPABASE_URL, SUPABASE_ANON_KEY,
    initSession, currentUser, saveSession,
    getProfile, setProfile, updateProfile,
    getHistory,
  };
})(window);