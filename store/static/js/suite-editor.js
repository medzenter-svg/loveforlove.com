(() => {
  const root = document.querySelector('[data-suite-editor]');
  if (!root) return;

  const locales = JSON.parse(root.dataset.locales || '{}');
  const rtlLanguages = JSON.parse(root.dataset.rtl || '[]');
  const storageKey = root.dataset.storageKey || 'loveforlove-suite';
  const languageSelect = document.getElementById('languagePreset');
  const status = document.getElementById('editorSaveStatus');
  const labelKeys = Object.keys(locales.en || {});

  const installWeekendPrograms = () => {
    const optionalSection = document.getElementById('useAccommodation')?.closest('.editor-section');
    if (optionalSection && !document.getElementById('useDayOne')) {
      optionalSection.insertAdjacentHTML('beforeend', `
        <label class="optional-control"><input type="checkbox" id="useDayOne" data-toggle-piece="day-one" data-default="true" checked><span><strong>Wedding program — Day 1</strong><br>Optional first-day schedule for welcome events, dinner and evening activities.</span></label>
        <label class="optional-control"><input type="checkbox" id="useDayTwo" data-toggle-piece="day-two" data-default="true" checked><span><strong>Wedding program — Day 2</strong><br>Optional second-day schedule for brunch, activities and farewell events.</span></label>
      `);
    }

    const programSection = document.getElementById('thankMessage')?.closest('.editor-section');
    if (programSection && !document.getElementById('dayOneDate')) {
      programSection.insertAdjacentHTML('afterend', `
        <div class="editor-section" id="weekendProgramEditor">
          <div class="editor-section-title">Two-day wedding program</div>
          <p class="editor-note">Both cards are optional. Every event name and time can be changed.</p>
          <label class="editor-field"><span>Day 1 date</span><input id="dayOneDate" data-bind-key="dayOneDate" data-default="13 June 2027" value="13 June 2027"></label>
          <label class="editor-field"><span>Day 1 · event 1 time</span><input id="dayOneTime1" data-bind-key="dayOneTime1" data-default="5:00 PM" value="5:00 PM"></label>
          <label class="editor-field"><span>Day 1 · event 1</span><input id="dayOneEvent1" data-bind-key="dayOneEvent1" data-default="Welcome Aperitivo" value="Welcome Aperitivo"></label>
          <label class="editor-field"><span>Day 1 · event 2 time</span><input id="dayOneTime2" data-bind-key="dayOneTime2" data-default="7:30 PM" value="7:30 PM"></label>
          <label class="editor-field"><span>Day 1 · event 2</span><input id="dayOneEvent2" data-bind-key="dayOneEvent2" data-default="Welcome Dinner" value="Welcome Dinner"></label>
          <label class="editor-field"><span>Day 1 · event 3 time</span><input id="dayOneTime3" data-bind-key="dayOneTime3" data-default="9:30 PM" value="9:30 PM"></label>
          <label class="editor-field"><span>Day 1 · event 3</span><input id="dayOneEvent3" data-bind-key="dayOneEvent3" data-default="Cocktails & Music" value="Cocktails & Music"></label>
          <label class="editor-field"><span>Day 1 · event 4 time</span><input id="dayOneTime4" data-bind-key="dayOneTime4" data-default="11:30 PM" value="11:30 PM"></label>
          <label class="editor-field"><span>Day 1 · event 4</span><input id="dayOneEvent4" data-bind-key="dayOneEvent4" data-default="Late Night" value="Late Night"></label>

          <label class="editor-field"><span>Day 2 date</span><input id="dayTwoDate" data-bind-key="dayTwoDate" data-default="14 June 2027" value="14 June 2027"></label>
          <label class="editor-field"><span>Day 2 · event 1 time</span><input id="dayTwoTime1" data-bind-key="dayTwoTime1" data-default="10:30 AM" value="10:30 AM"></label>
          <label class="editor-field"><span>Day 2 · event 1</span><input id="dayTwoEvent1" data-bind-key="dayTwoEvent1" data-default="Brunch" value="Brunch"></label>
          <label class="editor-field"><span>Day 2 · event 2 time</span><input id="dayTwoTime2" data-bind-key="dayTwoTime2" data-default="1:00 PM" value="1:00 PM"></label>
          <label class="editor-field"><span>Day 2 · event 2</span><input id="dayTwoEvent2" data-bind-key="dayTwoEvent2" data-default="Lake Activity" value="Lake Activity"></label>
          <label class="editor-field"><span>Day 2 · event 3 time</span><input id="dayTwoTime3" data-bind-key="dayTwoTime3" data-default="5:00 PM" value="5:00 PM"></label>
          <label class="editor-field"><span>Day 2 · event 3</span><input id="dayTwoEvent3" data-bind-key="dayTwoEvent3" data-default="Farewell Aperitivo" value="Farewell Aperitivo"></label>
          <label class="editor-field"><span>Day 2 · event 4 time</span><input id="dayTwoTime4" data-bind-key="dayTwoTime4" data-default="7:00 PM" value="7:00 PM"></label>
          <label class="editor-field"><span>Day 2 · event 4</span><input id="dayTwoEvent4" data-bind-key="dayTwoEvent4" data-default="Farewell" value="Farewell"></label>
        </div>
      `);
    }

    const grid = root.querySelector('.suite-grid');
    if (grid && !grid.querySelector('[data-piece="day-one"]')) {
      grid.insertAdjacentHTML('beforeend', `
        <div class="suite-piece-wrap" data-piece="day-one">
          <div class="suite-piece-name">Optional · Wedding Program · Day 1</div>
          <article class="suite-card card-portrait">
            <div class="suite-ornament">✦</div>
            <div class="suite-kicker" data-label="weekend_program">Wedding Weekend</div>
            <div class="suite-names" style="font-size:25px" data-label="day_one">Day One</div>
            <div class="suite-date" data-bind="dayOneDate">13 June 2027</div><div class="suite-rule"></div>
            <div class="program-row"><span class="program-time" data-bind="dayOneTime1">5:00 PM</span><span data-bind="dayOneEvent1">Welcome Aperitivo</span></div>
            <div class="program-row"><span class="program-time" data-bind="dayOneTime2">7:30 PM</span><span data-bind="dayOneEvent2">Welcome Dinner</span></div>
            <div class="program-row"><span class="program-time" data-bind="dayOneTime3">9:30 PM</span><span data-bind="dayOneEvent3">Cocktails & Music</span></div>
            <div class="program-row"><span class="program-time" data-bind="dayOneTime4">11:30 PM</span><span data-bind="dayOneEvent4">Late Night</span></div>
          </article>
        </div>
        <div class="suite-piece-wrap" data-piece="day-two">
          <div class="suite-piece-name">Optional · Wedding Program · Day 2</div>
          <article class="suite-card card-portrait">
            <div class="suite-ornament">✦</div>
            <div class="suite-kicker" data-label="weekend_program">Wedding Weekend</div>
            <div class="suite-names" style="font-size:25px" data-label="day_two">Day Two</div>
            <div class="suite-date" data-bind="dayTwoDate">14 June 2027</div><div class="suite-rule"></div>
            <div class="program-row"><span class="program-time" data-bind="dayTwoTime1">10:30 AM</span><span data-bind="dayTwoEvent1">Brunch</span></div>
            <div class="program-row"><span class="program-time" data-bind="dayTwoTime2">1:00 PM</span><span data-bind="dayTwoEvent2">Lake Activity</span></div>
            <div class="program-row"><span class="program-time" data-bind="dayTwoTime3">5:00 PM</span><span data-bind="dayTwoEvent3">Farewell Aperitivo</span></div>
            <div class="program-row"><span class="program-time" data-bind="dayTwoTime4">7:00 PM</span><span data-bind="dayTwoEvent4">Farewell</span></div>
          </article>
        </div>
      `);
    }

    const toolbar = root.querySelector('.suite-toolbar p');
    if (toolbar) toolbar.textContent = '8 core pieces + 7 optional matching pieces · one locked design system · fully editable text';

    const previewButton = document.getElementById('printSuite');
    if (previewButton) {
      previewButton.textContent = 'PRINT PREVIEW';
      previewButton.title = 'Preview only. Professional printer files are generated separately.';
    }
  };

  installWeekendPrograms();

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

  const syncOptionalPiece = (toggle) => {
    const piece = toggle.dataset.togglePiece;
    document.querySelectorAll(`[data-piece="${piece}"]`).forEach(el => {
      el.classList.toggle('is-disabled', !toggle.checked);
    });
  };

  const saveState = () => {
    const state = {};
    root.querySelectorAll('input[id], textarea[id], select[id]').forEach(field => {
      state[field.id] = field.type === 'checkbox' ? field.checked : field.value;
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
    Object.entries(preset).forEach(([key, value]) => setLabelText(key, value));
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
      if (field.type === 'checkbox') {
        field.checked = Boolean(value);
        syncOptionalPiece(field);
      } else {
        field.value = value;
        syncField(field);
      }
    });
    applyDirection(state.languagePreset || 'en');
    return true;
  };

  root.querySelectorAll('input[id]:not([type="checkbox"]), textarea[id]').forEach(field => {
    field.addEventListener('input', () => {
      syncField(field);
      saveState();
    });
  });

  root.querySelectorAll('[data-toggle-piece]').forEach(toggle => {
    syncOptionalPiece(toggle);
    toggle.addEventListener('change', () => {
      syncOptionalPiece(toggle);
      saveState();
    });
  });

  if (languageSelect) {
    languageSelect.addEventListener('change', () => applyLanguage(languageSelect.value));
  }

  document.getElementById('resetSuite')?.addEventListener('click', () => {
    localStorage.removeItem(storageKey);
    root.querySelectorAll('[data-default]').forEach(field => {
      if (field.type === 'checkbox') {
        field.checked = field.dataset.default === 'true';
        syncOptionalPiece(field);
      } else {
        field.value = defaultValue(field);
        syncField(field);
      }
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
      if (field.type === 'checkbox') {
        field.checked = field.dataset.default === 'true';
        syncOptionalPiece(field);
      } else if (!field.value) {
        field.value = defaultValue(field);
        syncField(field);
      }
    });
    applyLanguage(languageSelect?.value || 'en', false);
  } else {
    applyLanguage(languageSelect?.value || 'en', false);
  }
})();
