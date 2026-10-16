"""Preuve que la suite test_restore_* sait échouer : chaque mutation abîme UNE garde
de la restauration locale dans une COPIE de index.html (dossier temporaire, jamais
le fichier du dépôt), sert cette copie sur un port libre, lance le fichier de test
visé avec OVRYK_URL, et exige au moins un échec. Une mutation dont l'ancre est
introuvable ou qui ne casse aucun test compte comme un échec de l'outil.
Témoins : chaque fichier visé est d'abord lancé sur une copie NON abîmée et doit
tout réussir (sinon les échecs des mutations ne prouveraient rien).
Ancres = extraits de code, jamais de numéros de ligne. Aucune dépendance à git.
Usage : python3 mutations_restore.py <dossier de travail> [numéro de mutation ...]"""
import sys, os, re, socket, subprocess, time, shutil, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = ROOT / 'index.html'

# (numéro, garde abîmée, fichier visé, [(ancre, remplacement, nombre d'occurrences attendu)])
MUTATIONS = [
    (1, 'getBackupCrashError renvoie toujours null', 'refus',
     [('function getBackupCrashError(data) {', 'function getBackupCrashError(data) { return null;', 1)]),
    (2, 'contrôle d\'empreinte retiré', 'refus',
     [('parsed.summary.checksum !== hashBackupString(JSON.stringify(data))', 'false', 1)]),
    (3, 'refus d\'un schemaVersion plus récent retiré', 'refus',
     [('data.meta.schemaVersion > CURRENT_SCHEMA_VERSION', 'data.meta.schemaVersion > 999', 1)]),
    (4, 'retour arrière après écriture partielle retiré', 'ecriture',
     [('if (writeRawOvrykState(before) || sameRawState(readRawOvrykState(), before)) {', 'if (true) {', 1)]),
    (5, 'abandon à 10 s retiré (délai rendu infini)', 'ecriture',
     [('}, RESTORE_COPY_TIMEOUT_MS);', '}, 1e9);', 1)]),
    (6, 'copie arrivée après l\'abandon gardée', 'ecriture',
     [('if (isAbandoned && isAbandoned()) {', 'if (false) {', 2)]),
    (7, 'marque de restauration jamais posée', 'annulation',
     [('localStorage.setItem(RESTORE_MARK_KEY, JSON.stringify({ pointId: pointId, startedAt: new Date().toISOString(), mode: st.mode }));', 'void 0;', 1)]),
    (8, 'libellé toujours "Annuler"', 'annulation',
     [("return reason === 'avant annulation' ? 'Rétablir la restauration annulée' : 'Annuler la dernière restauration';",
       "return 'Annuler la dernière restauration';", 1)]),
    (9, 'séances perdues comptées par nombre et non par identifiant', 'annulation',
     [('return getMissingCompletedSessionIds(OvrykDB.getSessions(), st.incomingSessions);',
       "var cur = OvrykDB.getSessions().filter(function (s) { return s && s.status === 'completed'; });"
       " var inc = (st.incomingSessions || []).filter(function (s) { return s && s.status === 'completed'; });"
       " return cur.length > inc.length ? cur.slice(inc.length) : [];", 1)]),
    (10, 'copies gardées : 6 au lieu de 5', 'annulation',
     [('var RESTORE_KEEP = 5;', 'var RESTORE_KEEP = 6;', 1)]),
    (11, 'copies quotidiennes non supprimées par Réinitialiser', 'reinit',
     [('dailyKeys.forEach(function (key) { localStorage.removeItem(key); });', '', 1)]),
    (12, 'échec de suppression de la base de copies ignoré', 'reinit',
     [('if (!err) { wipeAppDataAndReload(); return; }', 'wipeAppDataAndReload(); return;', 1)]),
    (13, 'contrôle de clé illisible retiré de getBackupBlocker', 'export',
     [('try { JSON.parse(rawValue); } catch (e) {', 'try { } catch (e) {', 1)]),
    (14, 'lastExportAt écrit avant le succès du partage', 'export',
     [("navigator.share({ files: [file], title: 'Sauvegarde Ovryk' }).then(function () {\n"
       "      var settings = OvrykDB.getSettings();\n"
       "      settings.lastExportAt = new Date().toISOString();\n"
       "      OvrykDB.saveSettings(settings);",
       "var settings = OvrykDB.getSettings();\n"
       "    settings.lastExportAt = new Date().toISOString();\n"
       "    OvrykDB.saveSettings(settings);\n"
       "    navigator.share({ files: [file], title: 'Sauvegarde Ovryk' }).then(function () {", 1)]),
]

def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close(); return port

def serve(folder):
    port = free_port()
    proc = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1'], cwd=str(folder),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = 'http://127.0.0.1:%d/index.html' % port
    for _ in range(50):
        try:
            urllib.request.urlopen(url, timeout=1).read(1); return proc, url
        except Exception: time.sleep(0.1)
    proc.kill(); raise RuntimeError('serveur temporaire injoignable')

def run_test(target, html, work, label):
    """sert html dans un dossier neuf, lance test_restore_<target>.py ; renvoie (code, nb d'échecs, dernière ligne, sortie)."""
    site = work / ('site-' + label); shutil.rmtree(site, ignore_errors=True); site.mkdir(parents=True)
    (site / 'index.html').write_text(html, encoding='utf-8')
    out_dir = work / ('sortie-' + label); shutil.rmtree(out_dir, ignore_errors=True); out_dir.mkdir(parents=True)
    proc, url = serve(site)
    try:
        r = subprocess.run([sys.executable, str(HERE / ('test_restore_%s.py' % target)), str(out_dir)], cwd=str(HERE),
                           env=dict(os.environ, OVRYK_URL=url), capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or '') if isinstance(e.stdout, str) else ''
        r = type('R', (), {'returncode': 124})()
    finally:
        proc.kill()
    fails = [l for l in out.splitlines() if l.startswith('ECHEC')]
    last = [l for l in out.splitlines() if re.match(r'^\d+/\d+$', l)]
    (work / ('log-' + label + '.txt')).write_text(out, encoding='utf-8')
    return r.returncode, fails, (last[-1] if last else '(pas de total : %s)' % out.strip().splitlines()[-1:] ), out

def mutate(src, edits):
    for anchor, repl, count in edits:
        n = src.count(anchor)
        if n != count: return None, 'ANCRE INTROUVABLE OU AMBIGUË (%d occurrence(s) au lieu de %d) : %s' % (n, count, anchor[:60])
        src = src.replace(anchor, repl)
    return src, None

def main():
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    work = Path(sys.argv[1]).resolve(); work.mkdir(parents=True, exist_ok=True)
    if ROOT in work.parents or work == ROOT: print('Le dossier de travail doit être hors du dépôt.'); sys.exit(2)
    only = {int(x) for x in sys.argv[2:]}
    chosen = [m for m in MUTATIONS if not only or m[0] in only]
    original = SOURCE.read_text(encoding='utf-8')
    t0 = time.time()

    print('Témoins (copie non abîmée, tout doit réussir) :')
    temoins_ok = True
    for target in sorted({m[2] for m in chosen}):
        code, fails, last, _ = run_test(target, original, work, 'temoin-' + target)
        ok = code == 0 and not fails
        temoins_ok &= ok
        print('  %-11s %s %s' % (target, 'OK   ' if ok else 'ECHEC', last))
    if not temoins_ok:
        print('Arrêt : un témoin échoue sans mutation, les résultats des mutations ne prouveraient rien.'); sys.exit(1)

    print('\nMutations :')
    rows = []
    for num, label, target, edits in chosen:
        mutated, err = mutate(original, edits)
        if err:
            rows.append((num, label, target, 'ÉCHEC OUTIL', err)); print('  M%02d %s' % (num, err)); continue
        start = time.time()
        code, fails, last, _ = run_test(target, mutated, work, 'm%02d' % num)
        killed = code != 0 and bool(fails)
        detail = '%s, %d contrôle(s) en échec : %s' % (last, len(fails), '; '.join(f[7:60] for f in fails[:2]))
        rows.append((num, label, target, 'DÉTECTÉE' if killed else 'NON DÉTECTÉE', detail))
        print('  M%02d %-12s %-58s %s (%d s)' % (num, 'DÉTECTÉE' if killed else 'NON DÉTECTÉE', label[:58], detail[:110], time.time() - start))
    assert SOURCE.read_text(encoding='utf-8') == original, 'index.html du dépôt modifié : impossible'
    detected = sum(1 for r in rows if r[3] == 'DÉTECTÉE')
    print('\n%d/%d mutations détectées en %d s ; index.html du dépôt inchangé.' % (detected, len(rows), time.time() - t0))
    sys.exit(0 if detected == len(rows) else 1)

if __name__ == '__main__':
    main()
