/* Extrait les définitions de cycles de ../index.html pour les vérifier ou les documenter.
   Usage : node outils/verifier-cycles.js   ou   node outils/generer-docs-cycles.js */
const fs = require('fs');
const path = require('path');
module.exports = function charger() {
  const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
  const debut = html.indexOf('  function repeatSet(reps, percent, count) {');
  const fin = html.indexOf('  function getCycleWeek(cycle) {');
  if (debut < 0 || fin < 0) throw new Error('Définitions de cycles introuvables dans index.html');
  /* v162 : applyCycleRamp (montée de charge) a besoin du calcul des kg de l'app */
  const debutKg = html.indexOf('  function computeWeightFromPercent(oneRepMax, percent) {');
  const finKg = html.indexOf('\n  }\n', debutKg) + 5;
  if (debutKg < 0) throw new Error('computeWeightFromPercent introuvable dans index.html');
  const code = 'var CYCLE_NAMES = {};\nvar FORCE_CYCLES = {};\n' +
    html.slice(debutKg, finKg) + '\n' +
    html.slice(debut, fin) +
    '\nreturn { CYCLE_NAMES: CYCLE_NAMES, FORCE_CYCLES: FORCE_CYCLES, GENERIC_CYCLE_IDS: GENERIC_CYCLE_IDS, CYCLE_LETTERS: CYCLE_LETTERS, NEW_CYCLE_IDS: NEW_CYCLE_IDS, CYCLE_META: CYCLE_META, RAMP_CYCLE_IDS: RAMP_CYCLE_IDS, getCycleWeekAt: getCycleWeekAt, computeWeightFromPercent: computeWeightFromPercent, cycleLength: cycleLength };';
  return new Function(code)();
};
