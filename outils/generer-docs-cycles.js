/* Régénère docs/CYCLES.md à partir de index.html. Usage : node outils/generer-docs-cycles.js */
const fs = require('fs');
const path = require('path');
const { FORCE_CYCLES, GENERIC_CYCLE_IDS, NEW_CYCLE_IDS, CYCLE_META, CYCLE_NAMES } = require('./extraire-cycles.js')();

function resume(sets) {
  const groupes = [];
  sets.forEach(function (s) {
    const dernier = groupes[groupes.length - 1];
    if (dernier && dernier.reps === s.reps && dernier.percent === s.percent) dernier.n++;
    else groupes.push({ reps: s.reps, percent: s.percent, n: 1 });
  });
  return groupes.map(function (g) {
    return (g.n > 1 ? g.n + ' x ' : '') + g.reps + ' à ' + g.percent + ' %';
  }).join(', ');
}

let md = '# Les 20 cycles du tirage (C1 à C20)\n\n' +
  'Depuis v161, seuls ces 20 cycles sont tirés au sort. Chaque cycle est un gabarit de pourcentages du 1RM, une séance par semaine et par mouvement.\n' +
  'Cycles de 6 semaines : S6 allégée, puis une semaine 7 de test 1RM séparé. Cycles de 8 semaines : S4 allégée, S8 test 1RM (paliers puis 3 essais).\n' +
  'Après un cycle de type Intensité, le tirage ne propose que Volume, Technique ou Mixte. Fichier généré : ne pas modifier à la main.\n';
NEW_CYCLE_IDS.forEach(function (id) {
  const semaines = FORCE_CYCLES[id];
  md += '\n## Cycle ' + id.slice(1) + ' (' + id + ') : ' + CYCLE_NAMES[id] + ' (' + CYCLE_META[id].type + ', ' + (semaines.length === 7 ? '6 semaines + test' : semaines.length + ' semaines') + ')\n\n';
  md += CYCLE_META[id].explication + '\n\n';
  md += '| Semaine | Phase | Séries (reps à % du 1RM) | Repos |\n|---|---|---|---|\n';
  semaines.forEach(function (w) {
    md += '| ' + w.week + ' | ' + w.phase + ' | ' + resume(w.sets) + ' | ' + (w.timed ? 'chronométré' : w.restSeconds + ' s') + ' |\n';
  });
});
md += '\n# Les 12 anciens cycles génériques (hors tirage, affichés Ancien cycle 1 à 12)\n\n' +
  'Gardés pour les cycles déjà en cours et l\'historique.\n';
GENERIC_CYCLE_IDS.forEach(function (id) {
  const semaines = FORCE_CYCLES[id];
  md += '\n## Ancien cycle ' + id + ' : ' + CYCLE_NAMES[id] + ' (' + semaines.length + ' semaines)\n\n';
  md += '| Semaine | Phase | Séries (reps à % du 1RM) | Repos |\n|---|---|---|---|\n';
  semaines.forEach(function (w) {
    md += '| ' + w.week + ' | ' + w.phase + ' | ' + resume(w.sets) + ' | ' + (w.timed ? 'chronométré' : w.restSeconds + ' s') + ' |\n';
  });
});
fs.writeFileSync(path.join(__dirname, '..', 'docs', 'CYCLES.md'), md);
console.log('docs/CYCLES.md régénéré');
