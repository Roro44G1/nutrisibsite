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
        calculateNutrition();
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

function toggleField(id, show) {
    const el = document.getElementById(id);
    if(show) el.style.display = 'block';
    else el.style.display = 'none';
}

// --- 2. LOGICA DE CALCUL (Din wellness.js original) ---
function calculateNutrition() {
    const sex = document.getElementById('sex')?.value;
    const varsta = Number(document.getElementById('varsta')?.value || 0);
    const inaltimeCm = Number(document.getElementById('inaltime')?.value || 0);
    const greutate = Number(document.getElementById('greutate')?.value || 0);
    const activitate = Number(document.getElementById('activitate')?.value || 0);

    if (!sex || !varsta || !inaltimeCm || !greutate) return;

    const inaltimeM = inaltimeCm / 100;

    // IMC
    const imc = greutate / (inaltimeM * inaltimeM);
    let imcCategory = '';
    if (imc < 18.5) imcCategory = 'Subponderal';
    else if (imc < 25) imcCategory = 'Normoponderal';
    else if (imc < 30) imcCategory = 'Supraponderal';
    else if (imc < 35) imcCategory = 'Obezitate grad I';
    else if (imc < 40) imcCategory = 'Obezitate grad II';
    else imcCategory = 'Obezitate grad III';

    // RMB (Harris-Benedict revizuit)
    let rmb = 0;
    if (sex === 'Masculin') {
        rmb = 88.362 + (13.397 * greutate) + (4.799 * inaltimeCm) - (5.677 * varsta);
    } else {
        rmb = 447.593 + (9.247 * greutate) + (3.098 * inaltimeCm) - (4.330 * varsta);
    }

    const rma = rmb * activitate;
    
    // PGC Estimativ
    const sexFactor = (sex === 'Masculin') ? 1 : 0;
    const pgc = (1.20 * imc) + (0.23 * varsta) - (10.8 * sexFactor) - 5.4;

    // Update Input-uri Ascunse
    document.getElementById('imc').value = imc.toFixed(2);
    document.getElementById('imc_category').value = imcCategory;
    document.getElementById('rmb').value = rmb.toFixed(0);
    document.getElementById('rma').value = rma.toFixed(0);
    document.getElementById('pgc').value = pgc.toFixed(1);
}

// Listeners pentru calcule live
['sex', 'varsta', 'inaltime', 'greutate', 'activitate'].forEach(id => {
    const el = document.getElementById(id);
    if(el) el.addEventListener('change', calculateNutrition);
});

// Slider display
const slider = document.getElementById('motivatie_range');
if(slider) {
    slider.addEventListener('input', function() {
        document.getElementById('motivatie_val').textContent = this.value;
    });
}

// --- 3. INJECTARE FOOTER (Ca în model) ---
fetch('https://nutrisib.club/footer.html')
.then(response => response.text())
.then(data => {
    document.getElementById('footer-placeholder').innerHTML = data;
})
.catch(err => console.log('Footer load error:', err));

// --- 4. PDF GENERATION (La Submit) ---
function handleFormSubmit(e) {
    calculateNutrition();
    
    // Populare PDF
    document.getElementById('pdf_nume').textContent = document.getElementById('nume').value + ' ' + document.getElementById('prenume').value;
    document.getElementById('pdf_imc').textContent = document.getElementById('imc').value;
    document.getElementById('pdf_rmb').textContent = document.getElementById('rmb').value;

    const element = document.getElementById('pdf-report');
    element.style.display = 'block';
    
    const opt = {
        margin: 10,
        filename: 'Raport_Nutrisib.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    html2pdf().set(opt).from(element).save();
    // Formularul va continua submit-ul către Netlify (action="success.html")
}