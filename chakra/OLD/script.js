 <script>
        // Funcția pentru deschiderea tab-urilor
        function openTab(evt, tabName) {
            var i, tabcontent, tabbuttons;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tabbuttons = document.getElementsByClassName("tab-button");
            for (i = 0; i < tabbuttons.length; i++) {
                tabbuttons[i].className = tabbuttons[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }

        // Script de securitate pentru a bloca copierea și uneltele de dezvoltator
        document.addEventListener('contextmenu', event => event.preventDefault()); // Blochează clicul dreapta

        document.addEventListener('keydown', function(e) {
            // Blochează Ctrl+C (Copiere)
            if (e.ctrlKey && e.key === 'c') {
                e.preventDefault();
            }
            // Blochează Ctrl+U (View Source)
            if (e.ctrlKey && e.key === 'u') {
                e.preventDefault();
            }
            // Blochează F12 (Developer Tools)
            if (e.key === 'F12') {
                e.preventDefault();
            }
            // Blochează Ctrl+Shift+I (Developer Tools)
            if (e.ctrlKey && e.shiftKey && e.key === 'I') {
                e.preventDefault();
            }
             // Blochează Ctrl+Shift+J (Developer Tools Console)
            if (e.ctrlKey && e.shiftKey && e.key === 'J') {
                e.preventDefault();
            }
        });

        // Activați primul tab la încărcarea paginii
        document.addEventListener("DOMContentLoaded", function() {
            document.querySelector('.tab-button').click();
        });
    </script>
