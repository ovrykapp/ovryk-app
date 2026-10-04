/* Exporte les 12 cycles génériques de index.html vers data/cycles_generiques.json.
   Usage : node outils/exporter-cycles-json.js
   Le fichier est généré : la source de vérité reste FORCE_CYCLES dans index.html. */
const fs = require('fs');
const path = require('path');
const { FORCE_CYCLES, GENERIC_CYCLE_IDS, CYCLE_NAMES } = require('./extraire-cycles.js')();

const cycles = GENERIC_CYCLE_IDS.map(function (id) {
  const semaines = FORCE_CYCLES[id];
  const derniere = semaines[semaines.length - 1];
  return {
    id: id,
    nom: CYCLE_NAMES[id],
    duree_semaines: semaines.length,
    test_1rm: derniere.phase === 'Test 1RM séparé' ? 'séparé en dernière semaine'
      : (semaines.length === 6 ? 'inclus dans la semaine 6' : 'dernière semaine'),
    semaines: semaines
  };
});

const sortie = {
  _info: 'Généré par outils/exporter-cycles-json.js depuis index.html. Ne pas modifier à la main.',
  nombre_de_cycles: cycles.length,
  cycles: cycles
};
fs.mkdirSync(path.join(__dirname, '..', 'data'), { recursive: true });
fs.writeFileSync(path.join(__dirname, '..', 'data', 'cycles_generiques.json'), JSON.stringify(sortie, null, 2) + '\n');
console.log('data/cycles_generiques.json écrit (' + cycles.length + ' cycles)');
