(() => {
  const root = document.querySelector('[data-suite-editor]');
  if (!root) return;

  const actions = root.querySelector('.editor-actions');
  const status = document.getElementById('editorSaveStatus');
  if (!actions) return;

  const toggleToPrintPiece = {
    accommodation: 'accommodation',
    coordinator: 'coordinator',
    dress: 'dress_code',
    envelope: 'envelope',
    liner: 'envelope_liner',
    'day-one': 'program_day_1',
    'day-two': 'program_day_2',
  };

  const collectPrintJob = () => {
    const fields = {};
    const labels = {};
    const enabledOptional = [];

    root.querySelectorAll('[data-bind-key]').forEach(field => {
      if (!field.dataset.bindKey) return;
      fields[field.dataset.bindKey] = field.value ?? '';
    });

    root.querySelectorAll('[data-label-key]').forEach(field => {
      if (!field.dataset.labelKey) return;
      labels[field.dataset.labelKey] = field.value ?? '';
    });

    root.querySelectorAll('[data-toggle-piece]').forEach(toggle => {
      if (!toggle.checked) return;
      const canonical = toggleToPrintPiece[toggle.dataset.togglePiece];
      if (canonical) enabledOptional.push(canonical);
    });

    return {
      language: document.getElementById('languagePreset')?.value || 'en',
      enabled_optional: enabledOptional,
      fields,
      labels,
    };
  };

  const validatePrintJob = async () => {
    const button = document.getElementById('validatePrintJob');
    if (button) button.disabled = true;
    if (status) status.textContent = 'Checking professional print data…';

    try {
      const endpoint = window.location.pathname.replace(/\/$/, '') + '/print-job/validate';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'same-origin',
        body: JSON.stringify(collectPrintJob()),
      });
      const result = await response.json().catch(() => ({}));

      if (!response.ok || !result.ok) {
        throw new Error(result.error || 'Print data validation failed.');
      }

      if (status) {
        const readiness = result.professional_print_package_ready
          ? 'Professional production package is enabled.'
          : 'Professional export remains locked until prepress QA is complete.';
        status.textContent = `${result.printable_pieces} print pieces · ${result.professional_pdf_files} professional PDF files. ${readiness}`;
      }
      return result;
    } catch (error) {
      if (status) status.textContent = error.message || 'Print data validation failed.';
      return null;
    } finally {
      if (button) button.disabled = false;
    }
  };

  const button = document.createElement('button');
  button.id = 'validatePrintJob';
  button.type = 'button';
  button.className = 'btn btn-outline';
  button.textContent = 'CHECK PRINT DATA';
  button.title = 'Validate personalization data and calculate the professional print package. This does not generate a press PDF yet.';
  button.addEventListener('click', validatePrintJob);
  actions.insertBefore(button, document.getElementById('resetSuite'));

  window.LoveForLovePrintJob = {
    collect: collectPrintJob,
    validate: validatePrintJob,
  };
})();
