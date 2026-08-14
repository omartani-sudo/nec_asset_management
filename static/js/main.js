/* ========================================================================
   NEC Asset Management — App shell behaviour
   Sidebar (off-canvas on mobile), dark mode, bulk selection, toasts.
   ======================================================================== */

(function () {
    'use strict';

    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('menu-toggle');
    const overlay = document.getElementById('sidebar-back');

    // ---- Theme toggle ---------------------------------------------------
    const themeBtn = document.getElementById('theme-toggle');
    const root = document.documentElement;
    const savedTheme = localStorage.getItem('nec-theme');
    if (savedTheme) root.setAttribute('data-theme', savedTheme);
    if (themeBtn) {
        function syncThemeIcon() {
            const dark = root.getAttribute('data-theme') === 'dark';
            themeBtn.innerHTML = dark ? '<span class="material-symbols-outlined" aria-hidden="true">light_mode</span>' : '<span class="material-symbols-outlined" aria-hidden="true">dark_mode</span>';
            themeBtn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
        }
        themeBtn.addEventListener('click', function () {
            const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            root.setAttribute('data-theme', next);
            localStorage.setItem('nec-theme', next);
            syncThemeIcon();
        });
        syncThemeIcon();
    }

    // ---- Sidebar (off-canvas < 768px) ----------------------------------
    function isMobile() { return window.innerWidth < 768; }
    let lastFocused = null;

    function openSidebar() {
        sidebar.classList.add('open');
        if (overlay) overlay.classList.add('show');
        toggleBtn.setAttribute('aria-expanded', 'true');
        const firstLink = sidebar.querySelector('.nav-item');
        if (firstLink) firstLink.focus();
    }

    function closeSidebar() {
        sidebar.classList.remove('open');
        if (overlay) overlay.classList.remove('show');
        toggleBtn.setAttribute('aria-expanded', 'false');
        if (lastFocused) { lastFocused.focus(); lastFocused = null; }
    }

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function (e) {
            e.preventDefault();
            if (sidebar.classList.contains('open')) {
                closeSidebar();
            } else {
                lastFocused = toggleBtn;
                openSidebar();
            }
        });
        if (overlay) {
            overlay.addEventListener('click', closeSidebar);
        }
        // Escape closes the off-canvas sidebar and restores focus
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && isMobile() && sidebar.classList.contains('open')) {
                closeSidebar();
            }
        });
        // Auto-close after navigating (link clicks)
        sidebar.addEventListener('click', function (e) {
            if (isMobile() && e.target.closest('.nav-item')) closeSidebar();
        });
        window.addEventListener('resize', function () {
            if (!isMobile()) closeSidebar();
        });
    }

    // ---- Bulk selection (delete / edit / print QR) ---------------------
    const selectAll = document.getElementById('select-all');
    const assetChecks = document.querySelectorAll('.asset-check');
    const bulkActionBtns = document.querySelectorAll(
        '#bulk-delete-btn, #bulk-edit-btn, #print-qr-btn'
    );

    if (selectAll && assetChecks.length) {
        const countEl = document.getElementById('selection-count');
        function updateBulkState() {
            const checked = Array.prototype.filter.call(assetChecks, function (c) { return c.checked; });
            const anyChecked = checked.length > 0;
            bulkActionBtns.forEach(function (btn) { btn.disabled = !anyChecked; });
            selectAll.checked = anyChecked && checked.length === assetChecks.length;
            selectAll.indeterminate = anyChecked && checked.length < assetChecks.length;
            if (countEl) countEl.textContent = checked.length + ' selected';
        }
        selectAll.addEventListener('change', function () {
            assetChecks.forEach(function (c) { c.checked = selectAll.checked; });
            updateBulkState();
        });
        assetChecks.forEach(function (c) {
            c.addEventListener('change', updateBulkState);
        });
        updateBulkState();
    }

    // ---- Toast auto-dismiss --------------------------------------------
    document.querySelectorAll('.alert.alert-dismissible').forEach(function (el) {
        setTimeout(function () {
            if (window.bootstrap && bootstrap.Alert) {
                bootstrap.Alert.getOrCreateInstance(el).close();
            } else {
                el.remove();
            }
        }, 6000);
    });
})();
