/* Régénère docs/CYCLES.md à partir de index.html. Usage : node outils/generer-docs-cycles.js */
const fs = require('fs');
const path = require('path');
const { FORCE_CYCLES, GENERIC_CYCLE_IDS, CYCLE_NAMES } = require('./extraire-cycles.js')();

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

let md = '# Les 12 cycles génériques\n\n' +
  'Chaque cycle est un gabarit de pourcentages du 1RM, applicable à n\'importe quel mouvement.\n' +
  'Cycles de 8 semaines : la semaine 8 est le test 1RM. Cycles de 7 semaines : 6 semaines de travail puis une semaine 7 de test 1RM séparé.\n' +
  'Le cycle 12 dure 6 semaines et contient son propre test.\n' +
  'Les pourcentages viennent des PDF de cycles. Les vagues du type 3-2-1 sont lues comme 3 reps, 2 reps puis 1 rep. Fichier généré : ne pas modifier à la main.\n';
GENERIC_CYCLE_IDS.forEach(function (id) {
  const semaines = FORCE_CYCLES[id];
  md += '\n## Cycle ' + id + ' : ' + CYCLE_NAMES[id] + ' (' + semaines.length + ' semaines)\n\n';
  md += '| Semaine | Phase | Séries (reps à % du 1RM) | Repos |\n|---|---|---|---|\n';
  semaines.forEach(function (w) {
    md += '| ' + w.week + ' | ' + w.phase + ' | ' + resume(w.sets) + ' | ' + (w.timed ? 'chronométré' : w.restSeconds + ' s') + ' |\n';
  });
});
fs.writeFileSync(path.join(__dirname, '..', 'docs', 'CYCLES.md'), md);
console.log('docs/CYCLES.md régénéré');
