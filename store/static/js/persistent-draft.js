(() => {
  const root = document.querySelector('[data-suite-editor]');
  if (!root) return;

  const status = document.getElementById('editorSaveStatus');
  const actions = root.querySelector('.editor-actions');
  const introNote = root.querySelector('.editor-panel > .editor-note');
  const basePath = window.location.pathname.replace(/\/$/, '');
  const draftEndpoint = `${basePath}/draft`;
  const revisionsEndpoint = `${draftEndpoint}/revisions`;
  let hydrating = false;
  let saveTimer = null;
  let latestRevision = null;
  let conflicted = false;

  if (introNote) {
    introNote.textContent = 'Your purchased copy stays editable. Changes are saved to this order, so you can return later, verify the purchase email and continue editing. Recent versions can also be restored.';
  }

  const setStatus = (text) => {
    if (status) status.textContent = text;
  };

  const collectState = () => {
    const state = {};
    root.querySelectorAll('input[id], textarea[id], select[id]').forEach(field => {
      state[field.id] = field.type === 'checkbox' ? field.checked : field.value;
    });
    state.__draft_expected_revision = latestRevision ?? 0;
    return state;
  };

  const applyState = (state) => {
    if (!state || typeof state !== 'object') return;
    hydrating = true;
    try {
      Object.entries(state).forEach(([id, value]) => {
        const field = document.getElementById(id);
        if (!field) return;
        if (field.type === 'checkbox') {
          field.checked = Boolean(value);
          field.dispatchEvent(new Event('change', {bubbles: true}));
        } else {
          field.value = value ?? '';
          field.dispatchEvent(new Event(field.tagName === 'SELECT' ? 'change' : 'input', {bubbles: true}));
        }
      });
    } finally {
      hydrating = false;
    }
  };

  const reloadButton = document.createElement('button');
  reloadButton.type = 'button';
  reloadButton.className = 'btn btn-outline';
  reloadButton.textContent = 'LOAD LATEST SAVED VERSION';
  reloadButton.hidden = true;

  const loadRemote = async () => {
    setStatus('Loading your saved version…');
    try {
      const response = await fetch(draftEndpoint, {credentials: 'same-origin'});
      const result = await response.json().catch(() => ({}));
      if (!response.ok || !result.ok) throw new Error(result.error || 'Could not load saved changes.');
      if (result.draft?.state) {
        applyState(result.draft.state);
        latestRevision = result.draft.revision;
        setStatus(`Saved version ${result.draft.revision} restored`);
      } else {
        latestRevision = 0;
        setStatus('Ready to edit · changes will be saved automatically');
      }
      conflicted = false;
      reloadButton.hidden = true;
    } catch (error) {
      setStatus(error.message || 'Could not load saved changes.');
    }
  };

  const saveRemote = async () => {
    if (hydrating || conflicted) return;
    setStatus('Saving your editable copy…');
    try {
      const response = await fetch(draftEndpoint, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        credentials: 'same-origin',
        body: JSON.stringify({state: collectState()}),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok || !result.ok) throw new Error(result.error || 'Could not save changes.');
      latestRevision = result.revision;
      setStatus(`Saved to your order · version ${result.revision}`);
    } catch (error) {
      const message = error.message || 'Could not save changes.';
      if (message.includes('newer saved version')) {
        conflicted = true;
        reloadButton.hidden = false;
        setStatus('A newer version was saved on another device. Load it before continuing so nothing is overwritten.');
      } else {
        setStatus(message);
      }
    }
  };

  const scheduleSave = () => {
    if (hydrating || conflicted) return;
    clearTimeout(saveTimer);
    setStatus('Saving…');
    saveTimer = setTimeout(saveRemote, 900);
  };

  reloadButton.addEventListener('click', loadRemote);

  const createHistoryControls = () => {
    if (!actions || document.getElementById('draftHistoryButton')) return;

    const button = document.createElement('button');
    button.type = 'button';
    button.id = 'draftHistoryButton';
    button.className = 'btn btn-outline';
    button.textContent = 'VERSION HISTORY';

    const panel = document.createElement('div');
    panel.id = 'draftHistoryPanel';
    panel.hidden = true;
    panel.style.width = '100%';
    panel.style.marginTop = '10px';
    panel.innerHTML = `
      <select id="draftRevisionSelect" style="width:100%;padding:10px;margin-bottom:8px;"></select>
      <button type="button" id="restoreDraftRevision" class="btn btn-outline" style="width:100%;">RESTORE SELECTED VERSION</button>
    `;

    button.addEventListener('click', async () => {
      panel.hidden = !panel.hidden;
      if (panel.hidden) return;
      setStatus('Loading version history…');
      try {
        const response = await fetch(revisionsEndpoint, {credentials: 'same-origin'});
        const result = await response.json().catch(() => ({}));
        if (!response.ok || !result.ok) throw new Error(result.error || 'Could not load version history.');
        const select = panel.querySelector('#draftRevisionSelect');
        select.innerHTML = '';
        result.revisions.forEach(item => {
          const option = document.createElement('option');
          option.value = item.revision;
          const stamp = new Date(item.created_at).toLocaleString();
          option.textContent = `Version ${item.revision} · ${stamp}`;
          select.appendChild(option);
        });
        if (!result.revisions.length) {
          const option = document.createElement('option');
          option.textContent = 'No saved versions yet';
          option.disabled = true;
          select.appendChild(option);
        }
        setStatus(latestRevision ? `Current version ${latestRevision}` : 'No saved versions yet');
      } catch (error) {
        setStatus(error.message || 'Could not load version history.');
      }
    });

    panel.querySelector('#restoreDraftRevision').addEventListener('click', async () => {
      const revision = panel.querySelector('#draftRevisionSelect').value;
      if (!revision) return;
      setStatus(`Restoring version ${revision}…`);
      try {
        const response = await fetch(`${draftEndpoint}/restore/${encodeURIComponent(revision)}`, {
          method: 'POST',
          credentials: 'same-origin',
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok || !result.ok) throw new Error(result.error || 'Could not restore version.');
        applyState(result.state);
        latestRevision = result.revision;
        conflicted = false;
        reloadButton.hidden = true;
        setStatus(`Previous version restored and saved as version ${result.revision}`);
      } catch (error) {
        setStatus(error.message || 'Could not restore version.');
      }
    });

    actions.appendChild(button);
    actions.appendChild(reloadButton);
    actions.appendChild(panel);
  };

  root.addEventListener('input', scheduleSave);
  root.addEventListener('change', scheduleSave);
  document.getElementById('resetSuite')?.addEventListener('click', () => setTimeout(scheduleSave, 0));

  createHistoryControls();
  loadRemote();
})();
