// ============================================================
//  SWITCH PROTECȚIE — schimbă în FALSE pentru a dezactiva
// ============================================================
const PROTECTION_ENABLED = true;
// ============================================================
(function () {
    if (!PROTECTION_ENABLED) return;

    document.addEventListener('contextmenu', function (e) {
        e.preventDefault();
    });

    document.addEventListener('copy', function (e) {
        e.preventDefault();
        e.clipboardData && e.clipboardData.clearData();
    });

    document.addEventListener('selectstart', function (e) {
        e.preventDefault();
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'F12') { e.preventDefault(); }
        if (e.ctrlKey  && e.key === 'U') { e.preventDefault(); }
        if (e.metaKey  && e.key === 'U') { e.preventDefault(); }
        if (e.ctrlKey  && e.key === 'C') { e.preventDefault(); }
        if (e.metaKey  && e.key === 'C') { e.preventDefault(); }
        if (e.ctrlKey  && e.key === 'A') { e.preventDefault(); }
        if (e.metaKey  && e.key === 'A') { e.preventDefault(); }
        if (e.ctrlKey  && e.shiftKey && e.key === 'I') { e.preventDefault(); }
        if (e.metaKey  && e.altKey  && e.key === 'I') { e.preventDefault(); }
        if (e.ctrlKey  && e.shiftKey && e.key === 'J') { e.preventDefault(); }
        if (e.metaKey  && e.altKey  && e.key === 'J') { e.preventDefault(); }
        if (e.ctrlKey  && e.key === 'S') { e.preventDefault(); }
        if (e.metaKey  && e.key === 'S') { e.preventDefault(); }
        if (e.ctrlKey  && e.key === 'P') { e.preventDefault(); }
        if (e.metaKey  && e.key === 'P') { e.preventDefault(); }
    });

    document.addEventListener('dragstart', function (e) {
        e.preventDefault();
    });

    const style = document.createElement('style');
    style.innerHTML = `
        * {
            -webkit-user-select: none !important;
            -moz-user-select: none !important;
            -ms-user-select: none !important;
            user-select: none !important;
        }
        input, textarea {
            -webkit-user-select: text !important;
            -moz-user-select: text !important;
            -ms-user-select: text !important;
            user-select: text !important;
        }
    `;
    document.head.appendChild(style);
})();
