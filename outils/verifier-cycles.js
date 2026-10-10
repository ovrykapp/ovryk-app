/* Vérifie les 17 cycles (12 génériques et A à E, lot 07) : une seule semaine
   de test, test en dernière semaine, durée de 6 à 8 semaines, pourcentages
   entre 1 et 100, reps positives. */
const { FORCE_CYCLES, GENERIC_CYCLE_IDS, CYCLE_LETTERS, CYCLE_NAMES } = require('./extraire-cycles.js')();
const ALL_CYCLE_IDS = GENERIC_CYCLE_IDS.concat(CYCLE_LETTERS);
let erreurs = 0;
ALL_CYCLE_IDS.forEach(function (id) {
  const semaines = FORCE_CYCLES[id];
  const problemes = [];
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
  console.log((problemes.length ? 'ERREUR ' : 'ok     ') + 'cycle ' + id + ' (' + semaines.length + ' sem.) ' + CYCLE_NAMES[id] + (problemes.length ? ' : ' + problemes.join(', ') : ''));
  if (problemes.length) erreurs++;
});
console.log(erreurs ? '\n' + erreurs + ' cycle(s) à corriger' : '\nTous les cycles sont valides');
process.exit(erreurs ? 1 : 0);
