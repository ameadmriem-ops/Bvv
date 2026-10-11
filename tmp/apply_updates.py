import re

with open('app/src/main/assets/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add episode alternative titles input in editEpisodeModal
old_ep_alt_input = '''        <div>
          <label style="font-size:12px;color:#aaa;display:block;margin-bottom:4px">رابط الموقع البديل (اختياري - YouTube أو موقع آخر):</label>
          <input id="editEpAltUrlInput" class="input" placeholder="رابط الموقع البديل">
        </div>'''

new_ep_alt_input = '''        <div>
          <label style="font-size:12px;color:#aaa;display:block;margin-bottom:4px">رابط الموقع البديل (اختياري - YouTube أو موقع آخر):</label>
          <input id="editEpAltUrlInput" class="input" placeholder="رابط الموقع البديل">
        </div>
        <div>
          <label style="font-size:12px;color:#aaa;display:block;margin-bottom:4px">الأسماء البديلة للحلقة للبحث (اختياري - مفصولة بفواصل):</label>
          <input id="editEpAltTitlesInput" class="input" placeholder="مثال: حلقة 1, الحلقة الأولى, Special">
        </div>'''

assert old_ep_alt_input in html, "old_ep_alt_input not found"
html = html.replace(old_ep_alt_input, new_ep_alt_input, 1)

# 2. Add editAltTitlesModal right before testNotificationModal
test_notif_modal_marker = '<!-- Test / Send Custom Notification Modal -->'
assert test_notif_modal_marker in html, "test_notif_modal_marker not found"

alt_modal_code = '''  <!-- Edit Alternative Titles Modal (Admin Only) -->
  <div id="editAltTitlesModal" class="ad-overlay" style="display:none;z-index:3700">
    <div class="ad-popup-card" style="max-width:460px;width:92%;background:#141414;border:1px solid #333;border-radius:16px;padding:18px;text-align:right;color:#fff;direction:rtl;max-height:90vh;overflow-y:auto">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;border-bottom:1px solid #222;padding-bottom:10px">
        <h3 style="margin:0;font-size:17px;font-weight:900;color:#fff;display:flex;align-items:center;gap:8px">🏷️ الأسماء البديلة للبحث</h3>
        <button type="button" onclick="closeEditAlternativeTitlesModal()" style="background:none;border:none;color:#888;font-size:20px;cursor:pointer;padding:4px">✕</button>
      </div>

      <div style="display:flex;flex-direction:column;gap:12px">
        <div id="editAltTitlesTargetTitle" style="font-size:15px;font-weight:bold;color:#00d2ff;text-align:center"></div>
        <p style="font-size:12px;color:#aaa;margin:0;line-height:1.5">
          أضف أسماء بديلة أو مرادفات للبحث (بالعربية، الإنجليزية، اليابانية وغيرها). سيتمكن المستخدمون من إيجاد هذا العمل بالبحث عن أي منها والوصول إلى العمل نفسه دون تكرار.
        </p>

        <div>
          <label style="font-size:12px;color:#aaa;display:block;margin-bottom:4px">إضافة اسم بديل جديد:</label>
          <div style="display:flex;gap:6px">
            <input id="editAltTitleInput" class="input" style="flex:1;margin:0" placeholder="مثال: ون بيس أو ワンピース" onkeydown="if(event.key==='Enter'){event.preventDefault();window.addModalAltTitle();}">
            <button type="button" onclick="window.addModalAltTitle()" style="background:#00d2ff;color:#000;border:none;padding:8px 14px;border-radius:8px;font-size:12px;font-weight:bold;cursor:pointer;white-space:nowrap">➕ إضافة</button>
          </div>
          <div style="font-size:10px;color:#777;margin-top:4px">يمكنك أيضاً إدخال عدة أسماء مفصولة بفواصل ( , أو ، )</div>
        </div>

        <div style="background:#0d0d0d;border:1px solid #262626;border-radius:12px;padding:12px">
          <div style="font-size:12px;font-weight:bold;color:#bbb;margin-bottom:8px">الأسماء البديلة المحفوظة لهذا العمل:</div>
          <div id="modalAltTitlesList" style="display:flex;flex-wrap:wrap;gap:6px;min-height:36px"></div>
        </div>

        <div id="editAltTitlesStatusMsg" style="font-size:12px;color:#aaa;text-align:center;min-height:16px"></div>

        <div style="display:flex;gap:10px;margin-top:4px">
          <button id="saveEditAltTitlesBtn" onclick="saveAlternativeTitlesFromModal()" style="flex:1;background:linear-gradient(135deg,#e50914,#b80610);color:#fff;border:none;padding:12px;border-radius:10px;font-weight:bold;font-size:14px;cursor:pointer">💾 حفظ الأسماء البديلة</button>
          <button type="button" onclick="closeEditAlternativeTitlesModal()" style="background:#1c1c1c;color:#aaa;border:1px solid #333;padding:12px 18px;border-radius:10px;cursor:pointer;font-size:14px">إلغاء</button>
        </div>
      </div>
    </div>
  </div>

'''

html = html.replace(test_notif_modal_marker, alt_modal_code + test_notif_modal_marker, 1)

# 3. Update onSnapshot mapping to safely parse alternativeTitles
old_snapshot = '''const q=query(colRef,orderBy("createdAt","desc"),limit(500));
onSnapshot(q,(s)=>{
  window.allContent=s.docs.map(d=>({firebaseId:d.id,...d.data()}));'''

new_snapshot = '''const q=query(colRef,orderBy("createdAt","desc"),limit(500));
onSnapshot(q,(s)=>{
  window.allContent=s.docs.map(d=>{
    const data = d.data() || {};
    let alts = [];
    if (Array.isArray(data.alternativeTitles)) {
      alts = data.alternativeTitles.map(x => String(x || "").trim()).filter(Boolean);
    } else if (typeof data.alternativeTitles === "string" && data.alternativeTitles.trim()) {
      alts = data.alternativeTitles.split(/[,،\\n]+/).map(x => x.trim()).filter(Boolean);
    }
    return {
      firebaseId: d.id,
      ...data,
      alternativeTitles: alts
    };
  });'''

assert old_snapshot in html, "old_snapshot not found"
html = html.replace(old_snapshot, new_snapshot, 1)

# 4. Update createCard to include Edit Alternative Titles button for Admin
old_create_card = '''  let editPosterBtn=(window.currentUserRole==="ADMIN")?`<button type="button" tabindex="0" style="width:100%;margin-top:8px;background:#1a2a3a;color:#00d2ff;border:1px solid #2a4a6a;padding:6px 8px;border-radius:8px;font-size:11px;font-weight:bold;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:4px" onclick="event.stopPropagation();openEditPosterModal('${item.firebaseId}')">🖼️ تعديل البوستر</button>`:"";
  let isAnimation = item.type === "animation" || item.type === "arabic" || item.type === "sports";
  let categoryLabel = window.translateCategoryLabel(item.category, isAnimation);
  return`<div class="movie-card" tabindex="0"><button tabindex="0" class="favorite-btn ${fav?"active":""}" onclick="event.stopPropagation();toggleFavorite('${item.id}')">♥</button>${del}<div onclick="${click}"><img class="poster" data-poster-fid="${item.firebaseId}" src="${item.poster}" loading="lazy" decoding="async"><h3>${item.title}</h3><p>${item.year} • ${categoryLabel}</p></div>${editPosterBtn}</div>`;'''

new_create_card = '''  let editPosterBtn=(window.currentUserRole==="ADMIN")?`<button type="button" tabindex="0" style="width:100%;margin-top:8px;background:#1a2a3a;color:#00d2ff;border:1px solid #2a4a6a;padding:6px 8px;border-radius:8px;font-size:11px;font-weight:bold;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:4px" onclick="event.stopPropagation();openEditPosterModal('${item.firebaseId}')">🖼️ تعديل البوستر</button>`:"";
  let editAltTitlesBtn=(window.currentUserRole==="ADMIN")?`<button type="button" tabindex="0" style="width:100%;margin-top:4px;background:#1b2a1e;color:#4ade80;border:1px solid #285430;padding:6px 8px;border-radius:8px;font-size:11px;font-weight:bold;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:4px" onclick="event.stopPropagation();openEditAlternativeTitlesModal('${item.firebaseId}')">🏷️ الأسماء البديلة</button>`:"";
  let isAnimation = item.type === "animation" || item.type === "arabic" || item.type === "sports";
  let categoryLabel = window.translateCategoryLabel(item.category, isAnimation);
  return`<div class="movie-card" tabindex="0"><button tabindex="0" class="favorite-btn ${fav?"active":""}" onclick="event.stopPropagation();toggleFavorite('${item.id}')">♥</button>${del}<div onclick="${click}"><img class="poster" data-poster-fid="${item.firebaseId}" src="${item.poster}" loading="lazy" decoding="async"><h3>${item.title}</h3><p>${item.year} • ${categoryLabel}</p></div>${editPosterBtn}${editAltTitlesBtn}</div>`;'''

assert old_create_card in html, "old_create_card not found"
html = html.replace(old_create_card, new_create_card, 1)

# 5. Update openDetails and openDetailsBack to display alternative titles and Admin button
old_open_details_body = '''    let editPosterDetailBtn = (window.currentUserRole === "ADMIN") ? `<button type="button" onclick="openEditPosterModal('${item.firebaseId}')" style="background:#1a2a3a;color:#00d2ff;border:1px solid #2a4a6a;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:bold;cursor:pointer;display:inline-flex;align-items:center;gap:6px">🖼️ تعديل البوستر</button>` : "";
    let reportDetailBtn = `<button type="button" onclick="openReportProblemModal('${item.firebaseId}', -1)" style="background:#260a0a;color:#ff6b6b;border:1px solid #4a1515;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:bold;cursor:pointer;display:inline-flex;align-items:center;gap:6px">🚩 الإبلاغ عن مشكلة</button>`;

    main.innerHTML=`<div class="page-header" style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px 4px 14px;margin-top:55px"><button class="back-btn" style="margin:0" onclick="goBack()">${t("back_btn")}</button>${orderBtnHtml}</div><div style="padding:15px;text-align:center"><img class="poster" data-poster-fid="${item.firebaseId}" src="${item.poster}" style="width:140px;height:140px;object-fit:contain;padding:10px;border-radius:18px"><div style="margin-top:10px;display:flex;justify-content:center;gap:8px;flex-wrap:wrap">${editPosterDetailBtn}${reportDetailBtn}</div><h1 style="margin-top:12px">${item.title}</h1><p style="color:#888">${item.year} • ${categoryLabel}</p>${window.renderDescriptionHtml(item.firebaseId)}</div><div id="episodesListContainer" style="padding:12px;display:flex;flex-direction:column;gap:8px"></div>`;'''

new_open_details_body = '''    let editPosterDetailBtn = (window.currentUserRole === "ADMIN") ? `<button type="button" onclick="openEditPosterModal('${item.firebaseId}')" style="background:#1a2a3a;color:#00d2ff;border:1px solid #2a4a6a;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:bold;cursor:pointer;display:inline-flex;align-items:center;gap:6px">🖼️ تعديل البوستر</button>` : "";
    let editAltTitlesDetailBtn = (window.currentUserRole === "ADMIN") ? `<button type="button" onclick="openEditAlternativeTitlesModal('${item.firebaseId}')" style="background:#1b2a1e;color:#4ade80;border:1px solid #285430;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:bold;cursor:pointer;display:inline-flex;align-items:center;gap:6px">🏷️ الأسماء البديلة</button>` : "";
    let reportDetailBtn = `<button type="button" onclick="openReportProblemModal('${item.firebaseId}', -1)" style="background:#260a0a;color:#ff6b6b;border:1px solid #4a1515;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:bold;cursor:pointer;display:inline-flex;align-items:center;gap:6px">🚩 الإبلاغ عن مشكلة</button>`;
    let altTitlesBadges = (Array.isArray(item.alternativeTitles) && item.alternativeTitles.length > 0)
      ? `<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:6px;margin:8px auto;max-width:340px">${item.alternativeTitles.map(a => `<span style="background:#1a2332;color:#38bdf8;border:1px solid #1e3a5f;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:500">🏷️ ${window.escapeDescHtml(a)}</span>`).join("")}</div>`
      : "";

    main.innerHTML=`<div class="page-header" style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px 4px 14px;margin-top:55px"><button class="back-btn" style="margin:0" onclick="goBack()">${t("back_btn")}</button>${orderBtnHtml}</div><div style="padding:15px;text-align:center"><img class="poster" data-poster-fid="${item.firebaseId}" src="${item.poster}" style="width:140px;height:140px;object-fit:contain;padding:10px;border-radius:18px"><div style="margin-top:10px;display:flex;justify-content:center;gap:8px;flex-wrap:wrap">${editPosterDetailBtn}${editAltTitlesDetailBtn}${reportDetailBtn}</div><h1 style="margin-top:12px">${item.title}</h1>${altTitlesBadges}<p style="color:#888">${item.year} • ${categoryLabel}</p>${window.renderDescriptionHtml(item.firebaseId)}</div><div id="episodesListContainer" style="padding:12px;display:flex;flex-direction:column;gap:8px"></div>`;'''

assert old_open_details_body in html, "old_open_details_body not found"
html = html.replace(old_open_details_body, new_open_details_body, 1)

old_open_details_back_body = '''  let editPosterDetailBtn = (window.currentUserRole === "ADMIN") ? `<button type="button" onclick="openEditPosterModal('${item.firebaseId}')" style="background:#1a2a3a;color:#00d2ff;border:1px solid #2a4a6a;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:bold;cursor:pointer;display:inline-flex;align-items:center;gap:6px">🖼️ تعديل البوستر</button>` : "";
  let reportDetailBtn = `<button type="button" onclick="openReportProblemModal('${item.firebaseId}', -1)" style="background:#260a0a;color:#ff6b6b;border:1px solid #4a1515;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:bold;cursor:pointer;display:inline-flex;align-items:center;gap:6px">🚩 الإبلاغ عن مشكلة</button>`;

  main.innerHTML=`<div class="page-header" style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px 4px 14px;margin-top:55px"><button class="back-btn" style="margin:0" onclick="goBack()">${t("back_btn")}</button>${orderBtnHtml}</div><div style="padding:15px;text-align:center"><img class="poster" data-poster-fid="${item.firebaseId}" src="${item.poster}" style="width:140px;height:140px;object-fit:contain;padding:10px;border-radius:18px"><div style="margin-top:10px;display:flex;justify-content:center;gap:8px;flex-wrap:wrap">${editPosterDetailBtn}${reportDetailBtn}</div><h1>${item.title}</h1><p style="color:#888">${item.year} • ${categoryLabel}</p>${window.renderDescriptionHtml(item.firebaseId)}</div><div id="episodesListContainer" style="padding:12px;display:flex;flex-direction:column;gap:8px"></div>`;'''

new_open_details_back_body = '''  let editPosterDetailBtn = (window.currentUserRole === "ADMIN") ? `<button type="button" onclick="openEditPosterModal('${item.firebaseId}')" style="background:#1a2a3a;color:#00d2ff;border:1px solid #2a4a6a;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:bold;cursor:pointer;display:inline-flex;align-items:center;gap:6px">🖼️ تعديل البوستر</button>` : "";
  let editAltTitlesDetailBtn = (window.currentUserRole === "ADMIN") ? `<button type="button" onclick="openEditAlternativeTitlesModal('${item.firebaseId}')" style="background:#1b2a1e;color:#4ade80;border:1px solid #285430;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:bold;cursor:pointer;display:inline-flex;align-items:center;gap:6px">🏷️ الأسماء البديلة</button>` : "";
  let reportDetailBtn = `<button type="button" onclick="openReportProblemModal('${item.firebaseId}', -1)" style="background:#260a0a;color:#ff6b6b;border:1px solid #4a1515;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:bold;cursor:pointer;display:inline-flex;align-items:center;gap:6px">🚩 الإبلاغ عن مشكلة</button>`;
  let altTitlesBadges = (Array.isArray(item.alternativeTitles) && item.alternativeTitles.length > 0)
    ? `<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:6px;margin:8px auto;max-width:340px">${item.alternativeTitles.map(a => `<span style="background:#1a2332;color:#38bdf8;border:1px solid #1e3a5f;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:500">🏷️ ${window.escapeDescHtml(a)}</span>`).join("")}</div>`
    : "";

  main.innerHTML=`<div class="page-header" style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px 4px 14px;margin-top:55px"><button class="back-btn" style="margin:0" onclick="goBack()">${t("back_btn")}</button>${orderBtnHtml}</div><div style="padding:15px;text-align:center"><img class="poster" data-poster-fid="${item.firebaseId}" src="${item.poster}" style="width:140px;height:140px;object-fit:contain;padding:10px;border-radius:18px"><div style="margin-top:10px;display:flex;justify-content:center;gap:8px;flex-wrap:wrap">${editPosterDetailBtn}${editAltTitlesDetailBtn}${reportDetailBtn}</div><h1>${item.title}</h1>${altTitlesBadges}<p style="color:#888">${item.year} • ${categoryLabel}</p>${window.renderDescriptionHtml(item.firebaseId)}</div><div id="episodesListContainer" style="padding:12px;display:flex;flex-direction:column;gap:8px"></div>`;'''

assert old_open_details_back_body in html, "old_open_details_back_body not found"
html = html.replace(old_open_details_back_body, new_open_details_back_body, 1)

# 6. Update openSearch, performSearch, and openSearchBack
old_search_block = '''window.openSearch=()=>{
  navigateTo("search",()=>{
    main.innerHTML=`<div class="page-header"><button class="back-btn" onclick="goBack()">${t("back_btn")}</button></div><div style="padding:12px"><input id="searchInput" class="input" placeholder="${t("search_placeholder")}" oninput="performSearch()"></div><div id="searchResults" class="movies-grid"></div>`;
  });
};
window.performSearch=()=>{
  let qq=document.getElementById("searchInput").value.toLowerCase();
  document.getElementById("searchResults").innerHTML=window.allContent.filter(x=>(x.title&&x.title.toLowerCase().includes(qq))||(x.category&&x.category.toLowerCase().includes(qq))).map(createCard).join("");
};'''

new_search_block = '''window.searchActiveFilter = "all";

window.normalizeSearchText = function(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .toLowerCase()
    .trim()
    .replace(/[\\u064B-\\u065F\\u0670]/g, "") // Remove Arabic Tashkeel / diacritics
    .replace(/[أإآٱ]/g, "ا")              // Normalize Alef variants
    .replace(/ى/g, "ي")                  // Normalize Alef Maksura
    .replace(/ة/g, "ه")                  // Normalize Taa Marbuta
    .replace(/ـ+/g, "")                  // Remove Tatweel / Kashida
    .replace(/[\\u200B-\\u200D\\uFEFF]/g, "") // Remove zero-width chars
    .replace(/\\s+/g, " ");               // Collapse whitespace
};

window.matchesSearchQuery = function(item, rawQuery) {
  if (!rawQuery || !rawQuery.trim()) return true;
  const q = window.normalizeSearchText(rawQuery);
  if (!q) return true;

  // 1. Primary title match (case-insensitive & normalized)
  if (item.title && window.normalizeSearchText(item.title).includes(q)) return true;

  // 2. All alternative titles match
  const alts = Array.isArray(item.alternativeTitles) ? item.alternativeTitles : [];
  for (const alt of alts) {
    if (alt && window.normalizeSearchText(alt).includes(q)) return true;
  }

  // 3. Category & Type match
  if (item.category && window.normalizeSearchText(item.category).includes(q)) return true;
  if (item.type && window.normalizeSearchText(item.type).includes(q)) return true;

  // 4. Description match
  if (item.description && window.normalizeSearchText(item.description).includes(q)) return true;

  // 5. Episode titles & episode alternative titles match
  const episodes = Array.isArray(item.episodes) ? item.episodes : [];
  for (const ep of episodes) {
    if (ep && ep.title && window.normalizeSearchText(ep.title).includes(q)) return true;
    if (ep && Array.isArray(ep.alternativeTitles)) {
      for (const epAlt of ep.alternativeTitles) {
        if (epAlt && window.normalizeSearchText(epAlt).includes(q)) return true;
      }
    }
  }

  return false;
};

window.setSearchFilter = function(filterVal) {
  window.searchActiveFilter = filterVal;
  document.querySelectorAll(".search-filter-chip").forEach(btn => {
    if (btn.getAttribute("data-filter") === filterVal) {
      btn.style.background = "#e50914";
      btn.style.color = "#fff";
      btn.style.borderColor = "#e50914";
    } else {
      btn.style.background = "#181818";
      btn.style.color = "#aaa";
      btn.style.borderColor = "#2c2c2c";
    }
  });
  window.performSearch();
};

window.renderSearchPage = function() {
  currentPage = "search";
  const currFilter = window.searchActiveFilter || "all";
  main.innerHTML = `
    <div class="page-header" style="display:flex;align-items:center;justify-content:space-between;padding:10px 14px 4px 14px;margin-top:55px">
      <button class="back-btn" style="margin:0" onclick="goBack()">${t("back_btn")}</button>
      <h2 style="margin:0;font-size:18px;color:#fff">${t("search_title")}</h2>
      <div style="width:40px"></div>
    </div>
    <div style="padding:12px;display:flex;flex-direction:column;gap:10px">
      <div style="position:relative;display:flex;align-items:center">
        <input id="searchInput" class="input" style="padding-left:36px;margin:0" placeholder="ابحث باسم العمل أو أي اسم بديل (عربي، إنجليزي...)" oninput="window.performSearch()" autofocus>
        <button type="button" onclick="document.getElementById('searchInput').value='';window.performSearch();" style="position:absolute;left:10px;background:none;border:none;color:#888;font-size:16px;cursor:pointer;padding:4px">✕</button>
      </div>
      <div style="display:flex;gap:6px;overflow-x:auto;padding-bottom:4px">
        <button type="button" class="search-filter-chip" data-filter="all" onclick="window.setSearchFilter('all')" style="background:${currFilter==='all'?'#e50914':'#181818'};color:${currFilter==='all'?'#fff':'#aaa'};border:1px solid ${currFilter==='all'?'#e50914':'#2c2c2c'};padding:6px 14px;border-radius:18px;font-size:12px;font-weight:bold;cursor:pointer;white-space:nowrap">الكل</button>
        <button type="button" class="search-filter-chip" data-filter="anime" onclick="window.setSearchFilter('anime')" style="background:${currFilter==='anime'?'#e50914':'#181818'};color:${currFilter==='anime'?'#fff':'#aaa'};border:1px solid ${currFilter==='anime'?'#e50914':'#2c2c2c'};padding:6px 14px;border-radius:18px;font-size:12px;font-weight:bold;cursor:pointer;white-space:nowrap">⚡ الأنمي</button>
        <button type="button" class="search-filter-chip" data-filter="animation" onclick="window.setSearchFilter('animation')" style="background:${currFilter==='animation'?'#e50914':'#181818'};color:${currFilter==='animation'?'#fff':'#aaa'};border:1px solid ${currFilter==='animation'?'#e50914':'#2c2c2c'};padding:6px 14px;border-radius:18px;font-size:12px;font-weight:bold;cursor:pointer;white-space:nowrap">🎬 الأنميشن</button>
        <button type="button" class="search-filter-chip" data-filter="series" onclick="window.setSearchFilter('series')" style="background:${currFilter==='series'?'#e50914':'#181818'};color:${currFilter==='series'?'#fff':'#aaa'};border:1px solid ${currFilter==='series'?'#e50914':'#2c2c2c'};padding:6px 14px;border-radius:18px;font-size:12px;font-weight:bold;cursor:pointer;white-space:nowrap">📺 مسلسلات</button>
        <button type="button" class="search-filter-chip" data-filter="movie" onclick="window.setSearchFilter('movie')" style="background:${currFilter==='movie'?'#e50914':'#181818'};color:${currFilter==='movie'?'#fff':'#aaa'};border:1px solid ${currFilter==='movie'?'#e50914':'#2c2c2c'};padding:6px 14px;border-radius:18px;font-size:12px;font-weight:bold;cursor:pointer;white-space:nowrap">🍿 أفلام</button>
      </div>
    </div>
    <div id="searchResults" class="movies-grid"></div>
  `;
  window.performSearch();
};

window.openSearch=()=>{
  navigateTo("search",()=>{
    window.renderSearchPage();
  });
};

window.performSearch=()=>{
  const input = document.getElementById("searchInput");
  const rawQ = input ? input.value : "";
  const normQ = window.normalizeSearchText(rawQ);
  const container = document.getElementById("searchResults");
  if (!container) return;

  const currentFilter = window.searchActiveFilter || "all";

  // Filter content with category filter & search matcher (distinct items, no duplicates)
  const matches = (window.allContent || []).filter(item => {
    // 1. Filter by content category / type
    if (currentFilter === "anime") {
      if (item.type !== "anime" && item.type !== "foreign" && item.type !== "news" && item.type !== "entertainment") return false;
    } else if (currentFilter === "animation") {
      if (item.type !== "animation" && item.type !== "arabic" && item.type !== "sports") return false;
    } else if (currentFilter === "series") {
      if (item.category !== "مسلسل") return false;
    } else if (currentFilter === "movie") {
      if (item.category !== "فلم") return false;
    }

    // 2. If search query is empty, show all items matching the filter
    if (!normQ) return true;

    // 3. Match against primary title, all alternative titles, category, description, and episodes
    return window.matchesSearchQuery(item, rawQ);
  });

  if (matches.length === 0) {
    if (normQ) {
      container.innerHTML = `
        <div style="grid-column:1/-1;text-align:center;padding:40px 16px;color:#777">
          <div style="font-size:36px;margin-bottom:10px">🔍</div>
          <div style="font-size:15px;color:#aaa;font-weight:bold">لم يتم العثور على نتائج لـ "${window.escapeDescHtml(rawQ)}"</div>
          <div style="font-size:12px;color:#666;margin-top:6px">جرب البحث بكلمة أخرى أو اسم بديل آخر (عربي أو إنجليزي أو ياباني)</div>
        </div>
      `;
    } else {
      container.innerHTML = `
        <div style="grid-column:1/-1;text-align:center;padding:40px 16px;color:#777">
          <div style="font-size:14px;color:#888">لا توجد أعمال في هذا التصنيف حالياً</div>
        </div>
      `;
    }
    return;
  }

  // Deduplication guaranteed: each item from window.allContent is unique in the matches array
  container.innerHTML = matches.map(createCard).join("");
};'''

assert old_search_block in html, "old_search_block not found"
html = html.replace(old_search_block, new_search_block, 1)

# 7. Update openSearchBack
old_search_back = '''window.openSearchBack=()=>{
  currentPage="search";
  main.innerHTML=`<div class="page-header"><button class="back-btn" onclick="goBack()">${t("back_btn")}</button></div><div style="padding:12px"><input id="searchInput" class="input" placeholder="${t("search_placeholder")}" oninput="performSearch()"></div><div id="searchResults" class="movies-grid"></div>`;
};'''

new_search_back = '''window.openSearchBack=()=>{
  currentPage="search";
  window.renderSearchPage();
};'''

assert old_search_back in html, "old_search_back not found"
html = html.replace(old_search_back, new_search_back, 1)

# 8. Update renderAdminManageListHtml to include 🏷️ الأسماء البديلة button and filter with normalization
old_admin_manage = '''window.renderAdminManageListHtml = function(filterText = "") {
  const q = (filterText || "").trim().toLowerCase();
  const list = (window.allContent || []).filter(item => {
    if (!q) return true;
    return (item.title && item.title.toLowerCase().includes(q)) || (item.category && item.category.toLowerCase().includes(q));
  });
  if (list.length === 0) {
    return `<div style="text-align:center;color:#777;padding:14px;font-size:13px">لا توجد أعمال مطابقة</div>`;
  }
  return list.map(item => {
    let isAnimation = item.type === "animation" || item.type === "arabic" || item.type === "sports";
    let categoryLabel = item.category || (isAnimation ? "أنميشن" : "مسلسل");
    return `
      <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;background:#161616;border:1px solid #282828;border-radius:12px;padding:8px 10px">
        <div style="display:flex;align-items:center;gap:10px;min-width:0;flex:1;cursor:pointer" onclick="openDetails('${item.firebaseId}')">
          <img class="poster" data-poster-fid="${item.firebaseId}" src="${item.poster}" style="width:48px;height:48px;border-radius:8px;object-fit:contain;margin:0;flex-shrink:0">
          <div style="min-width:0;flex:1">
            <div style="font-size:13px;font-weight:bold;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${item.title}</div>
            <div style="font-size:11px;color:#888;margin-top:2px">${item.year || ""} • ${categoryLabel}</div>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:6px;flex-shrink:0">
          <button type="button" onclick="openEditPosterModal('${item.firebaseId}')" style="background:#1a2a3a;color:#00d2ff;border:1px solid #2a4a6a;padding:7px 10px;border-radius:8px;font-size:12px;font-weight:bold;cursor:pointer;display:flex;align-items:center;gap:4px">🖼️ تعديل البوستر</button>
          <button type="button" onclick="renderAddEpisodeForm('${item.firebaseId}')" title="إدارة الحلقات" style="background:#222;color:#fff;border:1px solid #333;padding:7px 9px;border-radius:8px;font-size:12px;cursor:pointer">📺</button>
        </div>
      </div>
    `;
  }).join("");
};'''

new_admin_manage = '''window.renderAdminManageListHtml = function(filterText = "") {
  const q = window.normalizeSearchText(filterText || "");
  const list = (window.allContent || []).filter(item => {
    if (!q) return true;
    if (item.title && window.normalizeSearchText(item.title).includes(q)) return true;
    if (item.category && window.normalizeSearchText(item.category).includes(q)) return true;
    const alts = Array.isArray(item.alternativeTitles) ? item.alternativeTitles : [];
    for (const alt of alts) {
      if (alt && window.normalizeSearchText(alt).includes(q)) return true;
    }
    return false;
  });
  if (list.length === 0) {
    return `<div style="text-align:center;color:#777;padding:14px;font-size:13px">لا توجد أعمال مطابقة</div>`;
  }
  return list.map(item => {
    let isAnimation = item.type === "animation" || item.type === "arabic" || item.type === "sports";
    let categoryLabel = item.category || (isAnimation ? "أنميشن" : "مسلسل");
    let altsCount = (Array.isArray(item.alternativeTitles) ? item.alternativeTitles.length : 0);
    let altsBadge = altsCount > 0 ? `<span style="font-size:10px;background:#064e3b;color:#34d399;border:1px solid #059669;padding:1px 6px;border-radius:10px;margin-right:4px">${altsCount} اسم بديل</span>` : "";
    return `
      <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;background:#161616;border:1px solid #282828;border-radius:12px;padding:8px 10px">
        <div style="display:flex;align-items:center;gap:10px;min-width:0;flex:1;cursor:pointer" onclick="openDetails('${item.firebaseId}')">
          <img class="poster" data-poster-fid="${item.firebaseId}" src="${item.poster}" style="width:48px;height:48px;border-radius:8px;object-fit:contain;margin:0;flex-shrink:0">
          <div style="min-width:0;flex:1">
            <div style="font-size:13px;font-weight:bold;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${item.title}</div>
            <div style="font-size:11px;color:#888;margin-top:2px">${item.year || ""} • ${categoryLabel} ${altsBadge}</div>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:6px;flex-shrink:0">
          <button type="button" onclick="openEditAlternativeTitlesModal('${item.firebaseId}')" style="background:#1b2a1e;color:#4ade80;border:1px solid #285430;padding:7px 9px;border-radius:8px;font-size:12px;font-weight:bold;cursor:pointer;display:flex;align-items:center;gap:4px" title="تعديل الأسماء البديلة">🏷️ الأسماء البديلة</button>
          <button type="button" onclick="openEditPosterModal('${item.firebaseId}')" style="background:#1a2a3a;color:#00d2ff;border:1px solid #2a4a6a;padding:7px 9px;border-radius:8px;font-size:12px;font-weight:bold;cursor:pointer;display:flex;align-items:center;gap:4px">🖼️ البوستر</button>
          <button type="button" onclick="renderAddEpisodeForm('${item.firebaseId}')" title="إدارة الحلقات" style="background:#222;color:#fff;border:1px solid #333;padding:7px 9px;border-radius:8px;font-size:12px;cursor:pointer">📺</button>
        </div>
      </div>
    `;
  }).join("");
};'''

assert old_admin_manage in html, "old_admin_manage not found"
html = html.replace(old_admin_manage, new_admin_manage, 1)

# 9. In renderAddPage, add the alternative titles manager field in Add Form
old_add_title_field = '<input id="addTitle" class="input" placeholder="اسم العمل / الأنمي">'
new_add_title_field = '''<input id="addTitle" class="input" placeholder="اسم العمل / الأنمي">
<div style="background:#161616;border:1px solid #2a2a2a;border-radius:10px;padding:12px;display:flex;flex-direction:column;gap:8px">
  <div style="display:flex;align-items:center;justify-content:space-between">
    <label style="font-size:13px;font-weight:bold;color:#00d2ff">🏷️ الأسماء البديلة للبحث (اختياري):</label>
    <span style="font-size:11px;color:#888">One Piece, ون بيس, ワンピース...</span>
  </div>
  <p style="font-size:11px;color:#888;margin:0;line-height:1.4">أضف أسماء العمل باللغة العربية والإنجليزية واليابانية وأي مرادفات للبحث:</p>
  <div style="display:flex;gap:6px">
    <input id="newAltTitleInput" class="input" style="flex:1;margin:0" placeholder="أدخل اسماً بديلاً ثم اضغط إضافة" onkeydown="if(event.key==='Enter'){event.preventDefault();window.addTempAltTitle();}">
    <button type="button" onclick="window.addTempAltTitle()" style="background:#00d2ff;color:#000;border:none;padding:8px 14px;border-radius:8px;font-size:12px;font-weight:bold;cursor:pointer;white-space:nowrap">➕ إضافة</button>
  </div>
  <div id="addAltTitlesChips" style="display:flex;flex-wrap:wrap;gap:6px;min-height:24px"></div>
</div>'''

assert old_add_title_field in html, "old_add_title_field not found"
html = html.replace(old_add_title_field, new_add_title_field, 1)

# 10. Update addNewContent to save alternativeTitles
old_add_new_content = '''window.addNewContent=async()=>{
  if(window.currentUserRole!=="ADMIN"){showPage('home');return;}
  let type=document.getElementById("addType").value,category=(document.getElementById("addCategory")?document.getElementById("addCategory").value.trim():"")||"مسلسل",title=document.getElementById("addTitle").value.trim(),year=document.getElementById("addYear").value||2024,poster=document.getElementById("addPoster").value.trim()||window.tempPosterData,video=document.getElementById("addVideo").value.trim()||window.tempVideoData,altUrl=(document.getElementById("addAltUrl")?document.getElementById("addAltUrl").value.trim():""),desc=document.getElementById("addDesc").value.trim()||"بدون وصف";
  if(!title||!poster){alert("العنوان والصورة ضروري");return;}
  video = window.normalizeVideoUrl(video);
  if(altUrl && !altUrl.startsWith("http://") && !altUrl.startsWith("https://")){
    altUrl="https://"+altUrl;
  }
  let btn=document.getElementById("addBtn");btn.disabled=true;btn.innerText="⏳ جاري الإضافة وإرسال الإشعار...";
  try{
    const newDocRef = await addDoc(colRef,{id:type+"-"+Date.now(),title,year:parseInt(year),type,category,description:desc,poster,video:video,altUrl:altUrl,episodes:[{title:"الحلقة 1",video,altUrl}],adminKey:"hamza2009",createdAt:serverTimestamp()});'''

new_add_new_content = '''window.addNewContent=async()=>{
  if(window.currentUserRole!=="ADMIN"){showPage('home');return;}
  let type=document.getElementById("addType").value,category=(document.getElementById("addCategory")?document.getElementById("addCategory").value.trim():"")||"مسلسل",title=document.getElementById("addTitle").value.trim(),year=document.getElementById("addYear").value||2024,poster=document.getElementById("addPoster").value.trim()||window.tempPosterData,video=document.getElementById("addVideo").value.trim()||window.tempVideoData,altUrl=(document.getElementById("addAltUrl")?document.getElementById("addAltUrl").value.trim():""),desc=document.getElementById("addDesc").value.trim()||"بدون وصف";
  if(!title||!poster){alert("العنوان والصورة ضروري");return;}
  video = window.normalizeVideoUrl(video);
  if(altUrl && !altUrl.startsWith("http://") && !altUrl.startsWith("https://")){
    altUrl="https://"+altUrl;
  }
  // Flush any pending alternative title in the input
  if (document.getElementById("newAltTitleInput") && document.getElementById("newAltTitleInput").value.trim()) {
    window.addTempAltTitle();
  }
  let alternativeTitles = (window.tempAltTitles || []).map(x => String(x || "").trim()).filter(Boolean);

  let btn=document.getElementById("addBtn");btn.disabled=true;btn.innerText="⏳ جاري الإضافة وإرسال الإشعار...";
  try{
    const newDocRef = await addDoc(colRef,{id:type+"-"+Date.now(),title,alternativeTitles,year:parseInt(year),type,category,description:desc,poster,video:video,altUrl:altUrl,episodes:[{title:"الحلقة 1",video,altUrl}],adminKey:"hamza2009",createdAt:serverTimestamp()});'''

assert old_add_new_content in html, "old_add_new_content not found"
html = html.replace(old_add_new_content, new_add_new_content, 1)

# Reset tempAltTitles after addNewContent success
old_add_cleanup = '''    window.tempPosterData="";
    window.tempVideoData="";
    setTimeout(()=>showPage("home"),600);'''

new_add_cleanup = '''    window.tempPosterData="";
    window.tempVideoData="";
    window.tempAltTitles=[];
    setTimeout(()=>showPage("home"),600);'''

assert old_add_cleanup in html, "old_add_cleanup not found"
html = html.replace(old_add_cleanup, new_add_cleanup, 1)

# 11. In renderAddEpisodeForm, add 🏷️ الأسماء البديلة button and epAltTitles input
old_addep_poster_btn = `<button type="button" onclick="openEditPosterModal('${item.firebaseId}')" style="background:#1a2a3a;color:#00d2ff;border:1px solid #2a4a6a;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:bold;cursor:pointer;display:inline-flex;align-items:center;gap:6px">🖼️ تعديل البوستر</button>`
new_addep_poster_btn = `<button type="button" onclick="openEditAlternativeTitlesModal('${item.firebaseId}')" style="background:#1b2a1e;color:#4ade80;border:1px solid #285430;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:bold;cursor:pointer;display:inline-flex;align-items:center;gap:6px">🏷️ تعديل الأسماء البديلة</button><button type="button" onclick="openEditPosterModal('${item.firebaseId}')" style="background:#1a2a3a;color:#00d2ff;border:1px solid #2a4a6a;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:bold;cursor:pointer;display:inline-flex;align-items:center;gap:6px">🖼️ تعديل البوستر</button>`

assert old_addep_poster_btn in html, "old_addep_poster_btn not found"
html = html.replace(old_addep_poster_btn, new_addep_poster_btn, 1)

old_ep_alturl_input = '<input id="epAltUrl" class="input" placeholder="رابط الموقع البديل (اختياري) - أدخل رابط موقع القناة أو YouTube أو Google">'
new_ep_alturl_input = '''<input id="epAltUrl" class="input" placeholder="رابط الموقع البديل (اختياري) - أدخل رابط موقع القناة أو YouTube أو Google">
<input id="epAltTitles" class="input" placeholder="الأسماء البديلة للحلقة للبحث (اختياري - مفصولة بفواصل)">'''

assert old_ep_alturl_input in html, "old_ep_alturl_input not found"
html = html.replace(old_ep_alturl_input, new_ep_alturl_input, 1)

# 12. In addEpisode, parse episode alternative titles
old_add_ep_line = '''  let baseEpisodes = Array.isArray(item.episodes) ? item.episodes : (item.video || item.altUrl ? [{ title: "البث المباشر", video: item.video || "", altUrl: item.altUrl || "" }] : []);
  let ne=[...baseEpisodes,{title:t,video:l,altUrl:alt}];'''

new_add_ep_line = '''  let epAlts = (document.getElementById("epAltTitles") ? document.getElementById("epAltTitles").value.trim() : "").split(/[,،\\n]+/).map(s => s.trim()).filter(Boolean);
  let baseEpisodes = Array.isArray(item.episodes) ? item.episodes : (item.video || item.altUrl ? [{ title: "البث المباشر", video: item.video || "", altUrl: item.altUrl || "" }] : []);
  let ne=[...baseEpisodes,{title:t,video:l,altUrl:alt,alternativeTitles:epAlts}];'''

assert old_add_ep_line in html, "old_add_ep_line not found"
html = html.replace(old_add_ep_line, new_add_ep_line, 1)

# 13. In openEditEpisodeModal and saveEditedEpisode, populate and save episode alternative titles
old_open_edit_ep_values = '''  if (titleEl) titleEl.value = ep.title || ("حلقة " + (idx + 1));
  if (videoEl) videoEl.value = ep.video || "";
  if (altEl) altEl.value = ep.altUrl || "";'''

new_open_edit_ep_values = '''  if (titleEl) titleEl.value = ep.title || ("حلقة " + (idx + 1));
  if (videoEl) videoEl.value = ep.video || "";
  if (altEl) altEl.value = ep.altUrl || "";
  const epAltsEl = document.getElementById("editEpAltTitlesInput");
  if (epAltsEl) {
    epAltsEl.value = Array.isArray(ep.alternativeTitles) ? ep.alternativeTitles.join(", ") : (ep.alternativeTitles || "");
  }'''

assert old_open_edit_ep_values in html, "old_open_edit_ep_values not found"
html = html.replace(old_open_edit_ep_values, new_open_edit_ep_values, 1)

old_save_edit_ep = '''  episodes[idx] = {
    title: title,
    video: video,
    altUrl: altUrl
  };'''

new_save_edit_ep = '''  let epAltsClean = (document.getElementById("editEpAltTitlesInput") ? document.getElementById("editEpAltTitlesInput").value.trim() : "").split(/[,،\\n]+/).map(s => s.trim()).filter(Boolean);
  episodes[idx] = {
    title: title,
    video: video,
    altUrl: altUrl,
    alternativeTitles: epAltsClean
  };'''

assert old_save_edit_ep in html, "old_save_edit_ep not found"
html = html.replace(old_save_edit_ep, new_save_edit_ep, 1)

# 14. Add the Alternative Titles management functions
alt_mgmt_code = '''
// ================= Alternative Titles (Search Aliases) Controller =================
window.tempAltTitles = [];

window.renderTempAltTitles = function() {
  const container = document.getElementById("addAltTitlesChips");
  if (!container) return;
  if (!window.tempAltTitles || window.tempAltTitles.length === 0) {
    container.innerHTML = '<span style="font-size:11px;color:#555">لم تُضف أسماء بديلة بعد (اختياري)</span>';
    return;
  }
  container.innerHTML = window.tempAltTitles.map((title, idx) => `
    <span style="display:inline-flex;align-items:center;gap:6px;background:#1e293b;color:#38bdf8;border:1px solid #0284c7;padding:4px 8px;border-radius:16px;font-size:11px">
      <span>${window.escapeDescHtml(title)}</span>
      <button type="button" onclick="window.removeTempAltTitle(${idx})" style="background:none;border:none;color:#ef4444;font-size:12px;cursor:pointer;padding:0 2px;line-height:1" title="حذف">✕</button>
    </span>
  `).join("");
};

window.addTempAltTitle = function() {
  const input = document.getElementById("newAltTitleInput");
  if (!input) return;
  const val = input.value.trim();
  if (!val) return;
  const parts = val.split(/[,،\\n]+/).map(x => x.trim()).filter(Boolean);
  for (const part of parts) {
    if (!window.tempAltTitles.includes(part)) {
      window.tempAltTitles.push(part);
    }
  }
  input.value = "";
  window.renderTempAltTitles();
};

window.removeTempAltTitle = function(idx) {
  if (idx >= 0 && idx < window.tempAltTitles.length) {
    window.tempAltTitles.splice(idx, 1);
    window.renderTempAltTitles();
  }
};

window.activeEditingAltTitlesFid = null;
window.modalAltTitles = [];

window.openEditAlternativeTitlesModal = function(fid) {
  if (window.currentUserRole !== "ADMIN") return;
  const item = getItemByFirebaseId(fid);
  if (!item) return;

  window.activeEditingAltTitlesFid = fid;
  let rawAlts = item.alternativeTitles;
  if (Array.isArray(rawAlts)) {
    window.modalAltTitles = rawAlts.map(x => String(x || "").trim()).filter(Boolean);
  } else if (typeof rawAlts === "string" && rawAlts.trim()) {
    window.modalAltTitles = rawAlts.split(/[,،\\n]+/).map(x => x.trim()).filter(Boolean);
  } else {
    window.modalAltTitles = [];
  }

  const titleEl = document.getElementById("editAltTitlesTargetTitle");
  if (titleEl) titleEl.innerText = item.title || "";

  const inputEl = document.getElementById("editAltTitleInput");
  if (inputEl) inputEl.value = "";

  const statusMsg = document.getElementById("editAltTitlesStatusMsg");
  if (statusMsg) statusMsg.innerHTML = "";

  const saveBtn = document.getElementById("saveEditAltTitlesBtn");
  if (saveBtn) {
    saveBtn.disabled = false;
    saveBtn.innerText = "💾 حفظ الأسماء البديلة";
  }

  window.renderModalAltTitles();

  const modal = document.getElementById("editAltTitlesModal");
  if (modal) modal.style.display = "flex";
};

window.closeEditAlternativeTitlesModal = function() {
  const modal = document.getElementById("editAltTitlesModal");
  if (modal) modal.style.display = "none";
  window.activeEditingAltTitlesFid = null;
  window.modalAltTitles = [];
};

window.renderModalAltTitles = function() {
  const container = document.getElementById("modalAltTitlesList");
  if (!container) return;
  if (!window.modalAltTitles || window.modalAltTitles.length === 0) {
    container.innerHTML = '<span style="font-size:12px;color:#666">لا توجد أسماء بديلة لهذا العمل بعد. أضف أسماء لتسهيل البحث.</span>';
    return;
  }
  container.innerHTML = window.modalAltTitles.map((title, idx) => `
    <span style="display:inline-flex;align-items:center;gap:6px;background:#1e293b;color:#38bdf8;border:1px solid #0284c7;padding:5px 10px;border-radius:20px;font-size:12px">
      <span>${window.escapeDescHtml(title)}</span>
      <button type="button" onclick="window.removeModalAltTitle(${idx})" style="background:none;border:none;color:#ef4444;font-size:14px;cursor:pointer;padding:0 2px;line-height:1" title="حذف">✕</button>
    </span>
  `).join("");
};

window.addModalAltTitle = function() {
  const inputEl = document.getElementById("editAltTitleInput");
  if (!inputEl) return;
  const raw = inputEl.value.trim();
  if (!raw) return;

  const parts = raw.split(/[,،\\n]+/).map(x => x.trim()).filter(Boolean);
  for (const part of parts) {
    if (!window.modalAltTitles.includes(part)) {
      window.modalAltTitles.push(part);
    }
  }
  inputEl.value = "";
  window.renderModalAltTitles();
};

window.removeModalAltTitle = function(idx) {
  if (idx >= 0 && idx < window.modalAltTitles.length) {
    window.modalAltTitles.splice(idx, 1);
    window.renderModalAltTitles();
  }
};

window.saveAlternativeTitlesFromModal = async function() {
  if (window.currentUserRole !== "ADMIN") return;
  const fid = window.activeEditingAltTitlesFid;
  if (!fid) return;
  const item = getItemByFirebaseId(fid);
  if (!item) return;

  const inputEl = document.getElementById("editAltTitleInput");
  if (inputEl && inputEl.value.trim()) {
    window.addModalAltTitle();
  }

  const saveBtn = document.getElementById("saveEditAltTitlesBtn");
  const statusMsg = document.getElementById("editAltTitlesStatusMsg");
  if (saveBtn) {
    saveBtn.disabled = true;
    saveBtn.innerText = "⏳ جاري الحفظ...";
  }
  if (statusMsg) statusMsg.innerHTML = '<span style="color:#00d2ff">⏳ جاري حفظ الأسماء البديلة في قاعدة البيانات...</span>';

  const cleanList = (window.modalAltTitles || []).map(x => String(x || "").trim()).filter(Boolean);

  try {
    await updateDoc(doc(db, "movies", fid), {
      alternativeTitles: cleanList,
      adminKey: "hamza2009",
      poster: item.poster || "https://images.unsplash.com/photo-1536240478700-b869070f9279?w=400"
    });

    item.alternativeTitles = cleanList;

    if (statusMsg) statusMsg.innerHTML = '<span style="color:#4ade80">✅ تم حفظ الأسماء البديلة بنجاح!</span>';

    setTimeout(() => {
      window.closeEditAlternativeTitlesModal();
      if (currentPage === "details") {
        openDetailsBack();
      } else if (currentPage === "add") {
        renderAddPage(true);
      } else if (currentPage === "addep") {
        renderAddEpisodeForm(fid);
      }
    }, 600);
  } catch (err) {
    console.error("Error saving alternative titles:", err);
    if (saveBtn) {
      saveBtn.disabled = false;
      saveBtn.innerText = "💾 حفظ الأسماء البديلة";
    }
    if (statusMsg) statusMsg.innerHTML = `<span style="color:#ef4444">❌ خطأ في الحفظ: ${window.escapeDescHtml(err.message)}</span>`;
  }
};
'''

# Place alt_mgmt_code near the end of script
script_end_marker = '</script>'
last_script_pos = html.rfind(script_end_marker)
assert last_script_pos != -1, "script_end_marker not found"
html = html[:last_script_pos] + alt_mgmt_code + html[last_script_pos:]

with open('app/src/main/assets/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('All updates applied successfully to index.html!')
