(() => {
  const root = document.querySelector('[data-suite-editor]');
  if (!root) return;

  const locales = JSON.parse(root.dataset.locales || '{}');
  const rtlLanguages = JSON.parse(root.dataset.rtl || '[]');
  const storageKey = root.dataset.storageKey || 'loveforlove-suite';
  const languageSelect = document.getElementById('languagePreset');
  const status = document.getElementById('editorSaveStatus');

  const labelKeys = [
    'invitation','details','venue','address','rsvp','reply_by','menu','first','second','third','dessert',
    'table','place','program','ceremony','cocktails','dinner','dancing','thank_you','join_us'
  ];

  const defaultValue = (field) => (field.dataset.default || '').replace(/\\n/g, '\n');

  const setBoundText = (key, value) => {
    document.querySelectorAll(`[data-bind="${key}"]`).forEach(el => {
      el.textContent = value || '';
    });
  };

  const setLabelText = (key, value) => {
    document.querySelectorAll(`[data-label="${key}"]`).forEach(el => {
      el.textContent = value || '';
    });
  };

  const syncField = (field) => {
    if (!field.id) return;
    if (field.dataset.bindKey) setBoundText(field.dataset.bindKey, field.value);
    if (field.dataset.labelKey) setLabelText(field.dataset.labelKey, field.value);
  };

  const saveState = () => {
    const state = {};
    root.querySelectorAll('input[id], textarea[id], select[id]').forEach(field => {
      state[field.id] = field.value;
    });
    localStorage.setItem(storageKey, JSON.stringify(state));
    if (status) {
      status.textContent = 'Saved on this device';
      clearTimeout(saveState._timer);
      saveState._timer = setTimeout(() => status.textContent = '', 1400);
    }
  };

  const applyDirection = (language) => {
    const dir = rtlLanguages.includes(language) ? 'rtl' : 'ltr';
    document.querySelectorAll('.suite-card').forEach(card => card.setAttribute('dir', dir));
  };

  const applyLanguage = (language, shouldSave = true) => {
    const preset = locales[language];
    if (!preset) return;
    labelKeys.forEach(key => {
      const field = document.querySelector(`[data-label-key="${key}"]`);
      if (!field || preset[key] === undefined) return;
      field.value = preset[key];
      syncField(field);
    });
    applyDirection(language);
    if (shouldSave) saveState();
  };

  const restoreState = () => {
    let state = null;
    try { state = JSON.parse(localStorage.getItem(storageKey) || 'null'); } catch (_) {}
    if (!state) return false;
    Object.entries(state).forEach(([id, value]) => {
      const field = document.getElementById(id);
      if (!field) return;
      field.value = value;
      syncField(field);
    });
    applyDirection(state.languagePreset || 'en');
    return true;
  };

  root.querySelectorAll('input[id], textarea[id]').forEach(field => {
    field.addEventListener('input', () => {
      syncField(field);
      saveState();
    });
  });

  if (languageSelect) {
    languageSelect.addEventListener('change', () => applyLanguage(languageSelect.value));
  }

  document.getElementById('resetSuite')?.addEventListener('click', () => {
    localStorage.removeItem(storageKey);
    root.querySelectorAll('[data-default]').forEach(field => {
      field.value = defaultValue(field);
      syncField(field);
    });
    if (languageSelect) {
      languageSelect.value = 'en';
      applyLanguage('en', false);
    }
    saveState();
  });

  document.getElementById('printSuite')?.addEventListener('click', () => window.print());

  const restored = restoreState();
  if (!restored) {
    root.querySelectorAll('[data-default]').forEach(field => {
      if (!field.value) field.value = defaultValue(field);
      syncField(field);
    });
    applyLanguage(languageSelect?.value || 'en', false);
  }
})();
