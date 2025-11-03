        //Disable right-click and common dev tools shortcuts
        document.addEventListener('contextmenu', function(e) {e.preventDefault()});
        document.addEventListener('keydown', function(e) {
            if (e.key === 'F12') {e.preventDefault();}  Disable F12
            if (e.ctrlKey && e.shiftKey && e.key === 'I') {e.preventDefault()}   Disable Ctrl+Shift+I (WindowsLinux)
            if (e.metaKey && e.altKey && e.key === 'I') {e.preventDefault()}     Disable Cmd+Opt+I (Mac)
            if (e.ctrlKey && e.shiftKey && e.key === 'J') {e.preventDefault()}   Disable Ctrl+Shift+J (WindowsLinux)
            if (e.metaKey && e.altKey && e.key === 'J') {e.preventDefault()}     Disable Cmd+Opt+J (Mac)
            if (e.ctrlKey && e.key === 'U') {e.preventDefault()}                 Disable Ctrl+U (WindowsLinux)
            if (e.metaKey && e.key === 'U') {e.preventDefault()}                 Disable Cmd+U (Mac)
        });