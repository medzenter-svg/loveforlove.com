(() => {
  'use strict';

  const root = document.getElementById('stationeryEditor');
  if (!root) return;

  const EXPECTED_CARD_COUNT = 24;
  const EXPECTED_LANGUAGE_COUNT = 6;
  const config = window.STATIONERY_CONFIG || [];
  const languages = window.STATIONERY_LANGUAGES || [];
  const isPaid = root.dataset.paid === 'true';
  const productSlug = root.dataset.productSlug || 'amalfi-wedding-suite';
  const orderId = root.dataset.orderId || '';
  const designId = root.dataset.designId || 'amalfi';

  if (config.length !== EXPECTED_CARD_COUNT) throw new Error(`Stationery configuration must contain exactly ${EXPECTED_CARD_COUNT} items; received ${config.length}.`);
  if (languages.length !== EXPECTED_LANGUAGE_COUNT) throw new Error(`Stationery editor must contain exactly ${EXPECTED_LANGUAGE_COUNT} languages.`);
  config.forEach((card, index) => {
    if (card.number !== index + 1) throw new Error(`Invalid card order at ${card.id}.`);
    languages.forEach((language) => {
      if (!card.translations || !card.translations[language]) throw new Error(`Missing ${language} translation for ${card.id}.`);
    });
  });

  const state = { language: root.dataset.language || 'en', activeCardId: config[0].id, activeView: config[0].views[0] || 'front', values: {} };
  const els = {
    languageSwitcher: document.getElementById('languageSwitcher'), navigation: document.getElementById('cardNavigation'), gallery: document.getElementById('previewGallery'),
    editorWorkspace: document.getElementById('editorWorkspace'), viewSwitcher: document.getElementById('viewSwitcher'), screenCard: document.getElementById('screenCard'),
    screenContent: document.getElementById('screenCardContent'), sizeNote: document.getElementById('physicalSizeNote'), fields: document.getElementById('editorFields'),
    status: document.getElementById('editorStatus'), saveButton: document.getElementById('saveEditorData'), printButton: document.getElementById('printCard'),
  };

  const ENVELOPE_FIELDS = {
    front: ['recipient_name', 'recipient_address'],
    back: ['return_names', 'return_address'],
    flap: ['flap_note'],
    liner: ['liner_text'],
  };

  function designBackgroundUrl(card) { return `/static/designs/${encodeURIComponent(designId)}/${encodeURIComponent(card.id)}.webp`; }
  function getCard(cardId = state.activeCardId) { return config.find((card) => card.id === cardId) || null; }
  function defaultsFor(card, language = state.language) { return card.translations[language]; }
  function valuesFor(card) { return { ...defaultsFor(card), ...((((state.values[card.id] || {})[state.language]) || {})) }; }
  function setValue(card, key, value) {
    if (!isPaid) return;
    state.values[card.id] = state.values[card.id] || {};
    state.values[card.id][state.language] = state.values[card.id][state.language] || {};
    state.values[card.id][state.language][key] = value;
  }
  function isEnvelope(card) { return card && card.id === '24_envelope_suite'; }
  function isWebsite(card) { return card && card.id === '05_wedding_website'; }
  function visibleFields(card) { return isEnvelope(card) ? (ENVELOPE_FIELDS[state.activeView] || card.fields) : card.fields; }

  function humanSize(card) {
    if (isEnvelope(card) && card.envelope_spec) {
      const s = card.envelope_spec;
      return `flat ${s.flat_w_mm} × ${s.flat_h_mm} mm · finished ${s.finished_w_mm} × ${s.finished_h_mm} mm · bleed ${card.bleed_mm} mm`;
    }
    const folded = card.fold && card.finished_w_mm ? ` · folded ${card.finished_w_mm} × ${card.finished_h_mm} mm` : '';
    return `${card.w_mm} × ${card.h_mm} mm · bleed ${card.bleed_mm} mm${folded}`;
  }

  function fieldLabel(key) { return key.replaceAll('_', ' ').replace(/\b\w/g, (m) => m.toUpperCase()); }

  function renderLanguages() {
    els.languageSwitcher.innerHTML = '';
    languages.forEach((language) => {
      const button = document.createElement('button'); button.type = 'button';
      button.className = `language-button${language === state.language ? ' is-active' : ''}`; button.dataset.language = language; button.textContent = language.toUpperCase();
      button.addEventListener('click', () => { state.language = language; renderAll(); });
      els.languageSwitcher.appendChild(button);
    });
  }

  function renderNavigation() {
    els.navigation.innerHTML = '';
    config.forEach((card) => {
      const button = document.createElement('button'); button.type = 'button'; button.className = `card-nav-button${card.id === state.activeCardId ? ' is-active' : ''}`;
      const translatedTitle = defaultsFor(card).title || card.name;
      button.innerHTML = `<strong>${String(card.number).padStart(2, '0')} · ${escapeHtml(translatedTitle)}</strong><span class="card-nav-size">${escapeHtml(humanSize(card))}</span>`;
      button.addEventListener('click', () => selectCard(card.id)); els.navigation.appendChild(button);
    });
  }

  function renderGallery() {
    els.gallery.innerHTML = '';
    config.forEach((card) => {
      const tile = document.createElement('article'); tile.className = `gallery-card${isEnvelope(card) ? ' is-envelope' : ''}${isWebsite(card) ? ' is-website' : ''}`;
      tile.style.backgroundImage = `url("${designBackgroundUrl(card)}")`;
      const t = defaultsFor(card);
      if (isWebsite(card)) {
        tile.innerHTML = `<div class="gallery-number">${String(card.number).padStart(2, '0')}</div><div class="gallery-title">${escapeHtml(t.title || card.name)}</div><div class="gallery-names">${escapeHtml(t.names || '')}</div><div class="gallery-location">${escapeHtml(t.website || '')}</div><div class="gallery-size">${escapeHtml(humanSize(card))}</div>`;
      } else {
        tile.innerHTML = `<div class="gallery-number">${String(card.number).padStart(2, '0')}</div><div class="gallery-title">${escapeHtml(t.title || card.name)}</div><div class="gallery-names">${escapeHtml(t.names || '')}</div><div class="gallery-date">${escapeHtml(t.date || '')}</div><div class="gallery-location">${escapeHtml(t.location || '')}</div><div class="gallery-size">${escapeHtml(humanSize(card))}</div>`;
      }
      tile.addEventListener('click', () => selectCard(card.id)); els.gallery.appendChild(tile);
    });
  }

  function selectCard(cardId) {
    const card = getCard(cardId); if (!card) return;
    state.activeCardId = cardId; state.activeView = card.views[0] || 'front'; renderAll();
    if (isPaid && els.editorWorkspace) els.editorWorkspace.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function renderViews(card) {
    els.viewSwitcher.innerHTML = '';
    card.views.forEach((view) => {
      const button = document.createElement('button'); button.type = 'button'; button.className = `view-button${view === state.activeView ? ' is-active' : ''}`; button.textContent = view.replaceAll('_', ' ');
      button.addEventListener('click', () => { state.activeView = view; renderViews(card); renderPreview(card); renderFields(card); });
      els.viewSwitcher.appendChild(button);
    });
  }

  function screenDimensions(card) {
    const maxW = 650, maxH = 500, ratio = card.w_mm / card.h_mm;
    let width = maxW, height = width / ratio;
    if (height > maxH) { height = maxH; width = height * ratio; }
    return { width, height };
  }

  function configureEnvelopePreview(card) {
    els.screenCard.classList.toggle('is-envelope', isEnvelope(card));
    if (!isEnvelope(card) || !card.envelope_spec) {
      els.screenContent.style.removeProperty('left'); els.screenContent.style.removeProperty('right'); els.screenContent.style.removeProperty('top'); els.screenContent.style.removeProperty('bottom');
      return;
    }
    const s = card.envelope_spec;
    const leftPct = (s.side_flap_mm / s.flat_w_mm) * 100;
    const rightPct = leftPct;
    const flapBottomPct = (s.seal_flap_mm / s.flat_h_mm) * 100;
    const backBottomPct = ((s.back_panel_top_mm + s.panel_h_mm) / s.flat_h_mm) * 100;
    const frontTopPct = (s.front_panel_top_mm / s.flat_h_mm) * 100;
    const safeXPct = (s.safe_inset_mm / s.flat_w_mm) * 100;
    const safeYPct = (s.safe_inset_mm / s.flat_h_mm) * 100;

    if (state.activeView === 'front') {
      els.screenContent.style.left = `${leftPct + safeXPct}%`;
      els.screenContent.style.right = `${rightPct + safeXPct}%`;
      els.screenContent.style.top = `${frontTopPct + safeYPct}%`;
      els.screenContent.style.bottom = `${safeYPct}%`;
    } else if (state.activeView === 'back') {
      els.screenContent.style.left = `${leftPct + safeXPct}%`;
      els.screenContent.style.right = `${rightPct + safeXPct}%`;
      els.screenContent.style.top = `${flapBottomPct + safeYPct}%`;
      els.screenContent.style.bottom = `${100 - backBottomPct + safeYPct}%`;
    } else if (state.activeView === 'flap') {
      els.screenContent.style.left = `${leftPct + safeXPct}%`;
      els.screenContent.style.right = `${rightPct + safeXPct}%`;
      els.screenContent.style.top = `${safeYPct}%`;
      els.screenContent.style.bottom = `${100 - flapBottomPct + safeYPct}%`;
    } else {
      els.screenContent.style.left = `${leftPct + safeXPct}%`;
      els.screenContent.style.right = `${rightPct + safeXPct}%`;
      els.screenContent.style.top = `${flapBottomPct + safeYPct}%`;
      els.screenContent.style.bottom = `${100 - backBottomPct + safeYPct}%`;
    }
  }

  function appendPreviewNode(card, className, key, value, editable = false) {
    if (value == null || value === '') return null;
    const node = document.createElement('div'); node.className = className; if (key) node.dataset.key = key; node.textContent = String(value);
    if (editable && isPaid && key) {
      node.contentEditable = 'true'; node.spellcheck = false;
      node.addEventListener('input', () => { const text = node.textContent.trim(); setValue(card, key, text); syncInput(key, text); });
    }
    els.screenContent.appendChild(node); return node;
  }

  function renderWebsitePreview(card, values) {
    const copy = defaultsFor(card);
    appendPreviewNode(card, 'screen-card-title website-title', null, copy.title, false);
    appendPreviewNode(card, 'screen-card-field website-names', 'names', values.names, true);
    appendPreviewNode(card, 'screen-card-static website-info', null, copy.info, false);
    appendPreviewNode(card, 'screen-card-field website-url', 'website', values.website, true);
    const passwordLine = document.createElement('div'); passwordLine.className = 'website-password-line';
    const label = document.createElement('span'); label.className = 'website-password-label'; label.textContent = copy.password_label || '';
    const password = document.createElement('span'); password.className = 'website-password-value'; password.dataset.key = 'password'; password.textContent = values.password || '';
    if (isPaid) {
      password.contentEditable = 'true'; password.spellcheck = false;
      password.addEventListener('input', () => { const text = password.textContent.trim(); setValue(card, 'password', text); syncInput('password', text); });
    }
    passwordLine.append(label, password); els.screenContent.appendChild(passwordLine);
  }

  function renderPreview(card) {
    const size = screenDimensions(card);
    els.screenCard.style.width = `${size.width}px`; els.screenCard.style.height = `${size.height}px`; els.screenCard.style.backgroundImage = `url("${designBackgroundUrl(card)}")`;
    els.screenCard.dataset.cardId = card.id; els.screenCard.dataset.view = state.activeView; els.screenCard.classList.toggle('is-website', isWebsite(card)); configureEnvelopePreview(card);
    els.screenContent.classList.toggle('is-website-content', isWebsite(card));
    els.sizeNote.textContent = `${humanSize(card)} · view: ${state.activeView}`;
    const values = valuesFor(card); els.screenContent.innerHTML = '';
    if (isWebsite(card)) { renderWebsitePreview(card, values); return; }
    visibleFields(card).forEach((key) => {
      const value = values[key]; if (value == null || value === '') return;
      const node = document.createElement('div'); node.className = key === 'title' ? 'screen-card-title' : 'screen-card-field'; node.dataset.key = key; node.textContent = String(value);
      if (isPaid) { node.contentEditable = 'true'; node.spellcheck = false; node.addEventListener('input', () => { const text = node.textContent.trim(); setValue(card, key, text); syncInput(key, text); }); }
      els.screenContent.appendChild(node);
    });
  }

  function renderFields(card) {
    els.fields.innerHTML = ''; const values = valuesFor(card);
    visibleFields(card).forEach((key) => {
      const row = document.createElement('div'); row.className = 'editor-field';
      const label = document.createElement('label'); label.htmlFor = `field-${key}`; label.textContent = fieldLabel(key);
      const value = values[key] == null ? '' : String(values[key]); const isLong = value.length > 70 || key.includes('greeting') || key.includes('program') || key.includes('instructions') || key.includes('payment') || key.includes('address');
      const control = isLong ? document.createElement('textarea') : document.createElement('input'); control.id = `field-${key}`; control.dataset.key = key; control.value = value; control.disabled = !isPaid;
      control.addEventListener('input', () => { setValue(card, key, control.value); renderPreview(card); }); row.append(label, control); els.fields.appendChild(row);
    });
  }

  function syncInput(key, value) { const control = els.fields.querySelector(`[data-key="${CSS.escape(key)}"]`); if (control) control.value = value; }

  function buildPayload() {
    const cards = config.map((card) => ({ id: card.id, view: card.id === state.activeCardId ? state.activeView : card.views[0], values: valuesFor(card) }));
    if (cards.length !== EXPECTED_CARD_COUNT) throw new Error(`Payload must contain exactly ${EXPECTED_CARD_COUNT} cards.`);
    return { product_slug: productSlug, order_id: orderId, design_id: designId, language: state.language, card_count: EXPECTED_CARD_COUNT, cards };
  }

  async function savePayload() {
    if (!isPaid) return; els.status.textContent = 'Saving…';
    try {
      const response = await fetch('/api/stationery/payload', { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(buildPayload()) });
      const result = await response.json(); if (!response.ok) throw new Error(result.error || `HTTP ${response.status}`);
      if (result.card_count !== EXPECTED_CARD_COUNT || result.cards.length !== EXPECTED_CARD_COUNT) throw new Error('Backend returned an invalid card count.');
      localStorage.setItem(`stationery:${productSlug}:${orderId}`, JSON.stringify(state.values)); els.status.textContent = `Saved. Exactly ${result.card_count} items validated.`;
    } catch (error) { els.status.textContent = `Save failed: ${error.message}`; }
  }

  async function generatePdfPackage() {
    if (!isPaid) return; els.printButton.disabled = true; els.saveButton.disabled = true; els.status.textContent = 'Generating 24 print-ready PDF files…';
    try {
      const response = await fetch('/api/generate-pdf', { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(buildPayload()) });
      const result = await response.json(); if (!response.ok) throw new Error(result.message || result.error || `HTTP ${response.status}`);
      if (result.card_count !== EXPECTED_CARD_COUNT || !result.download_url) throw new Error('Backend returned an invalid PDF package response.');
      els.status.textContent = 'PDF package is ready. Download is starting…'; window.location.assign(result.download_url);
    } catch (error) { els.status.textContent = `PDF generation failed: ${error.message}`; }
    finally { els.printButton.disabled = !isPaid; els.saveButton.disabled = !isPaid; }
  }

  function loadLocalEdits() {
    if (!isPaid) return;
    try { const saved = JSON.parse(localStorage.getItem(`stationery:${productSlug}:${orderId}`) || '{}'); state.values = saved && typeof saved === 'object' ? saved : {}; }
    catch (_) { state.values = {}; }
  }

  function renderAll() {
    const card = getCard(); renderLanguages(); renderNavigation(); renderGallery(); renderViews(card); renderPreview(card); renderFields(card); els.saveButton.disabled = !isPaid; els.printButton.disabled = !isPaid;
  }

  function escapeHtml(value) { return String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;'); }

  loadLocalEdits(); els.saveButton.addEventListener('click', savePayload); els.printButton.addEventListener('click', generatePdfPackage); renderAll();
})();
