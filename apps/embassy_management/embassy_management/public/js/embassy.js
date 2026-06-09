(function (root) {
  root.embassy_management = root.embassy_management || {};

  const getFrappe = () => root.frappe || {};
  const escapeHtml = (value) => {
    const frappeObj = getFrappe();
    if (frappeObj.utils && frappeObj.utils.escape_html) {
      return frappeObj.utils.escape_html(value == null ? '' : String(value));
    }
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  };

  root.embassy_management.ui = {
  appIcon: '/assets/embassy_management/img/app_icon.png',

  escape(value) {
    return escapeHtml(value);
  },

  icon(name, size = 'md') {
    const frappeObj = getFrappe();
    if (frappeObj.utils && frappeObj.utils.icon) {
      try {
        return frappeObj.utils.icon(name, size);
      } catch (error) {
        return '';
      }
    }
    return '';
  },

  statusClass(value) {
    return String(value || 'open')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');
  },

  injectDeskStyles() {
    if (document.getElementById('ems-desk-runtime-styles')) {
      return;
    }

    const style = document.createElement('style');
    style.id = 'ems-desk-runtime-styles';
    style.textContent = `
      .layout-main-section .ems-desk, .page-content .ems-desk {
        color: #162235;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        padding: 20px 6px 36px;
      }

      .ems-command-shell {
        display: grid;
        gap: 18px;
      }

      .ems-command-header {
        align-items: stretch;
        background: #f7f9fc;
        border: 1px solid #d8e0ea;
        border-radius: 8px;
        display: grid;
        gap: 20px;
        grid-template-columns: minmax(0, 1fr) minmax(260px, 340px);
        overflow: hidden;
        padding: 22px;
      }

      .ems-command-title {
        align-items: flex-start;
        display: flex;
        gap: 16px;
        min-width: 0;
      }

      .ems-brand-mark {
        align-items: center;
        background: #ffffff;
        border: 1px solid #d8e0ea;
        border-radius: 8px;
        box-shadow: 0 10px 28px rgba(22, 34, 53, .08);
        display: grid;
        flex: 0 0 76px;
        height: 76px;
        justify-items: center;
        overflow: hidden;
        width: 76px;
      }

      .ems-brand-mark img {
        display: block;
        height: 64px;
        object-fit: contain;
        width: 64px;
      }

      .ems-brand-mark--fallback::before {
        color: #123c5f;
        content: "EMS";
        font-weight: 800;
      }

      .ems-kicker {
        color: #8a6412;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 0;
        margin-bottom: 7px;
        text-transform: uppercase;
      }

      .ems-command-title h2 {
        color: #0f172a;
        font-size: clamp(24px, 3vw, 34px);
        letter-spacing: 0;
        line-height: 1.12;
        margin: 0 0 10px;
      }

      .ems-command-title p {
        color: #526176;
        font-size: 14px;
        line-height: 1.55;
        margin: 0;
        max-width: 820px;
      }

      .ems-command-actions {
        align-content: space-between;
        display: grid;
        gap: 10px;
      }

      .ems-toolbar, .ems-filter-bar {
        align-items: center;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }

      .ems-filter-bar .form-control {
        min-width: 180px;
        width: auto;
      }

      .ems-toolbar .btn, .ems-filter-bar .btn {
        align-items: center;
        display: inline-flex;
        gap: 7px;
      }

      .ems-pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }

      .ems-pill {
        align-items: center;
        background: #eef6f5;
        border: 1px solid #cde3df;
        border-radius: 999px;
        color: #15534d;
        display: inline-flex;
        font-size: 12px;
        font-weight: 700;
        gap: 6px;
        line-height: 1;
        padding: 8px 10px;
      }

      .ems-action-grid, .ems-metric-grid, .ems-task-strip {
        display: grid;
        gap: 12px;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      }

      .ems-task-strip {
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      }

      .ems-action-card, .ems-metric-card, .ems-panel {
        background: #ffffff;
        border: 1px solid #d8e0ea;
        border-radius: 8px;
        box-shadow: 0 10px 28px rgba(22, 34, 53, .06);
      }

      .ems-action-card {
        color: inherit;
        cursor: pointer;
        display: grid;
        gap: 13px;
        min-height: 148px;
        padding: 17px;
        text-align: left;
        transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease;
        width: 100%;
      }

      .ems-task-button {
        align-items: center;
        background: #fbfcfe;
        border: 1px solid #e5ebf2;
        border-radius: 8px;
        color: inherit;
        display: grid;
        gap: 10px;
        grid-template-columns: auto auto minmax(0, 1fr);
        min-height: 76px;
        padding: 12px;
        text-align: left;
      }

      .ems-task-button:hover, .ems-task-button:focus {
        background: #f6faf9;
        border-color: #cde3df;
        outline: none;
      }

      .ems-task-number {
        align-items: center;
        background: #123c5f;
        border-radius: 999px;
        color: #ffffff;
        display: inline-flex;
        font-size: 12px;
        font-weight: 800;
        height: 28px;
        justify-content: center;
        width: 28px;
      }

      .ems-task-button strong, .ems-task-button small {
        display: block;
      }

      .ems-task-button small {
        color: #5a687a;
        font-size: 12px;
        line-height: 1.35;
        margin-top: 2px;
      }

      .ems-action-card:hover, .ems-action-card:focus {
        border-color: #1f6f78;
        box-shadow: 0 18px 36px rgba(22, 34, 53, .12);
        outline: none;
        transform: translateY(-1px);
      }

      .ems-card-head {
        align-items: center;
        display: flex;
        gap: 11px;
      }

      .ems-card-icon {
        align-items: center;
        background: #eef6f5;
        border: 1px solid #cde3df;
        border-radius: 8px;
        color: #15534d;
        display: inline-flex;
        height: 40px;
        justify-content: center;
        width: 40px;
      }

      .ems-card-icon svg {
        height: 20px;
        width: 20px;
      }

      .ems-card-head strong, .ems-panel-title h3 {
        color: #152238;
        font-size: 15px;
        letter-spacing: 0;
        line-height: 1.25;
        margin: 0;
      }

      .ems-card-copy, .ems-panel-copy {
        color: #5a687a;
        font-size: 13px;
        line-height: 1.45;
        margin: 0;
      }

      .ems-card-meta {
        align-items: center;
        color: #8a6412;
        display: flex;
        font-size: 12px;
        font-weight: 800;
        gap: 7px;
        margin-top: auto;
      }

      .ems-metric-card {
        display: grid;
        gap: 6px;
        min-height: 112px;
        padding: 16px;
      }

      .ems-metric-value {
        color: #123c5f;
        font-size: 30px;
        font-weight: 800;
        letter-spacing: 0;
        line-height: 1;
      }

      .ems-metric-label {
        color: #526176;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0;
        text-transform: uppercase;
      }

      .ems-panel {
        display: grid;
        gap: 12px;
        padding: 16px;
      }

      .ems-panel-title {
        align-items: flex-start;
        display: flex;
        justify-content: space-between;
        gap: 12px;
      }

      .ems-list {
        display: grid;
        gap: 10px;
      }

      .ems-list-row {
        align-items: center;
        background: #fbfcfe;
        border: 1px solid #e5ebf2;
        border-radius: 8px;
        color: inherit;
        display: grid;
        gap: 8px;
        grid-template-columns: minmax(0, 1fr) auto;
        padding: 13px;
      }

      .ems-list-row:hover {
        background: #f6faf9;
        border-color: #cde3df;
        text-decoration: none;
      }

      .ems-list-title {
        color: #152238;
        font-weight: 800;
      }

      .ems-list-subtitle {
        color: #5a687a;
        font-size: 12px;
        margin-top: 3px;
      }

      .ems-badge {
        align-items: center;
        background: #eef2f7;
        border-radius: 999px;
        color: #42526a;
        display: inline-flex;
        font-size: 12px;
        font-weight: 800;
        line-height: 1;
        padding: 8px 10px;
        white-space: nowrap;
      }

      .ems-badge--urgent, .ems-badge--emergency, .ems-badge--pending {
        background: #fff5d6;
        color: #8a6412;
      }

      .ems-badge--approved, .ems-badge--confirmed, .ems-badge--completed {
        background: #e7f6ed;
        color: #17633a;
      }

      .ems-badge--rejected, .ems-badge--cancelled {
        background: #fdecec;
        color: #9f2d2d;
      }

      .ems-empty-state {
        align-items: center;
        background: #fbfcfe;
        border: 1px dashed #c7d2df;
        border-radius: 8px;
        color: #5a687a;
        display: grid;
        min-height: 128px;
        padding: 20px;
        text-align: center;
      }

      .ems-empty-state strong {
        color: #152238;
        display: block;
        font-size: 15px;
        margin-bottom: 5px;
      }

      .ems-empty-state p {
        margin: 0 0 12px;
      }

      .ems-empty-actions {
        align-items: center;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
      }

      .ems-table-wrap {
        border: 1px solid #d8e0ea;
        border-radius: 8px;
        overflow: hidden;
      }

      .ems-table {
        margin: 0;
      }

      .ems-table thead th {
        background: #f7f9fc;
        border-bottom: 1px solid #d8e0ea;
        color: #526176;
        font-size: 12px;
        letter-spacing: 0;
        text-transform: uppercase;
      }

      @media (max-width: 900px) {
        .ems-command-header {
          grid-template-columns: 1fr;
        }

        .ems-command-title {
          flex-direction: column;
        }
      }

      @media (max-width: 640px) {
        .layout-main-section .ems-desk, .page-content .ems-desk {
          padding: 14px 0 28px;
        }

        .ems-command-header {
          padding: 16px;
        }

        .ems-list-row {
          grid-template-columns: 1fr;
        }

        .ems-filter-bar .form-control {
          width: 100%;
        }

        .ems-task-button {
          grid-template-columns: auto minmax(0, 1fr);
        }

        .ems-task-button .ems-card-icon {
          display: none;
        }
      }
    `;
    document.head.appendChild(style);
  }
  };
})(window);
