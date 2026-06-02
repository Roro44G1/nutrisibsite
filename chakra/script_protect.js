// script_protect.js – Blocare copiere, view source, developer tools
// Versiune unificată pentru toate paginile site-ului

(function() {
    // Blochează meniul contextual (click dreapta)
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        return false;
    });

    // Blochează selecția textului
    document.addEventListener('selectstart', function(e) {
        e.preventDefault();
        return false;
    });

    // Blochează combinări de taste periculoase
    document.addEventListener('keydown', function(e) {
        // F12
        if (e.key === 'F12') {
            e.preventDefault();
            return false;
        }
        // Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+Shift+C (DevTools)
        if (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J' || e.key === 'C')) {
            e.preventDefault();
            return false;
        }
        // Ctrl+U (View Source)
        if (e.ctrlKey && (e.key === 'u' || e.key === 'U')) {
            e.preventDefault();
            return false;
        }
        // Ctrl+S (Save)
        if (e.ctrlKey && (e.key === 's' || e.key === 'S')) {
            e.preventDefault();
            return false;
        }
        // Ctrl+C (Copy)
        if (e.ctrlKey && (e.key === 'c' || e.key === 'C')) {
            e.preventDefault();
            return false;
        }
        // Ctrl+V (Paste) – opțional, poate fi util să permiți, dar îl blochez complet
        if (e.ctrlKey && (e.key === 'v' || e.key === 'V')) {
            e.preventDefault();
            return false;
        }
        // Ctrl+X (Cut)
        if (e.ctrlKey && (e.key === 'x' || e.key === 'X')) {
            e.preventDefault();
            return false;
        }
    });

    // Previne deschiderea ferestrei de debug prin combinații de mouse/tastatură (console.log)
    console.log("%c⚠️ Developer tools sunt restricționate pe acest site.", "color: red; font-size: 14px;");
})();