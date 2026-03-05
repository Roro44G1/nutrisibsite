// Actualizare numerică pentru toate slider-ele (range)
document.querySelectorAll('input[type="range"]').forEach(range => {
  const span = document.querySelector(`.range-value[data-for="${range.id}"]`);
  if (!span) return;

  const update = () => span.textContent = range.value;
  range.addEventListener('input', update);
  update();
});

// Exemplu de calcul de scoruri (simplificat).
// Aici vom înlocui cu logica exactă din Jotform când ai nevoie.
function calculeazaNutritie() {
  const sex = document.getElementById('sex')?.value;
  const varsta = Number(document.getElementById('varsta')?.value || 0);
  const inaltimeCm = Number(document.getElementById('inaltime')?.value || 0);
  const greutate = Number(document.getElementById('greutate')?.value || 0);
  const activitate = Number(document.getElementById('activitate')?.value || 0);

  if (!sex || !varsta || !inaltimeCm || !greutate || !activitate) {
    return; // nu calculăm până nu sunt completate toate
  }

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

  // Harris-Benedict (kcal/zi)
  let rmb = 0;
  if (sex === 'M') {
    // masculin
    // RMB = 88.362 + (13.397 × greutate kg) + (4.799 × înălțime cm) − (5.677 × vârsta ani)
    rmb = 88.362 + 13.397 * greutate + 4.799 * inaltimeCm - 5.677 * varsta;
  } else if (sex === 'F') {
    // feminin
    // RMB = 447.593 + (9.247 × greutate kg) + (3.098 × înălțime cm) − (4.330 × vârsta ani)
    rmb = 447.593 + 9.247 * greutate + 3.098 * inaltimeCm - 4.330 * varsta;
  }

  const rma = rmb * activitate;      // Rata metabolică activă
  const cma = rma;                   // aici poți adăuga ulterior ajustări (ex. -10% deficit etc.)

  // scriem în câmpurile ascunse
  document.getElementById('imc').value = imc.toFixed(2);
  document.getElementById('imc_category').value = imcCategory;
  document.getElementById('rmb').value = rmb.toFixed(0);
  document.getElementById('rma').value = rma.toFixed(0);
  document.getElementById('cma').value = cma.toFixed(0);
}

// recalculăm când utilizatorul schimbă datele antropometrice
['sex', 'varsta', 'inaltime', 'greutate', 'activitate'].forEach(id => {
  const el = document.getElementById(id);
  if (el) {
    el.addEventListener('change', calculeazaNutritie);
    el.addEventListener('input', calculeazaNutritie);
  }
});

// la submit calculăm atât scorurile (dacă le folosești), cât și partea nutrițională
if (form) {
  form.addEventListener('submit', function (e) {
    calculeazaScoruri();    // dacă folosești scorurile de wellness
    calculeazaNutritie();   // asigură-te că IMC/RMB etc. sunt setate

    // nu anulăm submit-ul; Netlify îl procesează normal
  });
}


if (form) {
  form.addEventListener('submit', function (e) {
    // aici poți adăuga validări suplimentare dacă e nevoie
    calculeazaScoruri();
    // nu dăm preventDefault, lăsăm Netlify să trimită formularul
  });
}

