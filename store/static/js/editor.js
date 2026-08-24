(() => {
  'use strict';

  const root = document.getElementById('stationeryEditor');
  if (!root) return;

  const config = window.STATIONERY_CONFIG || [];
  const languages = window.STATIONERY_LANGUAGES || ['en', 'de', 'fr', 'it', 'es', 'ru'];
  const isPaid = root.dataset.paid === 'true';
  const productSlug = root.dataset.productSlug || 'amalfi-wedding-suite';
  const orderId = root.dataset.orderId || '';

  const state = {
    language: root.dataset.language || 'en',
    activeCardId: config[0] ? config[0].id : null,
    activeView: config[0] && config[0].views.length ? config[0].views[0] : 'front',
    values: {},
  };

  const els = {
    languageSwitcher: document.getElementById('languageSwitcher'),
    navigation: document.getElementById('cardNavigation'),
    gallery: document.getElementById('previewGallery'),
    editorWorkspace: document.getElementById('editorWorkspace'),
    viewSwitcher: document.getElementById('viewSwitcher'),
    screenCard: document.getElementById('screenCard'),
    screenContent: document.getElementById('screenCardContent'),
    brand: document.getElementById('screenCardBrand'),
    sizeNote: document.getElementById('physicalSizeNote'),
    fields: document.getElementById('editorFields'),
    status: document.getElementById('editorStatus'),
    saveButton: document.getElementById('saveEditorData'),
    printButton: document.getElementById('printCard'),
    printHost: document.getElementById('printHost'),
  };

  function getCard(cardId = state.activeCardId) {
    return config.find((card) => card.id === cardId) || null;
  }

  function defaultsFor(card, language = state.language) {
    return (card && card.translations && card.translations[language]) || {};
  }

  function valuesFor(card) {
    const defaults = defaultsFor(card);
    const edited = (((state.values[card.id] || {})[state.language]) || {});
    return { ...defaults, ...edited };
  }

  function setValue(card, key, value) {
    if (!isPaid || card.spec_locked) return;
    state.values[card.id] = state.values[card.id] || {};
    state.values[card.id][state.language] = state.values[card.id][state.language] || {};
    state.values[card.id][state.language][key] = value;
  }

  function humanSize(card) {
    if (!card || card.spec_locked || card.w_mm == null || card.h_mm == null) return 'Print specification required';
    const folded = card.fold && card.finished_w_mm ? ` · folded ${card.finished_w_mm} × ${card.finished_h_mm} mm` : '';
    return `${card.w_mm} × ${card.h_mm} mm · bleed ${card.bleed_mm} mm${folded}`;
  }

  function fieldLabel(key) {
    return key.replaceAll('_', ' ').replace(/\b\w/g, (m) => m.toUpperCase());
  }

  function renderLanguages() {
    els.languageSwitcher.innerHTML = '';
    languages.forEach((language) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `language-button${language === state.language ? ' is-active' : ''}`;
      button.dataset.language = language;
      button.textContent = language.toUpperCase();
      button.addEventListener('click', () => {
        state.language = language;
        renderAll();
      });
      els.languageSwitcher.appendChild(button);
    });
  }

  function renderNavigation() {
    els.navigation.innerHTML = '';
    config.forEach((card) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `card-nav-button${card.id === state.activeCardId ? ' is-active' : ''}${card.spec_locked ? ' is-locked' : ''}`;
      button.disabled = Boolean(card.spec_locked);
      const translatedTitle = defaultsFor(card).title || card.name;
      button.innerHTML = `<strong>${String(card.number).padStart(2, '0')} · ${escapeHtml(translatedTitle)}</strong><span class="card-nav-size">${escapeHtml(humanSize(card))}</span>`;
      button.addEventListener('click', () => selectCard(card.id));
      els.navigation.appendChild(button);
    });
  }

  function renderGallery() {
    if (!els.gallery) return;
    els.gallery.innerHTML = '';
    config.forEach((card) => {
      const tile = document.createElement('article');
      tile.className = `gallery-card${card.spec_locked ? ' is-locked' : ''}`;
      const t = defaultsFor(card);
      if (card.spec_locked) {
        tile.innerHTML = `<div class="gallery-number">${String(card.number).padStart(2, '0')}</div><div class="gallery-title">Specification required</div><div class="gallery-size">Not printable until approved</div>`;
      } else {
        tile.innerHTML = `
          <div class="gallery-number">${String(card.number).padStart(2, '0')}</div>
          <div class="gallery-title">${escapeHtml(t.title || card.name)}</div>
          <div class="gallery-names">${escapeHtml(t.names || '')}</div>
          <div class="gallery-date">${escapeHtml(t.date || '')}</div>
          <div class="gallery-location">${escapeHtml(t.location || '')}</div>
          <div class="gallery-size">${escapeHtml(humanSize(card))}</div>`;
        tile.addEventListener('click', () => selectCard(card.id));
      }
      els.gallery.appendChild(tile);
    });
  }

  function selectCard(cardId) {
    const card = getCard(cardId);
    if (!card || card.spec_locked) return;
    state.activeCardId = cardId;
    state.activeView = card.views[0] || 'front';
    renderAll();
    if (isPaid && els.editorWorkspace) els.editorWorkspace.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function renderViews(card) {
    els.viewSwitcher.innerHTML = '';
    (card.views || []).forEach((view) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `view-button${view === state.activeView ? ' is-active' : ''}`;
      button.textContent = view.replaceAll('_', ' ');
      button.addEventListener('click', () => {
        state.activeView = view;
        renderViews(card);
        renderPreview(card);
      });
      els.viewSwitcher.appendChild(button);
    });
  }

  function screenDimensions(card) {
    const maxW = 650;
    const maxH = 500;
    const ratio = card.w_mm / card.h_mm;
    let width = maxW;
    let height = width / ratio;
    if (height > maxH) {
      height = maxH;
      width = height * ratio;
    }
    return { width, height };
  }

  function renderPreview(card) {
    if (card.spec_locked) {
      els.screenContent.innerHTML = '<div class="locked-spec">Print specification is not approved.</div>';
      return;
    }

    const size = screenDimensions(card);
    els.screenCard.style.width = `${size.width}px`;
    els.screenCard.style.height = `${size.height}px`;
    els.screenCard.dataset.cardId = card.id;
    els.screenCard.dataset.view = state.activeView;
    els.sizeNote.textContent = `${humanSize(card)} · view: ${state.activeView}`;

    const values = valuesFor(card);
    els.screenContent.innerHTML = '';

    card.fields.forEach((key) => {
      const value = values[key];
      if (value == null || value === '') return;
      const node = document.createElement(key === 'title' ? 'div' : 'div');
      node.className = key === 'title' ? 'screen-card-title' : 'screen-card-field';
      node.dataset.key = key;
      node.textContent = String(value);
      if (isPaid) {
        node.contentEditable = 'true';
        node.spellcheck = false;
        node.addEventListener('input', () => {
          setValue(card, key, node.textContent.trim());
          syncInput(key, node.textContent.trim());
        });
      }
      els.screenContent.appendChild(node);
    });
  }

  function renderFields(card) {
    els.fields.innerHTML = '';
    const values = valuesFor(card);
    card.fields.forEach((key) => {
      const row = document.createElement('div');
      row.className = 'editor-field';
      const label = document.createElement('label');
      label.htmlFor = `field-${key}`;
      label.textContent = fieldLabel(key);
      const value = values[key] == null ? '' : String(values[key]);
      const control = value.length > 70 || key.includes('greeting') || key.includes('program') || key.includes('instructions') || key.includes('payment') ? document.createElement('textarea') : document.createElement('input');
      control.id = `field-${key}`;
      control.dataset.key = key;
      control.value = value;
      control.disabled = !isPaid;
      control.addEventListener('input', () => {
        setValue(card, key, control.value);
        renderPreview(card);
      });
      row.append(label, control);
      els.fields.appendChild(row);
    });
  }

  function syncInput(key, value) {
    const control = els.fields.querySelector(`[data-key="${CSS.escape(key)}"]`);
    if (control) control.value = value;
  }

  function buildPayload() {
    return {
      product_slug: productSlug,
      order_id: orderId,
      language: state.language,
      cards: config.filter((card) => !card.spec_locked).map((card) => ({
        id: card.id,
        view: card.id === state.activeCardId ? state.activeView : (card.views[0] || 'front'),
        values: valuesFor(card),
      })),
    };
  }

  async function savePayload() {
    if (!isPaid) return;
    els.status.textContent = 'Saving…';
    try {
      const response = await fetch('/api/stationery/payload', {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(buildPayload()),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || `HTTP ${response.status}`);
      localStorage.setItem(`stationery:${productSlug}:${orderId}`, JSON.stringify(state.values));
      els.status.textContent = `Saved. ${result.cards.length} printable items validated.`;
    } catch (error) {
      els.status.textContent = `Save failed: ${error.message}`;
    }
  }

  function preparePrint(card) {
    if (!isPaid || !card || card.spec_locked) return false;
    const bleed = Number(card.bleed_mm || 0);
    const pageW = Number(card.w_mm) + bleed * 2;
    const pageH = Number(card.h_mm) + bleed * 2;
    let style = document.getElementById('dynamicPageSize');
    if (!style) {
      style = document.createElement('style');
      style.id = 'dynamicPageSize';
      document.head.appendChild(style);
    }
    style.textContent = `@page{size:${pageW}mm ${pageH}mm;margin:0} @media print{html,body{width:${pageW}mm!important;height:${pageH}mm!important}}`;

    const values = valuesFor(card);
    els.printHost.innerHTML = '';
    const sheet = document.createElement('section');
    sheet.className = 'print-sheet';
    sheet.style.width = `${pageW}mm`;
    sheet.style.height = `${pageH}mm`;
    const trim = document.createElement('div');
    trim.className = 'print-trim';
    trim.style.left = `${bleed}mm`;
    trim.style.top = `${bleed}mm`;
    trim.style.width = `${card.w_mm}mm`;
    trim.style.height = `${card.h_mm}mm`;
    trim.innerHTML = `<div class="print-card-content">${card.fields.map((key) => values[key] ? `<div data-key="${escapeHtml(key)}">${escapeHtml(String(values[key]))}</div>` : '').join('')}<div class="print-brand">loveforlove.com</div></div>`;
    sheet.appendChild(trim);
    els.printHost.appendChild(sheet);
    return true;
  }

  function printActiveCard() {
    const card = getCard();
    if (!preparePrint(card)) return;
    window.print();
  }

  function loadLocalEdits() {
    if (!isPaid) return;
    try {
      const saved = JSON.parse(localStorage.getItem(`stationery:${productSlug}:${orderId}`) || '{}');
      state.values = saved && typeof saved === 'object' ? saved : {};
    } catch (_) {
      state.values = {};
    }
  }

  function renderAll() {
    const card = getCard();
    renderLanguages();
    renderNavigation();
    renderGallery();
    if (!card) return;
    renderViews(card);
    renderPreview(card);
    renderFields(card);
    els.saveButton.disabled = !isPaid;
    els.printButton.disabled = !isPaid || card.spec_locked;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  loadLocalEdits();
  els.saveButton.addEventListener('click', savePayload);
  els.printButton.addEventListener('click', printActiveCard);
  renderAll();
})();
