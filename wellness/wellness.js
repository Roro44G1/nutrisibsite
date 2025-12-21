let currentTab = 0;
const tabs = document.querySelectorAll('.tab');
const progressBar = document.getElementById('progressBar');

// Inițializare
document.addEventListener("DOMContentLoaded", () => {
    showTab(currentTab);
    
    // Listeners pentru calcul automat la modificarea datelor biometrice
    ['sex', 'varsta', 'inaltime', 'greutate', 'activitate'].forEach(id => {
        const el = document.getElementById(id);
        if(el) { el.addEventListener('input', calculeazaNutritie); }
    });

    // Listeners pentru recalculare la modificarea obiectivelor sau ritmului
    const ritmEl = document.getElementById('ritm_slabire');
    if(ritmEl) { ritmEl.addEventListener('change', calculeazaNutritie); }
    
    const obiectiveInputs = document.querySelectorAll('input[name="obiective[]"]');
    obiectiveInputs.forEach(input => input.addEventListener('change', calculeazaNutritie));

    // Slider listener pentru motivație
    const slider = document.getElementById('motivatie_range');
    if(slider) {
        slider.addEventListener('input', function() {
            document.getElementById('motivatie_val').textContent = this.value;
        });
    }

    // Toggle pentru Modelare Corporală (Ritm slăbire/îngrășare)
    const obiectiveChecks = document.querySelectorAll('input[name="obiective[]"]');
    obiectiveChecks.forEach(chk => {
        chk.addEventListener('change', () => {
            // Verifică dacă este selectat 'Slabire' sau 'Ingrasare'
            const showRitm = Array.from(obiectiveChecks).some(c => c.checked && (c.value === 'Slabire' || c.value === 'Ingrasare'));
            toggleField('ritm_slabire_box', showRitm);
        });
    });
    
    // Injectare Footer
    fetch('https://nutrisib.club/footer.html')
        .then(response => response.text())
        .then(data => { 
            const placeholder = document.getElementById('footer-placeholder');
            if(placeholder) placeholder.innerHTML = data; 
        })
        .catch(err => console.log('Err Footer:', err));
});

function showTab(n) {
    tabs.forEach(t => t.classList.remove('active'));
    tabs[n].classList.add('active');
    
    const progress = ((n + 1) / tabs.length) * 100;
    if(progressBar) progressBar.style.width = `${progress}%`;
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function nextTab() {
    if (!validateForm(currentTab)) return;
    
    calculeazaNutritie(); 

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
    const currentTabPanel = tabs[n];
    // Selectăm doar elementele vizibile care sunt required
    // (Excludem elementele din div-uri ascunse prin display: none)
    const allInputs = currentTabPanel.querySelectorAll('input[required], select[required], textarea[required]');
    let valid = true;
    
    // Convertim NodeList în Array pentru a putea folosi every/some sau forEach
    // Verificăm validitatea doar pentru elementele vizibile
    for (let input of allInputs) {
        if (input.offsetParent !== null) { // Verificare vizibilitate
            if (!input.checkValidity()) {
                input.reportValidity();
                valid = false;
                // Ne oprim la prima eroare pentru a nu bombarda utilizatorul cu mesaje
                break; 
            }
        }
    }
    return valid;
}

function toggleField(id, show) {
    const el = document.getElementById(id);
    if(el) {
        el.style.display = show ? 'block' : 'none';
        
        // Gestionare inteligentă a atributului 'required'
        const childrenInputs = el.querySelectorAll('input, textarea, select');
        childrenInputs.forEach(input => {
            if(show) {
                // Dacă devine vizibil, îl facem required DOAR dacă logic ar trebui să fie (ex. textareas de detalii)
                // Pentru simplitate, presupunem că câmpurile ascunse de toggle sunt required când sunt vizibile
                // sau au clasa 'conditional-required' (opțional)
                input.setAttribute('required', 'true');
            } else {
                input.removeAttribute('required');
                input.value = ''; // Resetăm valoarea la ascundere
                input.checked = false; // Pentru radio/checkbox
            }
        });
    }
}

function calculeazaNutritie() {
    const sex = document.getElementById('sex')?.value;
    const varsta = Number(document.getElementById('varsta')?.value || 0);
    const inaltimeCm = Number(document.getElementById('inaltime')?.value || 0);
    const greutate = Number(document.getElementById('greutate')?.value || 0);
    const activitate = Number(document.getElementById('activitate')?.value || 0);

    // Trebuie să avem date minime
    if (!sex || !varsta || !inaltimeCm || !greutate) return;

    const inaltimeM = inaltimeCm / 100;
    const imc = greutate / (inaltimeM * inaltimeM);
    
    let imcCategory = '';
    if (imc < 18.5) imcCategory = 'Subponderal';
    else if (imc < 25) imcCategory = 'Normal';
    else if (imc < 30) imcCategory = 'Supraponderal';
    else if (imc < 35) imcCategory = 'Obezitate gr. I';
    else if (imc < 40) imcCategory = 'Obezitate gr. II';
    else imcCategory = 'Obezitate morbidă';

    // Formule Mifflin-St Jeor (Standard de Aur)
    let rmb = 0;
    if (sex === 'Masculin') {
        rmb = (10 * greutate) + (6.25 * inaltimeCm) - (5 * varsta) + 5;
    } else {
        rmb = (10 * greutate) + (6.25 * inaltimeCm) - (5 * varsta) - 161;
    }

    const rma = activitate ? (rmb * activitate) : 0;
    
    // Estimare PGC (Procent Grăsime Corporală) - Formula Deurenberg
    const sexFactor = (sex === 'Masculin') ? 1 : 0;
    const pgc = (1.20 * imc) + (0.23 * varsta) - (10.8 * sexFactor) - 5.4;
    const mg = (pgc / 100) * greutate;

    // --- CALCUL CMA (Target Calories) ---
    // Conform logicii din sursa JotForm
    let cma = rma; // Default menținere
    
    // Identificare obiective
    const obiectiveInputs = document.querySelectorAll('input[name="obiective[]"]:checked');
    const obiectiveValues = Array.from(obiectiveInputs).map(cb => cb.value);
    
    const isSlabire = obiectiveValues.includes('Slabire');
    const isIngrasare = obiectiveValues.includes('Ingrasare');
    const ritm = document.getElementById('ritm_slabire')?.value;

    if (ritm) {
        // Multiplicatori conform JSON-ului original
        if (isSlabire) {
            if (ritm === '1') cma = rma * 0.52;      // 1 kg/sapt
            else if (ritm === '0.5') cma = rma * 0.76; // 0.5 kg/sapt
            else if (ritm === '0.25') cma = rma * 0.88;// 0.25 kg/sapt
        } else if (isIngrasare) {
            if (ritm === '1') cma = rma * 1.48;      // 1 kg/sapt
            else if (ritm === '0.5') cma = rma * 1.24; // 0.5 kg/sapt
            else if (ritm === '0.25') cma = rma * 1.12;// 0.25 kg/sapt
        }
    }

    // Update Hidden Inputs (pentru Netlify/PDF)
    updateVal('hidden_imc', imc.toFixed(2));
    updateVal('hidden_imc_cat', imcCategory);
    updateVal('hidden_rmb', rmb.toFixed(0));
    updateVal('hidden_rma', rma.toFixed(0));
    // Stocăm și CMA chiar dacă nu e afișat explicit în Tab 7, e util pentru PDF
    const hiddenCma = document.getElementById('hidden_cma') || createHiddenInput('hidden_cma');
    hiddenCma.value = cma.toFixed(0);

    // Update Visible Read-only Inputs (Tab Rezultate)
    updateVal('calc_greutate', greutate);
    updateVal('calc_inaltime', inaltimeCm);
    updateVal('calc_imc', imc.toFixed(2));
    updateVal('calc_conformatie', imcCategory);
    updateVal('calc_rmb', rmb.toFixed(0));
    updateVal('calc_rma', rma.toFixed(0));
    updateVal('calc_pgc', pgc > 0 ? pgc.toFixed(1) : '-');
    updateVal('calc_mg', mg > 0 ? mg.toFixed(1) : '-');
}

function updateVal(id, val) {
    const el = document.getElementById(id);
    if(el) el.value = val;
}

function createHiddenInput(id) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.id = id;
    input.name = id; // pentru netlify
    document.querySelector('form').appendChild(input);
    return input;
}

function setText(id, text) {
    const el = document.getElementById(id);
    if(el) el.textContent = text;
}

// SUBMIT FINAL
async function handleFinalSubmit(e) {
    e.preventDefault();
    const form = document.getElementById('wellnessForm');
    
    if(!form.checkValidity()) { 
        form.reportValidity(); 
        return; 
    }

    calculeazaNutritie(); // Asigură-te că ultimele valori sunt calculate

    // Pregătire date PDF
    const fullName = (document.getElementById('nume').value || '') + ' ' + (document.getElementById('prenume').value || '');
    setText('pdf_nume', fullName);
    setText('pdf_imc', document.getElementById('calc_imc').value);
    setText('pdf_imc_cat', document.getElementById('calc_conformatie').value);
    setText('pdf_rmb', document.getElementById('calc_rmb').value);
    setText('pdf_rma', document.getElementById('calc_rma').value);
    
    // Adăugăm CMA în PDF dacă există un obiectiv setat
    const cmaVal = document.getElementById('hidden_cma')?.value;
    const cmaElement = document.createElement('p');
    cmaElement.innerHTML = `<strong>Rata Calorică Propusă (CMA):</strong> ${cmaVal} kcal`;
    const resultsContainer = document.querySelector('#pdf-report h3').nextElementSibling.parentElement;
    // Evităm duplicarea dacă userul apasă de mai multe ori
    if(!resultsContainer.innerHTML.includes('Rata Calorică Propusă')) {
        resultsContainer.insertBefore(cmaElement, resultsContainer.querySelector('div')); // Insert before copyright div
    }

    const element = document.getElementById('pdf-report');
    element.style.display = 'block';
    
    const opt = { 
        margin: 15, 
        filename: `Raport_Wellness_${fullName.replace(/\s+/g, '_')}.pdf`, 
        image: { type: 'jpeg', quality: 0.98 }, 
        html2canvas: { scale: 2 }, 
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' } 
    };
    
    try {
        await html2pdf().set(opt).from(element).save();
    } catch (err) {
        console.error("PDF generation failed", err);
    }
    
    element.style.display = 'none';
    
    // Trimite formularul către Netlify
    form.submit();
}