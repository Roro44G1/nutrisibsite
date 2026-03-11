// ============================================================
//  SWITCH PROTECȚIE — schimbă în FALSE pentru a dezactiva
// ============================================================
const PROTECTION_ENABLED = true;
// ============================================================

(function () {
    if (!PROTECTION_ENABLED) return; // Dacă switch-ul e false, iese imediat

    // Blochează click dreapta
    document.addEventListener('contextmenu', function (e) {
        e.preventDefault();
    });

    // Blochează copierea textului selectat (evenimentul 'copy')
    document.addEventListener('copy', function (e) {
        e.preventDefault();
        e.clipboardData && e.clipboardData.clearData();
    });

    // Blochează selecția textului cu mouse-ul / tastatura
    document.addEventListener('selectstart', function (e) {
        e.preventDefault();
    });

    // Blochează scurtăturile de tastatură
    document.addEventListener('keydown', function (e) {
        if (e.key === 'F12') { e.preventDefault(); }                           // Disable F12          (Windows)
        if (e.ctrlKey  && e.key === 'U') { e.preventDefault(); }               // Disable Ctrl+U       (Windows/Linux)
        if (e.metaKey  && e.key === 'U') { e.preventDefault(); }               // Disable Cmd+U        (Mac)
        if (e.ctrlKey  && e.key === 'C') { e.preventDefault(); }               // Disable Ctrl+C       (Windows/Linux)
        if (e.metaKey  && e.key === 'C') { e.preventDefault(); }               // Disable Cmd+C        (Mac)
        if (e.ctrlKey  && e.key === 'A') { e.preventDefault(); }               // Disable Ctrl+A       (selectare totală)
        if (e.metaKey  && e.key === 'A') { e.preventDefault(); }               // Disable Cmd+A        (Mac)
        if (e.ctrlKey  && e.shiftKey && e.key === 'I') { e.preventDefault(); } // Disable Ctrl+Shift+I (Windows/Linux)
        if (e.metaKey  && e.altKey  && e.key === 'I') { e.preventDefault(); }  // Disable Cmd+Opt+I    (Mac)
        if (e.ctrlKey  && e.shiftKey && e.key === 'J') { e.preventDefault(); } // Disable Ctrl+Shift+J (Windows/Linux)
        if (e.metaKey  && e.altKey  && e.key === 'J') { e.preventDefault(); }  // Disable Cmd+Opt+J    (Mac)
        if (e.ctrlKey  && e.key === 'S') { e.preventDefault(); }               // Disable Ctrl+S       (salvare pagină)
        if (e.metaKey  && e.key === 'S') { e.preventDefault(); }               // Disable Cmd+S        (Mac)
        if (e.ctrlKey  && e.key === 'P') { e.preventDefault(); }               // Disable Ctrl+P       (printare)
        if (e.metaKey  && e.key === 'P') { e.preventDefault(); }               // Disable Cmd+P        (Mac)
    });

    // Blochează drag & drop al textului selectat
    document.addEventListener('dragstart', function (e) {
        e.preventDefault();
    });

    // CSS — dezactivează selecția vizuală a textului
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

<<<<<<< HEAD
})();
=======
})();
>>>>>>> 4581e47e49bb75233c7ed35d59fefbf2d642cc1d
