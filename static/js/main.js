/* ========================================================================
   NEC Asset Management — Mobile-Aware Sidebar & UI Enhancements
   ======================================================================== */

(function () {
    'use strict';

    const wrapper = document.getElementById('wrapper');
    const toggleBtn = document.getElementById('menu-toggle');
    const overlay = document.getElementById('sidebar-overlay');
    const sidebarLinks = document.querySelectorAll('#sidebar-wrapper .list-group-item');

    // ---- Sidebar toggle -------------------------------------------------
    if (toggleBtn && wrapper) {
        toggleBtn.addEventListener('click', function (e) {
            e.preventDefault();
            wrapper.classList.toggle('toggled');

            // Update aria
            const isOpen = wrapper.classList.contains('toggled');
            toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });
    }

    // ---- Overlay click → close sidebar (mobile only) -------------------
    if (overlay) {
        overlay.addEventListener('click', function () {
            wrapper.classList.remove('toggled');
            if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
        });
    }

    // ---- Nav link click → close sidebar on mobile ----------------------
    sidebarLinks.forEach(function (link) {
        link.addEventListener('click', function () {
            // Only auto-close if we're on mobile (sidebar is off-canvas)
            if (window.innerWidth < 992) {
                wrapper.classList.remove('toggled');
                if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
            }
        });
    });

    // ---- Resize: reset sidebar state when crossing breakpoint ----------
    let lastWidth = window.innerWidth;
    let wasToggled = false;

    window.addEventListener('resize', function () {
        const currentWidth = window.innerWidth;

        // Crossing from mobile to desktop (992px breakpoint)
        if (lastWidth < 992 && currentWidth >= 992) {
            // On desktop, sidebar should be visible by default
            // Restore whatever state it was in
            if (wasToggled && wrapper) {
                wrapper.classList.add('toggled');
            }
        }

        // Crossing from desktop to mobile
        if (lastWidth >= 992 && currentWidth < 992) {
            // Remember current state
            wasToggled = wrapper ? wrapper.classList.contains('toggled') : false;
            // On mobile, sidebar hidden by default
            if (wrapper) wrapper.classList.remove('toggled');
        }

        lastWidth = currentWidth;
    });

    // ---- Swipe-to-close on mobile (touch devices) ---------------------
    let touchStartX = 0;
    let touchCurrentX = 0;

    document.addEventListener('touchstart', function (e) {
        touchStartX = e.touches[0].clientX;
    }, { passive: true });

    document.addEventListener('touchmove', function (e) {
        touchCurrentX = e.touches[0].clientX;
    }, { passive: true });

    document.addEventListener('touchend', function () {
        const swipeDistance = touchStartX - touchCurrentX;
        // Swipe left > 80px on the overlay or content → close sidebar
        if (swipeDistance > 80 && wrapper && wrapper.classList.contains('toggled')) {
            wrapper.classList.remove('toggled');
            if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
        }
    });

})();
