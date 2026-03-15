/* ══════════════════════════════════════════════════════════════
   GoRiyadh  app.js  v4
   Multi-page SPA — Home · Chat · Explore · Map · Plan My Day
   ══════════════════════════════════════════════════════════════ */
'use strict';

// ── Image pools ──────────────────────────────────────────────────
const IMG = {
  hotel: [
    'photo-1566073771259-6a8506099945','photo-1551882547-ff40c63fe2e2',
    'photo-1520250497591-112f2f40a3f4','photo-1578683016700-83de6e1b0fa8',
    'photo-1445019980597-93fa8acb246c','photo-1611892440504-42a792e24d32',
    'photo-1582719478239-2ec8ee576d72','photo-1618773928121-c32242e63f39',
    'photo-1542314831-068cd1dbfeeb',  'photo-1571896349842-33c89424de2d',
    'photo-1564501049412-61c2a3083791','photo-1455587734955-081b22074882',
  ],
  restaurant: [
    'photo-1414235077428-338989a2e8c0','photo-1517248135467-4c7edcad34c4',
    'photo-1559339352-11d035aa65de', 'photo-1565299624946-b28f40a0ae38',
    'photo-1555396273-367ea4eb4db5', 'photo-1504674900247-0877df9cc836',
    'photo-1533777857889-4be7c70b33f7','photo-1540189549336-e6e99eb4b951',
    'photo-1567620905732-2d1ec7ab7445','photo-1484723091739-30a097e8f929',
    'photo-1476224203421-9ac39bcb3327','photo-1546069901-ba9599a7e63c',
    'photo-1544025162-d76694265947', 'photo-1529193591184-b1d58069ecdd',
    'photo-1512621776951-a57141f2eefd','photo-1534422298391-e4f8c172dddb',
    'photo-1481931098730-318b6f776db0','photo-1498654896293-37aacf113fd9',
    'photo-1455619452474-d2be8b1e70cd','photo-1626082927389-6cd097cdc6ec',
    'photo-1547592180-85f173990554', 'photo-1493770348161-369560ae357d',
    'photo-1432139555190-58524dae6a55','photo-1504544750208-dc0358ad04e3',
  ],
  cafe: [
    'photo-1501339847302-ac426a4a7cbb','photo-1495474472287-4d71bcdd2085',
    'photo-1554118811-1e0d58224f24', 'photo-1453614512568-c4024d13c247',
    'photo-1509042239860-f550ce710b93','photo-1600093463592-8e6aae3c3c01',
    'photo-1445116572660-ac56f2e31aaf','photo-1572119865084-43c285814d63',
    'photo-1521302080334-4bebac2763a6','photo-1559496417-e7f25cb247f3',
    'photo-1461023058943-07fcbe16d735','photo-1507133750040-4a8f57021571',
    'photo-1442512595331-e89e73853f31','photo-1511537190424-bbbab87ac5eb',
    'photo-1534040385115-33dcb3acba5b','photo-1516486392848-8b67ef89f981',
    'photo-1567532939604-b6b5b0db2604','photo-1558618666-fcd25c85cd64',
    'photo-1497515114629-f71d768fd07c','photo-1606791405792-1004f1718d0c',
    'photo-1610889556528-9a770e32642f','photo-1544787219-7f47ccb76574',
    'photo-1529543544282-ea669407fca3','photo-1525610553991-2bede1a236e2',
  ],
};

// ── District centroids ───────────────────────────────────────────
const DISTRICT_COORDS = {
  'Al Olaya':[24.6927,46.6810],'Al Nakheel':[24.8020,46.6470],
  'North Riyadh':[24.8200,46.6500],'Al Malaz':[24.6770,46.7500],
  'Al Muruj':[24.7570,46.6570],'Al Sulaimaniyah':[24.6910,46.6740],
  'Al Rawdah':[24.7050,46.7200],'Al Hamra':[24.7210,46.7220],
  'Al Aqeeq':[24.7970,46.6160],'Al Naseem':[24.6580,46.8050],
  'South Riyadh':[24.5800,46.7200],'Central Riyadh':[24.6880,46.7220],
  'East Riyadh':[24.6800,46.7800],'West Riyadh':[24.7000,46.6000],
  'Al Yasmin':[24.8350,46.6380],'Al Sahafah':[24.7700,46.6450],
  'Al Rabwah':[24.7230,46.6900],'Al Narjis':[24.8500,46.6200],
  'Al Wurud':[24.7150,46.6830],'Al Izdihar':[24.7480,46.7680],
  'Riyadh':[24.7136,46.6753],'Al Khabra':[24.7400,46.7000],
  'KAFD':[24.7740,46.6400],'King Abdullah':[24.7800,46.6200],
  'Al Diriyah':[24.7340,46.5740],'Al Salam':[24.6300,46.7700],
  'Al Shifa':[24.6150,46.7100],'Al Masif':[24.8050,46.6380],
  'Al Arid':[24.8600,46.6500],'Al Qirawan':[24.8700,46.6350],
};
function districtCoords(d) {
  if (!d) return DISTRICT_COORDS['Riyadh'];
  if (DISTRICT_COORDS[d]) return DISTRICT_COORDS[d];
  const k = Object.keys(DISTRICT_COORDS).find(k =>
    d.toLowerCase().includes(k.toLowerCase()) || k.toLowerCase().includes(d.toLowerCase()));
  return DISTRICT_COORDS[k] || DISTRICT_COORDS['Riyadh'];
}

// ── Translations ─────────────────────────────────────────────────
const TRANS = {
  en: {
    home:'Home', chat:'Chat', explore:'Explore', map:'Map', plan:'Plan My Day',
    langBtn:'العربية',
    hEyebrow:'AI-Powered Travel Guide · Riyadh, Saudi Arabia',
    hTitle:'Discover Riyadh',
    hAccent:'your way',
    hSub:'Personalised recommendations for cafes, restaurants & hotels — tailored to your taste and budget.',
    searchPh:'Search cafes, restaurants, hotels…',
    searchBtn:'Search',
    pillAll:'All', pillCafe:'Cafes', pillRest:'Restaurants', pillHotel:'Hotels',
    statCafesLbl:'Cafes', statRestsLbl:'Restaurants', statHotelsLbl:'Hotels', statAiLbl:'Smart Engine',
    featTitle:'Everything you need to explore Riyadh',
    feat1:'Smart Chat',      feat1d:'Ask anything in natural language and get personalised recommendations instantly.',
    feat2:'Explore Places',  feat2d:'Browse thousands of cafes, restaurants, and hotels with smart filters.',
    feat3:'Interactive Map', feat3d:'Visualise all places across Riyadh\'s districts on a live map.',
    feat4:'Day Planner',     feat4d:'Generate a full day itinerary matched to your exact budget.',
    newChatBtn:'✦ New Chat',
    chatSidebarH:'Try asking',
    suggestions:['Best cafes for studying','Fine dining restaurants','Budget-friendly hotels','Family-friendly restaurants','Specialty coffee shops','Luxury hotel recommendations','Cafes open late at night','Best rated restaurants'],
    chatWelcomeTitle:'GoRiyadh Assistant',
    chatWelcomeSub:'Ask me anything about Riyadh — cafes, restaurants, hotels, or help planning your visit.',
    chatPh:'Ask about cafes, restaurants, hotels…',
    exploreTitle:'Explore Riyadh', exploreSub:'Browse the best places across the city',
    tabCafe:'Cafes', tabRest:'Restaurants', tabHotel:'Hotels',
    filterHeading:'Filters', fRatingLbl:'Rating', fPriceLbl:'Price level', fDistrictLbl:'District',
    fRatingOpts:['Any rating','4★ and above','4.5★ and above'],
    fPriceOpts:['Any price','Budget','Moderate','Upscale'],
    fDistrictPh:'e.g. Al Olaya',
    applyBtn:'Apply', resetBtn:'Reset', loadMoreBtn:'Load more',
    mapPageTitle:'Map', mapAll:'All', mapCafe:'Cafes', mapRest:'Restaurants', mapHotel:'Hotels',
    planTitle:'Plan My Day',
    planSub:'Enter your budget and we\'ll generate multiple personalised day plans.',
    budgetLabel:'Daily Budget (SAR)', budgetPh:'e.g. 500', genBtn:'Generate Plans',
    planEmptyTxt:'Enter your budget above to generate personalised day plans.',
    periodMorning:'Morning', periodAfternoon:'Afternoon', periodEvening:'Evening',
    periodIcons:{ Morning:'☀️', Afternoon:'🍽️', Evening:'🌙' },
    estCost:'Estimated total',
    noResults:'No matching places found.',
    clearResults:'✕ Clear',
    connError:'Connection error — is the server running?',
    loading:'Loading…',
    approxPrice: n => `~${Math.round(n/50)*50} SAR`,
    approxNight: n => `~${Math.round(n/100)*100} SAR/night`,
  },
  ar: {
    home:'الرئيسية', chat:'المساعد', explore:'استكشاف', map:'الخريطة', plan:'خطط يومي',
    langBtn:'English',
    hEyebrow:'دليل السفر الذكي · الرياض، المملكة العربية السعودية',
    hTitle:'اكتشف الرياض',
    hAccent:'بأسلوبك',
    hSub:'توصيات مخصصة للمقاهي والمطاعم والفنادق — تتناسب مع ذوقك وميزانيتك.',
    searchPh:'ابحث عن مقاهي، مطاعم، فنادق…',
    searchBtn:'بحث',
    pillAll:'الكل', pillCafe:'مقاهٍ', pillRest:'مطاعم', pillHotel:'فنادق',
    statCafesLbl:'مقهى', statRestsLbl:'مطعم', statHotelsLbl:'فندق', statAiLbl:'محرك ذكي',
    featTitle:'كل ما تحتاجه لاستكشاف الرياض',
    feat1:'محادثة ذكية',   feat1d:'اسأل بلغة طبيعية واحصل على توصيات مخصصة فوراً.',
    feat2:'استكشاف الأماكن', feat2d:'تصفح آلاف المقاهي والمطاعم والفنادق بفلاتر ذكية.',
    feat3:'خريطة تفاعلية', feat3d:'استعرض جميع الأماكن عبر أحياء الرياض على خريطة مباشرة.',
    feat4:'مخطط اليوم',    feat4d:'أنشئ جدول يوم كامل يتناسب مع ميزانيتك بالضبط.',
    newChatBtn:'✦ محادثة جديدة',
    chatSidebarH:'جرّب أن تسأل',
    suggestions:['أفضل مقاهٍ للدراسة','مطاعم راقية للعشاء','فنادق مناسبة للميزانية','مطاعم عائلية','محلات قهوة متخصصة','توصيات فنادق فاخرة','مقاهٍ تفتح حتى وقت متأخر','أعلى المطاعم تقييماً'],
    chatWelcomeTitle:'مساعد GoRiyadh',
    chatWelcomeSub:'اسألني أي شيء عن الرياض — مقاهٍ أو مطاعم أو فنادق أو مساعدة في التخطيط.',
    chatPh:'اسأل عن مقاهٍ، مطاعم، فنادق…',
    exploreTitle:'استكشف الرياض', exploreSub:'تصفح أفضل الأماكن في المدينة',
    tabCafe:'مقاهٍ', tabRest:'مطاعم', tabHotel:'فنادق',
    filterHeading:'فلاتر', fRatingLbl:'التقييم', fPriceLbl:'مستوى السعر', fDistrictLbl:'الحي',
    fRatingOpts:['أي تقييم','4 نجوم فأكثر','4.5 نجوم فأكثر'],
    fPriceOpts:['أي سعر','اقتصادي','متوسط','فاخر'],
    fDistrictPh:'مثال: العليا',
    applyBtn:'تطبيق', resetBtn:'إعادة تعيين', loadMoreBtn:'تحميل المزيد',
    mapPageTitle:'الخريطة', mapAll:'الكل', mapCafe:'مقاهٍ', mapRest:'مطاعم', mapHotel:'فنادق',
    planTitle:'خطط يومي',
    planSub:'أدخل ميزانيتك وسنُنشئ لك خطط يومية متعددة.',
    budgetLabel:'الميزانية اليومية (ريال)', budgetPh:'مثال: 500', genBtn:'إنشاء الخطط',
    planEmptyTxt:'أدخل ميزانيتك أعلاه لإنشاء خطط مخصصة.',
    periodMorning:'الصباح', periodAfternoon:'الظهيرة', periodEvening:'المساء',
    periodIcons:{ Morning:'☀️', Afternoon:'🍽️', Evening:'🌙' },
    estCost:'التكلفة التقديرية',
    noResults:'لم يتم العثور على أماكن مطابقة.',
    clearResults:'✕ مسح',
    connError:'خطأ في الاتصال — هل الخادم يعمل؟',
    loading:'جارٍ التحميل…',
    approxPrice: n => `~${Math.round(n/50)*50} ريال`,
    approxNight: n => `~${Math.round(n/100)*100} ريال/ليلة`,
  },
};

// ── Global state ─────────────────────────────────────────────────
const G = {
  lang: 'en',
  heroPillType: '',
  exploreType: 'cafe',
  exploreLoaded: false,
  exploreDocs: [],
  exploreOffset: 0,
  mapInited: false,
  mapMarkers: null,
  map: null,
  mapType: '',
  plans: [],
  planIdx: 0,
  chatHistory: [],
  docsMap: {},
  modalMap: null,
  modalMapMarkers: null,
  modalDoc: null,
  toastTimer: null,
};

let PLACE_IMGS = {};
async function loadPlaceImages() {
  try {
    const r = await fetch('/static/place_images.json');
    if (r.ok) PLACE_IMGS = await r.json();
  } catch (_) {}
}

// ── Helpers ──────────────────────────────────────────────────────
function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function $(s)  { return document.querySelector(s); }
function $$(s) { return document.querySelectorAll(s); }
function nameHash(name) { let h=0; for(let i=0;i<name.length;i++) h=(h*31+name.charCodeAt(i))>>>0; return h; }
function poolImg(name, type) {
  const pool = IMG[type] || IMG.cafe;
  return `https://images.unsplash.com/${pool[nameHash(name)%pool.length]}?auto=format&fit=crop&w=700&q=80`;
}
function bestImg(name, type) { return PLACE_IMGS[name] || poolImg(name, type); }

function guardImg(img) {
  img.addEventListener('load', function() {
    if (this.naturalWidth < 50 || this.naturalHeight < 50) {
      this.src = poolImg(this.alt || '', this.dataset.type || 'cafe');
      this.onerror = null;
    }
  }, { once: true });
}

const VALID_PRICES = new Set(['Cheap','Moderate','Expensive','Very Expensive']);
function formatPrice(doc) {
  const T = TRANS[G.lang];
  const { type, price } = doc;
  if (!price || price === 'nan' || (typeof price === 'number' && isNaN(price))) return null;
  if (type === 'hotel' && typeof price === 'number') return T.approxNight(price);
  if (type === 'hotel' && typeof price === 'string') {
    const n = parseFloat(price);
    return isNaN(n) ? null : T.approxNight(n);
  }
  if (VALID_PRICES.has(price)) {
    const map = { Cheap:T.approxPrice(50), Moderate:T.approxPrice(100), Expensive:T.approxPrice(200), 'Very Expensive':T.approxPrice(350) };
    return map[price];
  }
  const n = parseFloat(price);
  if (!isNaN(n) && n > 0) return type === 'hotel' ? T.approxNight(n) : T.approxPrice(n);
  return null;
}

function approxStat(n) {
  if (n >= 2000) return '2,000+';
  if (n >= 1000) return '1,000+';
  if (n >= 500)  return '500+';
  if (n >= 100)  return '100+';
  if (n >= 50)   return '50+';
  return `${Math.floor(n/10)*10}+`;
}

// ── Place card HTML ──────────────────────────────────────────────
function imgTag(src, name, type, cls='', style='') {
  const fb = esc(poolImg(name, type));
  return `<img src="${esc(src)}" alt="${esc(name)}" data-type="${type}" onerror="this.onerror=null;this.src='${fb}'" loading="lazy"${cls?' class="'+cls+'"':''}${style?' style="'+style+'"':''}>`;
}

function placeCardHTML(doc) {
  G.docsMap[doc.name] = doc;
  const t = doc.type || 'cafe';
  const img = bestImg(doc.name, t);
  const rating = doc.rating ? `⭐ ${parseFloat(doc.rating).toFixed(1)}` : '';
  const district = doc.district ? `📍 ${doc.district}` : '';
  const price = formatPrice(doc);
  const showImg = t === 'hotel';
  return `
  <div class="place-card" data-place-name="${esc(doc.name)}" style="cursor:pointer">
    ${showImg ? `
    <div class="card-img-wrap">
      ${imgTag(img, doc.name, t)}
      <span class="card-type-badge badge-${t}">${esc(t)}</span>
    </div>` : ''}
    <div class="card-body">
      ${!showImg ? `<span class="card-type-badge-inline badge-${t}">${esc(t)}</span>` : ''}
      <div class="card-name">${esc(doc.name)}</div>
      <div class="card-meta">
        ${rating ? `<span class="card-rating">${rating}</span>` : ''}
        ${district ? `<span>${district}</span>` : ''}
      </div>
      ${price ? `<div class="card-price">${esc(price)}</div>` : ''}
      <button class="card-share-btn" data-share-name="${esc(doc.name)}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
        Share
      </button>
    </div>
  </div>`;
}

function chatPlaceCardHTML(doc) {
  const t = doc.type || 'cafe';
  const rating = doc.rating ? `⭐ ${parseFloat(doc.rating).toFixed(1)}` : '';
  const district = doc.district ? `· ${doc.district}` : '';
  return `
  <div class="chat-place-card">
    <div class="chat-card-body">
      <span class="card-type-badge-inline badge-${t}" style="margin-bottom:6px">${esc(t)}</span>
      <div class="chat-card-name">${esc(doc.name)}</div>
      <div class="chat-card-meta">${rating} ${district}</div>
    </div>
  </div>`;
}

// ── Router ───────────────────────────────────────────────────────
function navigate(page) {
  $$('.page').forEach(p => p.classList.remove('active'));
  $$('.nav-link, .nav-mobile-link').forEach(a => a.classList.toggle('active', a.dataset.nav === page));
  const el = $('#page-' + page);
  if (el) el.classList.add('active');
  window.scrollTo(0, 0);
  // close mobile menu
  const mob = $('#navMobile');
  if (mob) mob.style.display = 'none';
  // lazy init
  if (page === 'explore' && !G.exploreLoaded) { G.exploreLoaded = true; loadExplore('cafe'); }
  if (page === 'map' && !G.mapInited) { G.mapInited = true; setTimeout(initMap, 100); }
}

// ── Language ─────────────────────────────────────────────────────
function setLang(lang) {
  G.lang = lang;
  const html = document.documentElement;
  html.lang = lang;
  html.dir  = lang === 'ar' ? 'rtl' : 'ltr';
  const T = TRANS[lang];

  // Nav
  $$('.nav-link, .nav-mobile-link').forEach(a => { a.textContent = T[a.dataset.nav] || a.textContent; });
  $('#langBtn').textContent = T.langBtn;

  // Hero
  $('#hEyebrow').textContent = T.hEyebrow;
  $('#hTitle').childNodes[0].textContent = T.hTitle + '\n';
  document.querySelector('.hero-accent').textContent = T.hAccent;
  $('#hSub').textContent = T.hSub;
  $('#heroQ').placeholder = T.searchPh;
  $('#heroSearchBtn').textContent = T.searchBtn;
  $$('.hero-pill').forEach((p, i) => { p.textContent = [T.pillAll,T.pillCafe,T.pillRest,T.pillHotel][i] || p.textContent; });

  // Stats
  $('#statCafesLbl').textContent = T.statCafesLbl;
  $('#statRestsLbl').textContent  = T.statRestsLbl;
  $('#statHotelsLbl').textContent = T.statHotelsLbl;
  $('#statAiLbl').textContent     = T.statAiLbl;

  // Features
  $('#featTitle').textContent = T.featTitle;
  ['feat1','feat2','feat3','feat4'].forEach(k => {
    const el = $('#'+k); if (el) el.textContent = T[k];
    const eld = $('#'+k+'d'); if (eld) eld.textContent = T[k+'d'];
  });

  // Chat
  $('#chatSidebarH').textContent = T.chatSidebarH;
  $('#chatSuggestions').querySelectorAll('.suggestion-btn').forEach((b,i) => { b.textContent = T.suggestions[i] || b.textContent; });
  $('#chatWelcomeTitle').textContent = T.chatWelcomeTitle;
  $('#chatWelcomeSub').textContent   = T.chatWelcomeSub;
  $('#chatInput').placeholder = T.chatPh;

  // Explore
  $('#exploreTitle').textContent = T.exploreTitle;
  $('#exploreSub').textContent   = T.exploreSub;
  $('#tabCafe') .closest('.tab-btn') ? null : null;
  $$('.tab-btn').forEach(b => {
    const map = { cafe: T.tabCafe, restaurant: T.tabRest, hotel: T.tabHotel };
    b.textContent = map[b.dataset.type] || b.textContent;
  });
  $('#filterHeading').textContent = T.filterHeading;
  $('#fRatingLbl').textContent    = T.fRatingLbl;
  $('#fPriceLbl').textContent     = T.fPriceLbl;
  $('#fDistrictLbl').textContent  = T.fDistrictLbl;
  $('#fDistrict').placeholder     = T.fDistrictPh;
  $('#applyFiltersBtn').textContent = T.applyBtn;
  $('#resetFiltersBtn').textContent = T.resetBtn;
  const lmb = $('#loadMoreBtn');
  if (lmb) lmb.textContent = T.loadMoreBtn;
  // filter selects
  const fRating = $('#fRating');
  if (fRating) fRating.querySelectorAll('option').forEach((o,i) => { o.textContent = T.fRatingOpts[i] || o.textContent; });
  const fPrice = $('#fPrice');
  if (fPrice) fPrice.querySelectorAll('option').forEach((o,i) => { o.textContent = T.fPriceOpts[i] || o.textContent; });

  // Map
  $('#mapPageTitle').textContent = T.mapPageTitle;
  $$('.map-chip').forEach((c,i) => { c.textContent = [T.mapAll,T.mapCafe,T.mapRest,T.mapHotel][i] || c.textContent; });

  // Plan
  $('#planTitle').textContent   = T.planTitle;
  $('#planSub').textContent     = T.planSub;
  $('#budgetLabel').textContent = T.budgetLabel;
  $('#budgetInput').placeholder = T.budgetPh;
  $('#genPlanBtn').textContent  = T.genBtn;
  $('#planEmptyTxt').textContent = T.planEmptyTxt;

  // Re-render cards if explore is loaded
  if (G.exploreLoaded && G.exploreDocs.length) renderExploreCards(G.exploreDocs);
  if (G.plans.length) renderPlan(G.planIdx);
}

// ── Stats ────────────────────────────────────────────────────────
async function loadStats() {
  try {
    const r = await fetch('/api/stats');
    if (!r.ok) return;
    const d = await r.json();
    if ($('#statCafes')) $('#statCafes').textContent = approxStat(d.cafes || 0);
    if ($('#statRests'))  $('#statRests').textContent  = approxStat(d.restaurants || 0);
    if ($('#statHotels')) $('#statHotels').textContent = approxStat(d.hotels || 0);
  } catch (_) {}
}

// ══════════════════════════════════════════════════════════════════
// HOME PAGE
// ══════════════════════════════════════════════════════════════════
function setupHome() {
  // Hero pill filter
  $$('.hero-pill').forEach(p => {
    p.addEventListener('click', () => {
      $$('.hero-pill').forEach(x => x.classList.remove('active'));
      p.classList.add('active');
      G.heroPillType = p.dataset.type;
    });
  });

  $('#heroSearchBtn').addEventListener('click', runHomeSearch);
  $('#heroQ').addEventListener('keydown', e => { if (e.key === 'Enter') runHomeSearch(); });
  $('#homeClearBtn').addEventListener('click', clearHomeResults);

  // Feature cards navigate
  $$('.feature-card[data-nav]').forEach(c => {
    c.addEventListener('click', () => navigate(c.dataset.nav));
  });
}

async function runHomeSearch() {
  const q = $('#heroQ').value.trim();
  if (!q) return;
  const btn = $('#heroSearchBtn');
  btn.textContent = '…';
  btn.disabled = true;
  try {
    const res = await fetch('/api/query', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ question:q, top_k:8, filter_type: G.heroPillType || null, arabic_mode: G.lang==='ar' }),
    });
    if (!res.ok) throw new Error('Server error');
    const data = await res.json();

    const sec = $('#homeResultsSec');
    sec.style.display = 'block';
    const T = TRANS[G.lang];

    // Answer
    const ansBox = $('#homeAnswer');
    if (data.answer) { ansBox.textContent = data.answer; ansBox.style.display='block'; }
    else ansBox.style.display='none';

    // Title
    $('#homeResultsTitle').textContent = q;

    // Cards
    const cards = $('#homeCards');
    if (data.docs && data.docs.length) {
      cards.innerHTML = data.docs.map(d => placeCardHTML(d)).join('');
      cards.querySelectorAll('img').forEach(guardImg);
    } else {
      cards.innerHTML = `<p style="color:var(--text3);padding:12px 0">${T.noResults}</p>`;
    }

    sec.scrollIntoView({ behavior:'smooth', block:'start' });
  } catch(e) {
    alert(TRANS[G.lang].connError);
    console.error(e);
  } finally {
    btn.textContent = TRANS[G.lang].searchBtn;
    btn.disabled = false;
  }
}

function clearHomeResults() {
  $('#homeResultsSec').style.display = 'none';
  $('#heroQ').value = '';
}

// ══════════════════════════════════════════════════════════════════
// CHAT PAGE
// ══════════════════════════════════════════════════════════════════
function resetChat() {
  G.chatHistory = [];
  const msgs = $('#chatMessages');
  msgs.innerHTML = `
    <div class="chat-welcome" id="chatWelcome">
      <div class="welcome-logo">◆</div>
      <h2 id="chatWelcomeTitle">${TRANS[G.lang].chatWelcomeTitle}</h2>
      <p id="chatWelcomeSub">${TRANS[G.lang].chatWelcomeSub}</p>
    </div>`;
  $('#chatInput').value = '';
  $('#chatInput').focus();
}

function setupChat() {
  $('#chatSendBtn').addEventListener('click', sendChat);
  $('#chatInput').addEventListener('keydown', e => { if (e.key === 'Enter') sendChat(); });

  $('#chatSuggestions').addEventListener('click', e => {
    const btn = e.target.closest('.suggestion-btn');
    if (!btn) return;
    $('#chatInput').value = btn.textContent;
    sendChat();
  });

  // New Chat button
  const newChatBtn = document.createElement('button');
  newChatBtn.id = 'newChatBtn';
  newChatBtn.className = 'new-chat-btn';
  newChatBtn.textContent = TRANS[G.lang].newChatBtn;
  newChatBtn.addEventListener('click', resetChat);
  const sidebar = $('#page-chat .chat-sidebar');
  sidebar.insertBefore(newChatBtn, sidebar.firstChild);

  // Mobile suggestions strip
  injectMobileSuggestions();
}

function injectMobileSuggestions() {
  const bar = $('#page-chat .chat-input-bar');
  if (!bar) return;
  const T = TRANS[G.lang];

  const strip = document.createElement('div');
  strip.className = 'mobile-suggestions';
  strip.id = 'mobileSuggestions';
  T.suggestions.forEach(s => {
    const chip = document.createElement('button');
    chip.className = 'mobile-suggestion-chip';
    chip.textContent = s;
    chip.addEventListener('click', () => {
      $('#chatInput').value = s;
      sendChat();
    });
    strip.appendChild(chip);
  });

  // Wrap original input+btn in a row div
  const input = $('#chatInput');
  const btn   = $('#chatSendBtn');
  const row   = document.createElement('div');
  row.className = 'chat-input-row';
  bar.insertBefore(row, input);
  row.appendChild(input);
  row.appendChild(btn);

  bar.insertBefore(strip, row);
}

// Converts markdown-style LLM output to formatted HTML
function formatAIMsg(text) {
  // Escape HTML entities first
  let t = text
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;');

  // Bold **text**
  t = t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Process line by line — group bullet/numbered lines into lists
  const lines = t.split('\n');
  const out   = [];
  let listType = null;   // 'ul' | 'ol' | null

  const closeList = () => { if (listType) { out.push(`</${listType}>`); listType = null; } };

  for (const raw of lines) {
    const line  = raw.trimEnd();
    const ulM   = line.match(/^[\s]*[-•*]\s+(.+)$/);
    const olM   = line.match(/^[\s]*\d+\.\s+(.+)$/);

    if (ulM) {
      if (listType !== 'ul') { closeList(); out.push('<ul>'); listType = 'ul'; }
      out.push(`<li>${ulM[1]}</li>`);
    } else if (olM) {
      if (listType !== 'ol') { closeList(); out.push('<ol>'); listType = 'ol'; }
      out.push(`<li>${olM[1]}</li>`);
    } else {
      closeList();
      if (line.trim() === '') {
        out.push('<br>');
      } else {
        out.push(`<p>${line}</p>`);
      }
    }
  }
  closeList();

  // Collapse multiple consecutive <br> tags into one
  return out.join('').replace(/(<br>\s*){2,}/g, '<br>');
}

function appendMsg(role, text, docs) {
  const welcome = $('#chatWelcome');
  if (welcome) welcome.remove();

  const msgs = $('#chatMessages');
  const row = document.createElement('div');
  row.className = `msg-row ${role}`;

  let cardsHTML = '';
  if (docs && docs.length) {
    cardsHTML = `<div class="chat-cards-row">${docs.map(d => chatPlaceCardHTML(d)).join('')}</div>`;
  }

  row.innerHTML = `
    <div class="msg-avatar ${role}">${role==='ai'?'◆':'Y'}</div>
    <div class="msg-body">
      <div class="msg-bubble">${role === 'ai' ? formatAIMsg(text) : esc(text)}</div>
      ${cardsHTML}
    </div>`;

  msgs.appendChild(row);
  row.querySelectorAll('img').forEach(guardImg);
  msgs.scrollTop = msgs.scrollHeight;
  return row;
}

function appendTyping() {
  const welcome = $('#chatWelcome');
  if (welcome) welcome.remove();
  const msgs = $('#chatMessages');
  const row = document.createElement('div');
  row.className = 'msg-row ai';
  row.id = 'typingRow';
  row.innerHTML = `
    <div class="msg-avatar ai">◆</div>
    <div class="msg-body"><div class="msg-bubble"><div class="typing-dots"><span></span><span></span><span></span></div></div></div>`;
  msgs.appendChild(row);
  msgs.scrollTop = msgs.scrollHeight;
  return row;
}

async function sendChat() {
  const input = $('#chatInput');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';

  G.chatHistory.push({ role:'user', content:text });
  appendMsg('user', text);

  const typingRow = appendTyping();
  const sendBtn = $('#chatSendBtn');
  sendBtn.disabled = true;

  try {
    const res = await fetch('/api/chat', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        messages: G.chatHistory,
        top_k: 6,
        arabic_mode: G.lang === 'ar',
      }),
    });
    if (!res.ok) throw new Error('Server error');
    const data = await res.json();

    typingRow.remove();
    const answer = data.answer || TRANS[G.lang].noResults;
    const docs = data.docs || [];
    G.chatHistory.push({ role:'assistant', content:answer });
    appendMsg('ai', answer, docs);
  } catch(e) {
    typingRow.remove();
    appendMsg('ai', TRANS[G.lang].connError, []);
    console.error(e);
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

// ══════════════════════════════════════════════════════════════════
// EXPLORE PAGE
// ══════════════════════════════════════════════════════════════════
let exploreState = { type:'cafe', offset:0, total:0 };
const PAGE_SIZE = 24;

function setupExplore() {
  // Mobile filter toggle
  const mft = $('#mobileFilterToggle');
  if (mft) {
    mft.addEventListener('click', () => {
      const panel = $('#filtersPanel');
      panel.classList.toggle('open');
      mft.classList.toggle('active');
    });
  }

  $$('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadExplore(btn.dataset.type);
    });
  });
  $('#applyFiltersBtn').addEventListener('click', () => loadExplore(exploreState.type));
  $('#resetFiltersBtn').addEventListener('click', () => {
    $('#fRating').value = '';
    $('#fPrice').value  = '';
    $('#fDistrict').value = '';
    loadExplore(exploreState.type);
  });
}

async function loadExplore(type, append=false) {
  exploreState.type = type;
  if (!append) exploreState.offset = 0;

  const cards = $('#exploreCards');
  if (!append) {
    cards.innerHTML = skeletonHTML(8);
  }

  // Fetch more when filters are active so client-side filtering has enough candidates
  const rating   = parseFloat($('#fRating').value);
  const price    = $('#fPrice').value;
  const district = $('#fDistrict').value.toLowerCase().trim();
  const hasFilter = !isNaN(rating) || price || district;
  const fetchTopK = hasFilter ? 300 : exploreState.offset + PAGE_SIZE;
  const requestedTopK = exploreState.offset + PAGE_SIZE;

  try {
    const res = await fetch(`/api/explore/${type}?top_k=${fetchTopK}`);
    if (!res.ok) throw new Error();
    const data = await res.json();
    let docs = data.docs || [];

    // Client-side filters
    if (!isNaN(rating)) docs = docs.filter(d => parseFloat(d.rating) >= rating);
    if (price)    docs = docs.filter(d => d.price === price);
    if (district) docs = docs.filter(d => (d.district||'').toLowerCase().includes(district));

    const slice = append ? docs.slice(exploreState.offset) : docs;
    G.exploreDocs = append ? [...G.exploreDocs, ...slice] : docs;
    exploreState.total = docs.length;

    if (!append) renderExploreCards(docs);
    else {
      slice.forEach(d => {
        cards.insertAdjacentHTML('beforeend', placeCardHTML(d));
      });
      cards.querySelectorAll('img:not([data-guarded])').forEach(img => { img.dataset.guarded='1'; guardImg(img); });
    }

    exploreState.offset = G.exploreDocs.length;

    // Count label (only show count, not the error message — cards handle empty state)
    const T = TRANS[G.lang];
    const typeLabel = type === 'cafe' ? T.tabCafe : type === 'restaurant' ? T.tabRest : T.tabHotel;
    $('#exploreCount').textContent = docs.length ? `${docs.length} ${typeLabel}` : '';

    // Load more — only show when there are results AND a full page was returned
    const wrap = $('#loadMoreWrap');
    wrap.style.display = docs.length && (data.docs?.length || 0) >= requestedTopK ? 'block' : 'none';
    const lmb = $('#loadMoreBtn');
    if (lmb) {
      lmb.onclick = () => loadExplore(exploreState.type, true);
      lmb.textContent = T.loadMoreBtn;
    }
  } catch(e) {
    cards.innerHTML = `<p style="color:var(--text3);padding:12px">${TRANS[G.lang].connError}</p>`;
    console.error(e);
  }
}

function renderExploreCards(docs) {
  const cards = $('#exploreCards');
  if (!docs.length) {
    cards.innerHTML = `<p style="color:var(--text3);padding:12px">${TRANS[G.lang].noResults}</p>`;
    return;
  }
  cards.innerHTML = docs.map(d => placeCardHTML(d)).join('');
  cards.querySelectorAll('img').forEach(guardImg);
}

// ══════════════════════════════════════════════════════════════════
// MAP PAGE
// ══════════════════════════════════════════════════════════════════
function setupMap() {
  $$('.map-chip').forEach(c => {
    c.addEventListener('click', () => {
      $$('.map-chip').forEach(x => x.classList.remove('active'));
      c.classList.add('active');
      G.mapType = c.dataset.type;
      if (G.map) loadMapPlaces(G.mapType);
    });
  });
}

function initMap() {
  if (G.map) return;
  const Lf = window.L;
  if (!Lf) { setTimeout(initMap, 300); return; }

  G.map = Lf.map('riyadhMap', { zoomControl:true }).setView([24.7136, 46.6753], 11);
  Lf.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution:'© OpenStreetMap contributors', maxZoom:18,
  }).addTo(G.map);
  G.mapMarkers = Lf.layerGroup().addTo(G.map);
  loadMapPlaces('');
}

async function loadMapPlaces(type) {
  if (!G.map) return;
  G.mapMarkers.clearLayers();
  try {
    const url = '/api/map' + (type ? `?place_type=${type}` : '');
    const res = await fetch(url);
    if (!res.ok) return;
    const data = await res.json();
    const Lf = window.L;
    const colors = { cafe:'#0C5235', restaurant:'#B85014', hotel:'#1E3C8C' };

    (data.docs || []).forEach(doc => {
      const [lat, lng] = districtCoords(doc.district);
      const jlat = lat + (Math.random()-.5)*.018;
      const jlng = lng + (Math.random()-.5)*.018;
      const color = colors[doc.type] || '#555';
      const img   = bestImg(doc.name, doc.type);
      const rating = doc.rating ? `⭐ ${parseFloat(doc.rating).toFixed(1)}` : '';

      const marker = Lf.circleMarker([jlat,jlng], {
        radius:7, fillColor:color, color:'#fff', weight:1.5, fillOpacity:.85,
      });
      marker.bindPopup(`
        <div style="width:180px;font-family:Inter,sans-serif">
          <img src="${esc(img)}" alt="${esc(doc.name)}" style="width:100%;height:100px;object-fit:cover;border-radius:6px;margin-bottom:8px">
          <div style="font-weight:700;font-size:.92rem;margin-bottom:4px">${esc(doc.name)}</div>
          <div style="font-size:.78rem;color:#666">${rating} · ${doc.district||''}</div>
          <div style="font-size:.74rem;color:${color};font-weight:600;margin-top:4px;text-transform:capitalize">${doc.type||''}</div>
        </div>`, { maxWidth:200 });
      marker.addTo(G.mapMarkers);
    });
  } catch(e) { console.error(e); }
}

// ══════════════════════════════════════════════════════════════════
// PLAN PAGE
// ══════════════════════════════════════════════════════════════════
function setupPlan() {
  $('#genPlanBtn').addEventListener('click', generatePlans);
  $('#planPrev').addEventListener('click', () => {
    if (!G.plans.length) return;
    G.planIdx = (G.planIdx - 1 + G.plans.length) % G.plans.length;
    renderPlan(G.planIdx);
  });
  $('#planNext').addEventListener('click', () => {
    if (!G.plans.length) return;
    G.planIdx = (G.planIdx + 1) % G.plans.length;
    renderPlan(G.planIdx);
  });
  $('#budgetInput').addEventListener('keydown', e => { if (e.key === 'Enter') generatePlans(); });
}

async function generatePlans() {
  const budget = parseFloat($('#budgetInput').value) || null;
  const btn = $('#genPlanBtn');
  btn.textContent = '…';
  btn.disabled = true;

  try {
    const res = await fetch('/api/itinerary', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ budget }),
    });
    if (!res.ok) throw new Error();
    const data = await res.json();
    G.plans   = data.plans || [];
    G.planIdx = 0;

    if (G.plans.length) {
      $('#planEmpty').style.display  = 'none';
      $('#planResults').style.display = 'block';
      renderPlan(0);
    }
  } catch(e) {
    alert(TRANS[G.lang].connError);
    console.error(e);
  } finally {
    btn.textContent = TRANS[G.lang].genBtn;
    btn.disabled    = false;
  }
}

function renderPlan(idx) {
  const T    = TRANS[G.lang];
  const plan = G.plans[idx];
  if (!plan) return;

  $('#planCounter').textContent = `${G.lang==='ar'?'خطة':'Plan'} ${idx+1} ${G.lang==='ar'?'من':'of'} ${G.plans.length}`;
  $('#planTheme').textContent   = plan.theme || '';
  $('#planCostBadge').textContent = plan.estimated_cost
    ? `${T.estCost}: ${T.approxPrice(plan.estimated_cost)}`
    : '';

  const slots = plan.slots || [];
  $('#planSlots').innerHTML = slots.map(slot => {
    const doc = slot.doc || {};
    const t   = doc.type || slot.type || 'cafe';
    const img = bestImg(doc.name||'', t);
    const rating = doc.rating ? `⭐ ${parseFloat(doc.rating).toFixed(1)}` : '';
    const district = doc.district ? `📍 ${doc.district}` : '';
    const price = doc.name ? formatPrice(doc) : null;
    const period = slot.period || 'Morning';
    const icon   = T.periodIcons[period] || '⏰';
    const periodLabel = T['period'+period] || period;
    const colors = { cafe:'badge-cafe', restaurant:'badge-restaurant', hotel:'badge-hotel' };

    return `
    <div class="plan-slot">
      <div class="plan-slot-period">
        <span class="slot-period-icon">${icon}</span>
        <span class="slot-period-label">${periodLabel}</span>
      </div>
      <div class="plan-slot-img">
        ${imgTag(img, doc.name||'', t)}
      </div>
      <div class="plan-slot-info">
        <span class="slot-type-badge ${colors[t]||'badge-cafe'}">${esc(t)}</span>
        <div class="slot-name">${esc(doc.name||'—')}</div>
        <div class="slot-meta">
          ${rating ? `<span>${rating}</span>  ` : ''}
          ${district}
        </div>
        ${price ? `<div class="slot-price">${esc(price)}</div>` : ''}
      </div>
    </div>`;
  }).join('');

  $('#planSlots').querySelectorAll('img').forEach(guardImg);
}

// ══════════════════════════════════════════════════════════════════
// SKELETON CARDS
// ══════════════════════════════════════════════════════════════════
function skeletonHTML(n = 8) {
  return Array.from({length: n}, () => `
    <div class="skeleton-card">
      <div class="skeleton-img"></div>
      <div class="skeleton-body">
        <div class="skeleton-line wide"></div>
        <div class="skeleton-line medium"></div>
        <div class="skeleton-line narrow"></div>
      </div>
    </div>`).join('');
}

// ══════════════════════════════════════════════════════════════════
// TOAST
// ══════════════════════════════════════════════════════════════════
function showToast(msg, duration = 3000) {
  const t = $('#toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(G.toastTimer);
  G.toastTimer = setTimeout(() => {
    t.classList.remove('show');
  }, duration);
}

// ══════════════════════════════════════════════════════════════════
// SHARE
// ══════════════════════════════════════════════════════════════════
function sharePlace(name) {
  const url = `${location.origin}${location.pathname}?place=${encodeURIComponent(name)}`;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(url).then(() => showToast('Link copied to clipboard!')).catch(() => fallbackCopy(url));
  } else {
    fallbackCopy(url);
  }
}
function fallbackCopy(text) {
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.select();
  document.execCommand('copy');
  document.body.removeChild(ta);
  showToast('Link copied!');
}

// ══════════════════════════════════════════════════════════════════
// PLACE MODAL
// ══════════════════════════════════════════════════════════════════
function openModal(doc) {
  G.modalDoc = doc;
  const t = doc.type || 'cafe';
  const img = bestImg(doc.name, t);

  const modalImg = $('#modalImg');
  modalImg.src = img;
  modalImg.alt = doc.name;
  modalImg.dataset.type = t;
  modalImg.onerror = function() { this.onerror = null; this.src = poolImg(doc.name, t); };

  const badge = $('#modalTypeBadge');
  badge.textContent = t;
  badge.className = `card-type-badge badge-${t}`;

  $('#modalName').textContent = doc.name;

  const rating = doc.rating ? `⭐ ${parseFloat(doc.rating).toFixed(1)}` : '';
  const district = doc.district || '';
  const price = formatPrice(doc);
  const metaItems = [];
  if (rating)   metaItems.push(`<span class="modal-meta-item">${rating}</span>`);
  if (district) metaItems.push(`<span class="modal-meta-item">📍 ${esc(district)}</span>`);
  if (price)    metaItems.push(`<span class="modal-meta-item modal-price">${esc(price)}</span>`);
  $('#modalMeta').innerHTML = metaItems.join('');

  const desc = (doc.text || '').trim();
  const descEl = $('#modalDesc');
  if (desc) {
    descEl.textContent = desc.length > 320 ? desc.slice(0, 320) + '…' : desc;
    descEl.style.display = 'block';
  } else {
    descEl.style.display = 'none';
  }

  const overlay = $('#placeModal');
  overlay.style.display = 'flex';
  document.body.style.overflow = 'hidden';
  requestAnimationFrame(() => overlay.classList.add('open'));

  setTimeout(() => initModalMap(doc), 150);
}

function closeModal() {
  const overlay = $('#placeModal');
  overlay.classList.remove('open');
  document.body.style.overflow = '';
  setTimeout(() => { overlay.style.display = 'none'; }, 300);
  if (G.modalMap) { G.modalMap.invalidateSize(); }
}

function initModalMap(doc) {
  const Lf = window.L;
  if (!Lf) return;
  const [lat, lng] = districtCoords(doc.district);
  const colors = { cafe:'#0C5235', restaurant:'#B85014', hotel:'#1E3C8C' };
  const color = colors[doc.type] || '#555';

  if (!G.modalMap) {
    G.modalMap = Lf.map('modalMiniMap', { zoomControl: false, attributionControl: false, dragging: true, scrollWheelZoom: false })
      .setView([lat, lng], 13);
    Lf.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18 }).addTo(G.modalMap);
    G.modalMapMarkers = Lf.layerGroup().addTo(G.modalMap);
  } else {
    G.modalMap.setView([lat, lng], 13);
    G.modalMapMarkers.clearLayers();
  }

  Lf.circleMarker([lat, lng], {
    radius: 10, fillColor: color, color: '#fff', weight: 2.5, fillOpacity: 1,
  }).addTo(G.modalMapMarkers);

  G.modalMap.invalidateSize();
}

function setupModal() {
  $('#modalClose').addEventListener('click', closeModal);
  $('#placeModal').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeModal();
  });
  $('#modalShareBtn').addEventListener('click', () => {
    if (G.modalDoc) sharePlace(G.modalDoc.name);
  });

  // Card clicks (event delegation — works for all card grids)
  document.addEventListener('click', e => {
    // Share button on card
    const shareBtn = e.target.closest('.card-share-btn');
    if (shareBtn) {
      e.stopPropagation();
      sharePlace(shareBtn.dataset.shareName);
      return;
    }
    // Card click → open modal
    const card = e.target.closest('.place-card[data-place-name]');
    if (card) {
      const doc = G.docsMap[card.dataset.placeName];
      if (doc) openModal(doc);
    }
  });

  // Close on Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
  });
}

// ══════════════════════════════════════════════════════════════════
// DARK MODE
// ══════════════════════════════════════════════════════════════════
function setupTheme() {
  const saved = localStorage.getItem('gr-theme') || 'light';
  applyTheme(saved);
  $('#themeBtn').addEventListener('click', () => {
    applyTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
  });
}
function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  $('#themeBtn').textContent = theme === 'dark' ? '☀️' : '🌙';
  localStorage.setItem('gr-theme', theme);
}

// ══════════════════════════════════════════════════════════════════
// SCROLL REVEAL
// ══════════════════════════════════════════════════════════════════
function setupScrollReveal() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); }
    });
  }, { threshold: 0.1 });

  $$('.feature-card, .stat-card').forEach((el, i) => {
    el.classList.add('reveal', `reveal-delay-${(i % 4) + 1}`);
    obs.observe(el);
  });
}

// ══════════════════════════════════════════════════════════════════
// NAV SCROLL EFFECT
// ══════════════════════════════════════════════════════════════════
function setupNavScroll() {
  window.addEventListener('scroll', () => {
    document.getElementById('topNav').classList.toggle('scrolled', window.scrollY > 10);
  }, { passive:true });
}

// ══════════════════════════════════════════════════════════════════
// INIT
// ══════════════════════════════════════════════════════════════════
function init() {
  loadPlaceImages();

  // All nav links (desktop + mobile + logo)
  $$('[data-nav]').forEach(el => {
    el.addEventListener('click', e => {
      e.preventDefault();
      navigate(el.dataset.nav);
    });
  });

  // Mobile menu toggle
  $('#navMenuBtn').addEventListener('click', () => {
    const mob = $('#navMobile');
    mob.style.display = mob.style.display === 'flex' ? 'none' : 'flex';
    if (mob.style.display === 'flex') mob.style.flexDirection = 'column';
  });

  // Language toggle
  $('#langBtn').addEventListener('click', () => setLang(G.lang === 'en' ? 'ar' : 'en'));

  setupHome();
  setupChat();
  setupExplore();
  setupMap();
  setupPlan();
  setupTheme();
  setupModal();
  setupNavScroll();
  loadStats();
  setTimeout(setupScrollReveal, 300);

  // Initial page from hash
  const hash = window.location.hash.slice(1);
  navigate(['home','chat','explore','map','plan'].includes(hash) ? hash : 'home');
}

document.addEventListener('DOMContentLoaded', init);
