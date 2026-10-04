/* Extrait les définitions de cycles de ../index.html pour les vérifier ou les documenter.
   Usage : node outils/verifier-cycles.js   ou   node outils/generer-docs-cycles.js */
const fs = require('fs');
const path = require('path');
module.exports = function charger() {
  const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
  const debut = html.indexOf('  function repeatSet(reps, percent, count) {');
  const fin = html.indexOf('  function getCycleWeek(cycle) {');
  if (debut < 0 || fin < 0) throw new Error('Définitions de cycles introuvables dans index.html');
  const code = 'var CYCLE_NAMES = {};\nvar FORCE_CYCLES = {};\n' +
    html.slice(debut, fin) +
    '\nreturn { CYCLE_NAMES: CYCLE_NAMES, FORCE_CYCLES: FORCE_CYCLES, GENERIC_CYCLE_IDS: GENERIC_CYCLE_IDS, cycleLength: cycleLength };';
  return new Function(code)();
};
