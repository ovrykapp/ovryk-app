/* Vérifie les 37 cycles : les 17 anciens (12 génériques et A à E, lot 07),
   et les 20 cycles C1 à C20 du tirage (v161). Pour tous : une seule semaine
   de test, test en dernière semaine, durée de 6 à 8 semaines, pourcentages
   entre 1 et 100, reps positives. Pour C1 à C20 en plus : 6 semaines
   (S6 allégée, test séparé en semaine 7) ou 8 semaines (S4 allégée, S8
   test), une seule semaine allégée, aucun pourcentage au dessus de 90 ni
   série au dessus de 3 reps hors test, type et explication présents,
   aucun tiret long ou moyen, charges calculables depuis un 1RM.
   v162, pour 12 cycles à montée de charge (RAMP_CYCLE_IDS), sur plusieurs
   1RM : la dernière série garde le % du gabarit, les kg ne baissent jamais
   d'une série à la suivante, plancher 20 kg, échauffement et test
   inchangés, une échelle garde une seule charge. Les 8 autres cycles et les
   anciens restent exactement leur gabarit. */
const { FORCE_CYCLES, GENERIC_CYCLE_IDS, CYCLE_LETTERS, NEW_CYCLE_IDS, CYCLE_META, CYCLE_NAMES, RAMP_CYCLE_IDS, getCycleWeekAt, computeWeightFromPercent } = require('./extraire-cycles.js')();
const ANCIENS = GENERIC_CYCLE_IDS.concat(CYCLE_LETTERS);
const TYPES = ['Volume', 'Technique', 'Mixte', 'Intensité'];
let erreurs = 0;

function verifierBase(id, semaines, problemes) {
  if (semaines.length < 6 || semaines.length > 8) problemes.push('durée ' + semaines.length + ' semaines');
  const tests = semaines.filter(function (w) { return w.isTestWeek; });
  if (tests.length !== 1) problemes.push(tests.length + ' semaines de test');
  if (!semaines[semaines.length - 1].isTestWeek) problemes.push('la dernière semaine n\'est pas le test');
  semaines.forEach(function (w, i) {
    if (w.week !== i + 1) problemes.push('numéro de semaine incohérent en position ' + (i + 1));
    if (!w.sets.length) problemes.push('semaine ' + w.week + ' sans série');
    /* lot 13 : drapeau deload posé si et seulement si la phase commence par "Allégée" */
    if (/^Allégée/.test(w.phase) !== !!w.deload) problemes.push('semaine ' + w.week + ' : drapeau deload incohérent avec la phase');
    if (w.deload && w.isTestWeek) problemes.push('semaine ' + w.week + ' : allégée et test à la fois');
    w.sets.forEach(function (s) {
      if (!(s.reps > 0)) problemes.push('semaine ' + w.week + ' : reps invalides');
      if (!(s.percent > 0 && s.percent <= 100)) problemes.push('semaine ' + w.week + ' : pourcentage invalide ' + s.percent);
    });
  });
}

function verifierNouveau(id, semaines, problemes) {
  const meta = CYCLE_META[id];
  if (!meta || TYPES.indexOf(meta.type) === -1) problemes.push('type absent ou inconnu');
  if (!meta || !meta.explication) problemes.push('explication absente');
  const textes = [CYCLE_NAMES[id], meta && meta.explication].concat(semaines.map(function (w) { return w.phase; }));
  if (textes.some(function (t) { return /[–—]/.test(t || ''); })) problemes.push('tiret long ou moyen dans un texte');
  const deloads = semaines.filter(function (w) { return w.deload; }).map(function (w) { return w.week; });
  if (semaines.length === 7) {
    if (deloads.join() !== '6') problemes.push('6 semaines : S6 doit être la seule allégée (' + deloads.join() + ')');
    if (semaines[6].phase !== 'Test 1RM séparé') problemes.push('6 semaines : test séparé attendu en semaine 7');
  } else if (semaines.length === 8) {
    if (deloads.join() !== '4') problemes.push('8 semaines : S4 doit être la seule allégée (' + deloads.join() + ')');
  } else {
    problemes.push('durée inattendue ' + semaines.length);
  }
  semaines.forEach(function (w) {
    if (w.isTestWeek) return;
    w.sets.forEach(function (s) {
      if (s.percent > 90) problemes.push('semaine ' + w.week + ' : ' + s.percent + ' % au dessus de 90');
      if (s.reps > 3) problemes.push('semaine ' + w.week + ' : ' + s.reps + ' reps au dessus de 3');
    });
  });
  /* charges calculées sur un 1RM de 100 kg, arrondies au 0,5 kg : toutes positives */
  semaines.forEach(function (w) {
    w.sets.forEach(function (s) {
      const kg = Math.round(100 * s.percent / 100 * 2) / 2;
      if (!(kg > 0)) problemes.push('semaine ' + w.week + ' : charge non calculable');
    });
  });
}

const UN_RM = [40, 70, 100, 137.5, 250];
function verifierMontee(id, semaines, problemes) {
  const montee = RAMP_CYCLE_IDS.indexOf(id) !== -1;
  if (montee !== !!(CYCLE_META[id] && CYCLE_META[id].montee)) problemes.push('drapeau montee incohérent');
  semaines.forEach(function (w) {
    if (montee && !w.isTestWeek && !/jusqu'à \d+ %/.test(w.phase)) problemes.push('semaine ' + w.week + ' : phase sans "jusqu\'à"');
    UN_RM.forEach(function (rm) {
      const sets = getCycleWeekAt({ cycle_actif: id, one_rm_actuel: rm, semaines_modifiees: {} }, w.week).sets;
      const ou = 'semaine ' + w.week + ', 1RM ' + rm + ' : ';
      if (sets.length !== w.sets.length) { problemes.push(ou + 'nombre de séries changé'); return; }
      if (!montee || w.isTestWeek) {
        if (JSON.stringify(sets) !== JSON.stringify(w.sets)) problemes.push(ou + 'séries modifiées hors montée');
        return;
      }
      if (sets[sets.length - 1].percent !== w.sets[w.sets.length - 1].percent) problemes.push(ou + 'dernière série hors % du gabarit');
      let precedent = null;
      sets.forEach(function (s, i) {
        const kg = computeWeightFromPercent(rm, s.percent);
        if (s.warmup) {
          if (s.percent !== w.sets[i].percent) problemes.push(ou + 'échauffement modifié');
          return;
        }
        if (s.reps !== w.sets[i].reps) problemes.push(ou + 'reps modifiées');
        if (kg < Math.min(20, computeWeightFromPercent(rm, w.sets[w.sets.length - 1].percent))) problemes.push(ou + 'sous le plancher de 20 kg');
        if (precedent !== null && kg < precedent) problemes.push(ou + 'kg en baisse série ' + (i + 1));
        if (w.sets[i].ladder != null && i > 0 && w.sets[i - 1].ladder === w.sets[i].ladder && kg !== precedent) problemes.push(ou + 'charge qui change dans une échelle');
        precedent = kg;
      });
    });
  });
}

ANCIENS.concat(NEW_CYCLE_IDS).forEach(function (id) {
  const semaines = FORCE_CYCLES[id];
  const problemes = [];
  verifierBase(id, semaines, problemes);
  if (NEW_CYCLE_IDS.indexOf(id) !== -1) verifierNouveau(id, semaines, problemes);
  verifierMontee(id, semaines, problemes);
  console.log((problemes.length ? 'ERREUR ' : 'ok     ') + 'cycle ' + id + ' (' + semaines.length + ' sem.) ' + CYCLE_NAMES[id] + (problemes.length ? ' : ' + problemes.join(', ') : ''));
  if (problemes.length) erreurs++;
});
if (NEW_CYCLE_IDS.length !== 20) { console.log('ERREUR ' + NEW_CYCLE_IDS.length + ' cycles dans le tirage au lieu de 20'); erreurs++; }
NEW_CYCLE_IDS.forEach(function (id) {
  if (ANCIENS.indexOf(id) !== -1) { console.log('ERREUR id ' + id + ' en collision avec un ancien cycle'); erreurs++; }
});
console.log(erreurs ? '\n' + erreurs + ' cycle(s) à corriger' : '\nTous les cycles sont valides');
process.exit(erreurs ? 1 : 0);
