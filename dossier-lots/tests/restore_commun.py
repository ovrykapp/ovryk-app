"""Outils communs des suites test_restore_* (restauration locale, lot 16).
Données FABRIQUÉES ici uniquement : aucun vrai export, aucun fichier de
backups/, aucun appel réseau (toute requête hors du site local est coupée
et notée). Aucune dépendance à git.
Adresse du site : variable d'environnement OVRYK_URL (par défaut
http://127.0.0.1:8765/index.html), pour que mutations_restore.py puisse
lancer les mêmes tests sur une copie abîmée servie ailleurs."""
import os, sys, json, time
from pathlib import Path

URL = os.environ.get('OVRYK_URL', 'http://127.0.0.1:8765/index.html')
DATA_KEYS = ['ovryk.exercises', 'ovryk.routines', 'ovryk.sessions', 'ovryk.settings', 'ovryk.forceCycles', 'ovryk.meta']
MARK = 'ovryk.restoreInProgress'

res = []
def check(c, m):
    res.append(bool(c)); print(('ok     ' if c else 'ECHEC  ') + m); sys.stdout.flush()
def constat(m): print('CONSTAT ' + m); sys.stdout.flush()
def done():
    print('\n%d/%d' % (sum(res), len(res)))
    sys.exit(0 if res and all(res) else 1)
def workdir():
    if len(sys.argv) < 2: print('Usage : python3 %s <dossier de travail>' % sys.argv[0]); sys.exit(2)
    d = Path(sys.argv[1]) / 'files'; d.mkdir(parents=True, exist_ok=True); return d

# ---------- empreinte : même calcul que hashBackupString (FNV-1a 32 bits sur JSON.stringify) ----------
def js_stringify(v): return json.dumps(v, separators=(',', ':'), ensure_ascii=False)
def fnv(s):
    h = 0x811c9dc5
    for ch in s:
        o = ord(ch)
        for unit in ([o] if o < 0x10000 else [0xD800 + ((o - 0x10000) >> 10), 0xDC00 + ((o - 0x10000) & 0x3FF)]):
            h ^= unit
            h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) & 0xFFFFFFFF
    return '%08x' % h

# ---------- données fabriquées ----------
CYCLE = {'exercise_id': 'ex-fab-l', 'cycle_actif': '1', 'semaine_actuelle': 2, 'one_rm_actuel': 100, 'historique_1rm': [], 'historique_cycles': [],
         'prochain_cycle': None, 'en_attente_de_validation': False, 'semaines_modifiees': {}, 'test_report_used': False, 'decalage_semaines': 0}
def ex(eid, name, cat='Pectoraux'):
    return {'id': eid, 'name': name, 'category': cat, 'equipment': 'Barre', 'unit': 'kg', 'isCustom': True}
def done_session(sid, day, month=9, ex_id='ex-fab-1'):
    d = '2026-%02d-%02d' % (month, day)
    return {'id': sid, 'status': 'completed', 'date': d + 'T10:00:00.000Z', 'startedAt': d + 'T10:00:00.000Z', 'completedAt': d + 'T11:00:00.000Z',
            'durationSeconds': 3600, 'routineId': None, 'routineName': None, 'notes': '',
            'exercises': [{'id': 'sex-' + sid, 'exerciseId': ex_id, 'exerciseName': 'Mouvement fabriqué', 'category': 'Pectoraux',
                           'restSeconds': 90, 'sets': [{'reps': 5, 'weightKg': 60, 'done': True}]}]}
def live_session(sid, day=15, month=10):
    s = done_session(sid, day, month); s['status'] = 'in_progress'; s['completedAt'] = None; s['durationSeconds'] = None
    s['exercises'][0]['sets'][0]['done'] = False
    return s
def routine(rid, name, ex_id='ex-fab-1'):
    return {'id': rid, 'name': name, 'weekdays': [], 'updatedAt': '2026-09-01T00:00:00.000Z',
            'exercises': [{'exerciseId': ex_id, 'restSeconds': 90, 'sets': [{'reps': 5, 'weightKg': 60}]}]}
def dataset(tag='a', n=3, first_day=1, month=9):
    """état fabriqué complet : un exercice, une routine, n séances terminées."""
    return {'exercises': [ex('ex-fab-1', 'Mouvement fabriqué ' + tag)],
            'routines': [routine('r-fab-' + tag, 'Routine fabriquée ' + tag)],
            'sessions': [done_session('s-%s-%d' % (tag, i), first_day + i, month) for i in range(n)],
            'settings': {'unit': 'kg', 'restTimerSeconds': 90, 'lastExportAt': None}, 'forceCycles': {}, 'meta': {'schemaVersion': 2}}
def summary_of(data):
    sess = data.get('sessions') if isinstance(data.get('sessions'), list) else []
    done_ = [s for s in sess if isinstance(s, dict) and s.get('status') == 'completed']
    return {'sessionsCompleted': len(done_), 'sessionsTotal': len(sess),
            'inProgressIds': [s.get('id') for s in sess if isinstance(s, dict) and s.get('status') == 'in_progress'],
            'lastSessionAt': max((s.get('completedAt') or s.get('date')) for s in done_) if done_ else None,
            'routines': len(data['routines']) if isinstance(data.get('routines'), list) else 0,
            'exercises': len(data['exercises']) if isinstance(data.get('exercises'), list) else 0,
            'cycles': len(data['forceCycles']) if isinstance(data.get('forceCycles'), dict) else 0,
            'schemaVersion': (data.get('meta') or {}).get('schemaVersion') if isinstance(data.get('meta'), dict) else None}
def envelope(data, exported='2026-10-01T08:30:00.000Z'):
    """enveloppe d'export version 1, empreinte calculée ici sur les données telles quelles."""
    summ = summary_of(data); summ['checksum'] = fnv(js_stringify(data))
    return {'app': 'Ovryk', 'exportedAt': exported, 'version': 1, 'data': data, 'summary': summ}
def raw_of(d): return {'ovryk.' + k: json.dumps(v) for k, v in d.items()}

# ---------- navigateur ----------
def new_context(b):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', accept_downloads=True)
    net = []
    def guard(route):
        u = route.request.url
        if u.startswith('http://127.0.0.1') or u.startswith('blob:') or u.startswith('data:'): route.continue_()
        elif u.startswith('https://fonts.googleapis.com/') or u.startswith('https://fonts.gstatic.com/'): route.abort()   # polices de l'app, coupées sans être comptées
        else: net.append(u); route.abort()
    ctx.route('**/*', guard)
    return ctx, net
def fresh(b, d, clock=False, init_script=None):
    """contexte neuf : état d fabriqué, deux démarrages (la migration existante complète le catalogue au premier)."""
    ctx, net = new_context(b)
    if init_script: ctx.add_init_script(init_script)
    page = ctx.new_page(); errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
    if clock: page.clock.install()
    page.goto(URL); page.evaluate("() => localStorage.clear()")
    if d is not None:
        for k, v in d.items(): jset(page, 'ovryk.' + k, v)
    page.reload(); page.wait_for_timeout(300); page.reload(); page.wait_for_timeout(300)
    page.net = net
    return ctx, page, errors
def ls(page): return page.evaluate("() => { const o = {}; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); o[k] = localStorage.getItem(k); } return o; }")
def data(page): return {k: v for k, v in ls(page).items() if k in DATA_KEYS}
def jget(page, key):
    v = page.evaluate("(k) => localStorage.getItem(k)", key); return json.loads(v) if v is not None else None
def jset(page, key, value): page.evaluate("([k, v]) => localStorage.setItem(k, v)", [key, json.dumps(value)])
def rawset(page, key, value): page.evaluate("([k, v]) => localStorage.setItem(k, v)", [key, value])
def settings(page):
    page.click('.nav-btn[data-target="dashboard"]'); page.wait_for_timeout(150); page.click('#dash-settings-btn'); page.wait_for_timeout(400)
def home(page): page.click('.nav-btn[data-target="dashboard"]'); page.wait_for_timeout(300)
def io(page): return page.inner_text('#dashboard-io-status')
def restore_open(page): return page.is_visible('#restore-page')
def import_file(page, path, wait=500):
    page.set_input_files('#dashboard-import-input', str(path)); page.wait_for_timeout(wait)
def write_file(folder, name, content):
    p = folder / name
    if isinstance(content, bytes): p.write_bytes(content)
    else: p.write_text(content if isinstance(content, str) else json.dumps(content), encoding='utf-8')
    return p
def confirm_restore(page, wait=1500):
    """bouton de l'écran, puis deuxième confirmation."""
    page.click('#restore-confirm-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(wait)
def wait_reload(page, wait=600):
    try: page.wait_for_load_state('load', timeout=5000)
    except Exception: pass
    page.wait_for_timeout(wait)

# ---------- IndexedDB (même base, même magasin que l'app) ----------
def dbs(page): return page.evaluate("() => indexedDB.databases().then(l => l.map(d => d.name).sort())")
def put_points(page, points):
    return page.evaluate("""(points) => new Promise((ok, ko) => {
      const req = indexedDB.open('ovryk-restore', 1);
      req.onupgradeneeded = (e) => e.target.result.createObjectStore('points', { keyPath: 'id', autoIncrement: true });
      req.onsuccess = () => { const db = req.result; const tx = db.transaction('points', 'readwrite'); const ids = [];
        points.forEach(p => { const r = tx.objectStore('points').add(p); r.onsuccess = () => ids.push(r.result); });
        tx.oncomplete = () => { db.close(); ok(ids); }; tx.onerror = () => ko(String(tx.error)); };
      req.onerror = () => ko(String(req.error)); })""", points)
def get_points(page):
    """toutes les copies (id, reason, savedAt, raw), ou [] si la base n'existe pas. Ne crée jamais la base."""
    return page.evaluate("""() => indexedDB.databases().then(l => l.some(d => d.name === 'ovryk-restore') ? new Promise(ok => {
      const req = indexedDB.open('ovryk-restore'); req.onsuccess = () => { const db = req.result;
        if (!db.objectStoreNames.contains('points')) { db.close(); ok([]); return; }
        const r = db.transaction('points', 'readonly').objectStore('points').getAll(); r.onsuccess = () => { db.close(); ok(r.result); }; }; }) : [])""")
def count_points(page): return len(get_points(page))
def point(raw, saved, reason='avant restauration'):
    return {'savedAt': saved, 'reason': reason, 'summary': {'sessionsCompleted': 0}, 'raw': raw}

def app_export(page, folder, name='export-app.json'):
    """export produit par l'app elle-même (bouton Exporter de Réglages), relu en JSON."""
    settings(page)
    with page.expect_download(timeout=5000) as dl: page.click('#dashboard-export-btn')
    p = folder / name; dl.value.save_as(str(p))
    return json.loads(p.read_text(encoding='utf-8'))
def control_fixtures(b, folder):
    """contrôle préalable : l'empreinte calculée par ces tests est celle de l'app, sur un export
    produit par l'app à partir de données fabriquées ici. Arrêt de la suite si elles divergent."""
    d = dataset('ctl', 2); d['exercises'][0]['name'] = 'Développé fabriqué « contrôle » éàç'
    ctx, page, errors = fresh(b, d)
    env = app_export(page, folder, 'controle-empreinte.json')
    ok = env['summary']['checksum'] == fnv(js_stringify(env['data'])) and not errors
    check(ok, 'F0 contrôle : empreinte calculée par le test = empreinte de l\'app sur un export fabriqué (%s)' % env['summary']['checksum'])
    ctx.close()
    if not ok:
        print('Arrêt : l\'empreinte des tests diverge de celle de l\'app, les fichiers fabriqués ne seraient pas fiables.'); done()
    return env
