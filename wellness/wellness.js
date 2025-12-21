// --- 1. NAVIGARE TAB-URI ---
let currentTab = 0;
const tabs = document.querySelectorAll('.tab');
const progressBar = document.getElementById('progressBar');

function showTab(n) {
    tabs.forEach(t => t.classList.remove('active'));
    tabs[n].classList.add('active');
    
    // Update Progress
    const progress = ((n + 1) / tabs.length) * 100;
    if(progressBar) progressBar.style.width = `${progress}%`;
    
    // Scroll Top
    document.querySelector('.main-container').scrollIntoView({ behavior: 'smooth' });
}

function nextTab() {
    if (!validateForm(currentTab)) return;
    
    // Dacă plecăm de la date personale (Tab index 1 -> Step 2), calculăm
    if (currentTab === 1) {
        calculeazaNutritie();
    }

    if (currentTab < tabs.length - 1) {
        currentTab++;
        showTab(currentTab);
    }
}

function prevTab() {
    if (currentTab > 0) {
        currentTab--;
        showTab(currentTab);
    }
}

function validateForm(n) {
    const inputs = tabs[n].querySelectorAll('input[required], select[required]');
    let valid = true;
    inputs.forEach(input => {
        if (!input.checkValidity()) {
            input.reportValidity();
            valid = false;
        }
    });
    return valid;
}

// Toggle pentru detalii (câmpuri ascunse)
function toggleField(id, show) {
    const el = document.getElementById(id);
    if(show) {
        el.style.display = 'block';
        el.setAttribute('required', 'true');
    } else {
        el.style.display = 'none';
        el.removeAttribute('required');
        el.value = '';
    }
}

// --- 2. LOGICA DE CALCUL (Din wellness - Copie.js) ---
function calculeazaNutritie() {
    const sex = document.getElementById('sex')?.value;
    const varsta = Number(document.getElementById('varsta')?.value || 0);
    const inaltimeCm = Number(document.getElementById('inaltime')?.value || 0);
    const greutate = Number(document.getElementById('greutate')?.value || 0);
    const activitate = Number(document.getElementById('activitate')?.value || 0);

    if (!sex || !varsta || !inaltimeCm || !greutate) return;

    const inaltimeM = inaltimeCm / 100;

    // A. IMC (BMI)
    const imc = greutate / (inaltimeM * inaltimeM);
    let imcCategory = '';
    if (imc < 18.5) imcCategory = 'Subponderal';
    else if (imc < 25) imcCategory = 'Normoponderal';
    else if (imc < 30) imcCategory = 'Supraponderal';
    else if (imc < 35) imcCategory = 'Obezitate grad I';
    else if (imc < 40) imcCategory = 'Obezitate grad II';
    else imcCategory = 'Obezitate grad III';

    // B. RMB (Harris-Benedict - din wellness - Copie.js)
    let rmb = 0;
    if (sex === 'Masculin') {
        // RMB = 88.362 + (13.397 × kg) + (4.799 × cm) − (5.677 × ani)
        rmb = 88.362 + (13.397 * greutate) + (4.799 * inaltimeCm) - (5.677 * varsta);
    } else {
        // RMB = 447.593 + (9.247 × kg) + (3.098 × cm) − (4.330 × ani)
        rmb = 447.593 + (9.247 * greutate) + (3.098 * inaltimeCm) - (4.330 * varsta);
    }

    // C. RMA (Rata Metabolică Activă) & CMA
    const rma = rmb * activitate;
    const cma = rma; // Default

    // Populate Hidden Inputs
    document.getElementById('imc').value = imc.toFixed(2);
    document.getElementById('imc_category').value = imcCategory;
    document.getElementById('rmb').value = rmb.toFixed(0);
    document.getElementById('rma').value = rma.toFixed(0);
    document.getElementById('cma').value = cma.toFixed(0);
}

// Event Listeners pentru calcule live
['sex', 'varsta', 'inaltime', 'greutate', 'activitate'].forEach(id => {
    const el = document.getElementById(id);
    if(el) {
        el.addEventListener('change', calculeazaNutritie);
        el.addEventListener('input', calculeazaNutritie);
    }
});

// Slider Value Update
const slider = document.getElementById('motivatie_range');
if(slider) {
    slider.addEventListener('input', function() {
        document.getElementById('motivatie_val').textContent = this.value;
        document.getElementById('motivatie_input').value = this.value;
    });
}

// --- 3. INJECTARE FOOTER (Fetch) ---
fetch('https://nutrisib.club/footer.html')
.then(response => response.text())
.then(data => {
    document.getElementById('footer-placeholder').innerHTML = data;
})
.catch(err => console.log('Eroare încărcare footer:', err));

// --- 4. GENERARE PDF & SUBMIT ---
const form = document.getElementById('wellnessForm');
if(form) {
    form.addEventListener('submit', function(e) {
        // Nu prevenim default complet pentru a lăsa Netlify să facă POST
        // Dar generăm PDF-ul înainte
        calculeazaNutritie();
        
        // Populăm template-ul PDF ascuns
        document.getElementById('pdf_nume').textContent = document.getElementById('nume').value + ' ' + document.getElementById('prenume').value;
        document.getElementById('pdf_imc').textContent = document.getElementById('imc').value;
        document.getElementById('pdf_imc_cat').textContent = document.getElementById('imc_category').value;
        document.getElementById('pdf_rmb').textContent = document.getElementById('rmb').value;
        document.getElementById('pdf_rma').textContent = document.getElementById('rma').value;

        // Generare
        const element = document.getElementById('pdf-report');
        element.style.display = 'block';
        
        const opt = {
            margin: 10,
            filename: 'Raport_Nutrisib.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        html2pdf().set(opt).from(element).save().then(() => {
            element.style.display = 'none';
        });
        
        // Lasăm formularul să continue către action="success.html"
    });
}