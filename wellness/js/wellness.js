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
function calculeazaScoruri() {
  // TODO: înlocuiește cu lista reală de câmpuri pentru fiecare domeniu
  const fizicFields = ['fizic_energie']; // + restul
  const mentalFields = []; // de completat
  const spiritualFields = [];
  const financiarFields = [];
  const ocupationalFields = [];
  const socialFields = [];
  const intelectualFields = [];
  const mediuFields = [];

  function medie(ids) {
    if (!ids.length) return 0;
    let sum = 0;
    ids.forEach(id => {
      const el = document.getElementById(id);
      if (el) sum += Number(el.value || 0);
    });
    return sum / ids.length;
  }

  const sFizic = medie(fizicFields);
  const sMental = medie(mentalFields);
  const sSpiritual = medie(spiritualFields);
  const sFinanciar = medie(financiarFields);
  const sOcupational = medie(ocupationalFields);
  const sSocial = medie(socialFields);
  const sIntelectual = medie(intelectualFields);
  const sMediu = medie(mediuFields);

  const total = (
    sFizic + sMental + sSpiritual +
    sFinanciar + sOcupational + sSocial +
    sIntelectual + sMediu
  ) / 8;

  document.getElementById('score_fizic').value = sFizic.toFixed(2);
  document.getElementById('score_mental').value = sMental.toFixed(2);
  document.getElementById('score_spiritual').value = sSpiritual.toFixed(2);
  document.getElementById('score_financiar').value = sFinanciar.toFixed(2);
  document.getElementById('score_ocupational').value = sOcupational.toFixed(2);
  document.getElementById('score_social').value = sSocial.toFixed(2);
  document.getElementById('score_intelectual').value = sIntelectual.toFixed(2);
  document.getElementById('score_mediu').value = sMediu.toFixed(2);
  document.getElementById('score_total').value = total.toFixed(2);

  // Exemplu: profil în funcție de scor total (poți schimba logică)
  let profil = 'În lucru';
  if (total >= 8) profil = 'High Wellness';
  else if (total >= 5) profil = 'Balanced';
  else profil = 'Needs Support';

  document.getElementById('profil_wellness').value = profil;
}

// Legăm calculul de submit, astfel încât scorurile să fie în Netlify Forms
const form = document.getElementById('wellnessForm');

if (form) {
  form.addEventListener('submit', function (e) {
    // aici poți adăuga validări suplimentare dacă e nevoie
    calculeazaScoruri();
    // nu dăm preventDefault, lăsăm Netlify să trimită formularul
  });
}
