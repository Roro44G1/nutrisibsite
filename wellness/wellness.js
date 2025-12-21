// --- 1. Tab Navigation Logic ---
let currentTab = 0; // Index starts at 0 (Tab 1)
const tabs = document.querySelectorAll('.tab');
const progressBar = document.getElementById('progressBar');

function showTab(n) {
    // Hide all tabs
    tabs.forEach(tab => tab.classList.remove('active'));
    // Show current tab
    tabs[n].classList.add('active');
    
    // Update Progress Bar
    const progress = ((n + 1) / tabs.length) * 100;
    progressBar.style.width = `${progress}%`;
    
    // Scroll to top of form
    document.querySelector('.main-container').scrollIntoView({ behavior: 'smooth' });
}

function nextTab() {
    if (!validateForm(currentTab)) return false;
    
    // Calculate before moving from Bio tab (Tab index 1 -> Step 2)
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
    // Validare simplă HTML5 pe câmpurile din tab-ul curent
    const currentTabInputs = tabs[n].querySelectorAll('input[required], select[required], textarea[required]');
    let valid = true;
    
    currentTabInputs.forEach(input => {
        if (!input.checkValidity()) {
            input.reportValidity();
            valid = false;
        }
    });
    return valid;
}

// --- 2. Dynamic Field Toggle ---
function toggleField(fieldId, show) {
    const field = document.getElementById(fieldId);
    if (show) {
        field.style.display = 'block';
        field.setAttribute('required', 'true');
    } else {
        field.style.display = 'none';
        field.removeAttribute('required');
        field.value = ''; // Reset value
    }
}

function updateRangeValue(val) {
    document.getElementById('range_val').textContent = val;
}

// --- 3. Calculation Logic (Adapted from wellness.js) ---
function calculateNutrition() {
    const sex = document.getElementById('sex')?.value;
    const varsta = Number(document.getElementById('varsta')?.value || 0);
    const inaltimeCm = Number(document.getElementById('inaltime')?.value || 0);
    const greutate = Number(document.getElementById('greutate')?.value || 0);
    const activitate = Number(document.getElementById('activitate')?.value || 0);

    if (!sex || !varsta || !inaltimeCm || !greutate || !activitate) return;

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

    // B. RMB (Harris-Benedict - as in source wellness.js)
    let rmb = 0;
    if (sex === 'Masculin') {
        // RMB = 88.362 + (13.397 × greutate kg) + (4.799 × înălțime cm) − (5.677 × vârsta ani)
        rmb = 88.362 + (13.397 * greutate) + (4.799 * inaltimeCm) - (5.677 * varsta);
    } else {
        // RMB = 447.593 + (9.247 × greutate kg) + (3.098 × înălțime cm) − (4.330 × vârsta ani)
        rmb = 447.593 + (9.247 * greutate) + (3.098 * inaltimeCm) - (4.330 * varsta);
    }

    // C. RMA (Rata Metabolica Activa)
    const rma = rmb * activitate;
    const cma = rma; // Default starting point

    // D. PGC (Procent Grăsime Corporală - Estimare Deurenberg)
    // Formula: (1.20 x IMC) + (0.23 x Vârsta) - (10.8 x Sex) - 5.4
    // Sex: 1 pt bărbați, 0 pt femei
    const sexFactor = (sex === 'Masculin') ? 1 : 0;
    const pgc = (1.20 * imc) + (0.23 * varsta) - (10.8 * sexFactor) - 5.4;

    // Write to hidden inputs
    document.getElementById('imc').value = imc.toFixed(2);
    document.getElementById('imc_category').value = imcCategory;
    document.getElementById('rmb').value = rmb.toFixed(0);
    document.getElementById('rma').value = rma.toFixed(0);
    document.getElementById('cma').value = cma.toFixed(0);
    document.getElementById('pgc').value = pgc.toFixed(1);
}

// Event Listeners for Real-time Calc
['sex', 'varsta', 'inaltime', 'greutate', 'activitate'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener('change', calculateNutrition);
        el.addEventListener('input', calculateNutrition);
    }
});

// Initial logic for ranges (if any visible)
document.querySelectorAll('input[type="range"]').forEach(range => {
    range.addEventListener('input', (e) => updateRangeValue(e.target.value));
});