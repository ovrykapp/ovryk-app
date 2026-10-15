"""Nettoyage du lot 16, livraison 2 : export de fin de séance après l'avancée
des cycles, copie supprimée après un échec de pose de la marque, copies
IndexedDB validées avant d'être proposées ou remises.
Données FABRIQUÉES ici : aucun vrai export, aucun appel réseau.
Usage : python3 test_cleanup.py <dossier de travail>, site servi sur http://127.0.0.1:8765."""
import sys, json, re, time
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright
SP = Path(sys.argv[1]); URL = 'http://127.0.0.1:8765/index.html'
F = SP / 'files'; F.mkdir(parents=True, exist_ok=True)
res = []
def check(c, m): res.append(bool(c)); print(('ok     ' if c else 'ECHEC  ') + m)
DATA_KEYS = ['ovryk.exercises', 'ovryk.routines', 'ovryk.sessions', 'ovryk.settings', 'ovryk.forceCycles', 'ovryk.meta']

# ---------- fixtures fabriquées ----------
def done_session(sid, day, ex='ex-fab-1'):
    return {'id': sid, 'status': 'completed', 'date': '2026-09-%02dT10:00:00.000Z' % day, 'completedAt': '2026-09-%02dT11:00:00.000Z' % day,
            'startedAt': '2026-09-%02dT10:00:00.000Z' % day, 'routineId': None,
            'exercises': [{'id': 'sex-%s' % sid, 'exerciseId': ex, 'exerciseName': 'Mouvement fabrique', 'category': 'Pectoraux',
                           'restSeconds': 90, 'sets': [{'reps': 5, 'weight': 60, 'done': True}]}]}
def dataset(n):
    return {'exercises': [{'id': 'ex-fab-1', 'name': 'Mouvement fabrique', 'category': 'Pectoraux', 'equipment': 'Barre', 'unit': 'kg', 'isCustom': True}],
            'routines': [], 'sessions': [done_session('s-%d' % i, 1 + i) for i in range(n)],
            'settings': {'unit': 'kg', 'restTimerSeconds': 90, 'lastExportAt': None}, 'forceCycles': {}, 'meta': {'schemaVersion': 2}}
def raw_of(d):
    return {'ovryk.' + k: json.dumps(v) for k, v in d.items()}
CYCLE = {'cycle_actif': '1', 'semaine_actuelle': 1, 'one_rm_actuel': 100, 'historique_1rm': [], 'historique_cycles': [], 'prochain_cycle': None,
         'en_attente_de_validation': False, 'semaines_modifiees': {}, 'test_report_used': False, 'decalage_semaines': 0}

def ls(page): return page.evaluate("() => { const o = {}; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); o[k] = localStorage.getItem(k); } return o; }")
def data(page): return {k: v for k, v in ls(page).items() if k in DATA_KEYS}
def jset(page, key, value): page.evaluate("([k, v]) => localStorage.setItem(k, v)", [key, json.dumps(value)])
def fresh(b, d):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', accept_downloads=True)
    page = ctx.new_page(); errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(URL); page.evaluate("() => localStorage.clear()")
    for k, v in d.items(): jset(page, 'ovryk.' + k, v)
    page.reload(); page.wait_for_timeout(300); page.reload(); page.wait_for_timeout(300)
    return ctx, page, errors
def settings(page):
    page.click('.nav-btn[data-target="dashboard"]'); page.wait_for_timeout(150); page.click('#dash-settings-btn'); page.wait_for_timeout(500)
def home(page):
    page.click('.nav-btn[data-target="dashboard"]'); page.wait_for_timeout(300)
def io(page): return page.inner_text('#dashboard-io-status')
# copies de restauration fabriquées, écrites directement dans IndexedDB (même base, même magasin que l'app)
def put_points(page, points):
    return page.evaluate("""(points) => new Promise((ok, ko) => {
      const req = indexedDB.open('ovryk-restore', 1);
      req.onupgradeneeded = (e) => e.target.result.createObjectStore('points', { keyPath: 'id', autoIncrement: true });
      req.onsuccess = () => { const db = req.result; const tx = db.transaction('points', 'readwrite'); const ids = [];
        points.forEach(p => { const r = tx.objectStore('points').add(p); r.onsuccess = () => ids.push(r.result); });
        tx.oncomplete = () => { db.close(); ok(ids); }; tx.onerror = () => ko(String(tx.error)); };
      req.onerror = () => ko(String(req.error)); })""", points)
def count_points(page):
    return page.evaluate("""() => indexedDB.databases().then(l => l.some(d => d.name === 'ovryk-restore') ? new Promise(ok => {
      const req = indexedDB.open('ovryk-restore'); req.onsuccess = () => { const db = req.result;
        if (!db.objectStoreNames.contains('points')) { db.close(); ok(0); return; }
        const c = db.transaction('points', 'readonly').objectStore('points').count(); c.onsuccess = () => { db.close(); ok(c.result); }; }; }) : 0)""")
def point(raw, saved, reason='avant restauration'):
    return {'savedAt': saved, 'reason': reason, 'summary': {'sessionsCompleted': 0}, 'raw': raw}

with sync_playwright() as p:
    b = p.chromium.launch()

    # C1 : le fichier de fin de séance contient la semaine de cycle avancée par cette séance ; ordre de fin de séance inchangé
    d = dataset(2)
    d['exercises'].append({'id': 'ex-fab-cyc', 'name': 'Squat fabrique', 'category': 'Lifting', 'liftBaseMode': 'force', 'equipment': 'Barre', 'unit': 'kg', 'isCustom': True})
    d['forceCycles'] = {'ex-fab-cyc': dict(CYCLE)}
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    live = done_session('s-live', 1, ex='ex-fab-cyc'); live.update({'status': 'in_progress', 'date': now, 'startedAt': now}); live.pop('completedAt')
    live['exercises'][0].update({'exerciseName': 'Squat fabrique', 'category': 'Lifting'})
    d['sessions'].append(live)
    ctx, page, errors = fresh(b, d)
    page.click('.nav-btn[data-target="seance"]'); page.wait_for_timeout(300)
    page.click('#seance-finish-btn'); page.wait_for_timeout(200)
    with page.expect_download() as dl: page.click('#confirm-modal-confirm')
    page.wait_for_timeout(500)
    path = F / 'fab-fin-de-seance.json'; dl.value.save_as(str(path)); exported = json.loads(path.read_text())
    week_local = json.loads(ls(page)['ovryk.forceCycles'])['ex-fab-cyc']['semaine_actuelle']
    week_file = exported['data']['forceCycles']['ex-fab-cyc']['semaine_actuelle']
    statuses = {s['id']: s['status'] for s in json.loads(ls(page)['ovryk.sessions'])}
    check(week_local == 2 and week_file == 2, 'C1 cycle avancé (semaine %s) et fichier exporté à la même semaine (%s)' % (week_local, week_file))
    file_status = {s['id']: s['status'] for s in exported['data']['sessions']}
    check(statuses.get('s-live') == 'completed' and file_status.get('s-live') == 'completed' and exported['data']['forceCycles'] == json.loads(ls(page)['ovryk.forceCycles']),
          'C1 séance terminée dans le téléphone et dans le fichier, cycles du fichier identiques au téléphone')
    check(page.is_visible('#seance-start-empty-btn') and json.loads(ls(page)['ovryk.settings']).get('lastExportAt') and not errors,
          'C1 écran de départ affiché, lastExportAt noté, aucune erreur (%s)' % errors[:1])
    ctx.close()

    # C2 : échec de la pose de la marque (stockage plein simulé) : rien remplacé, aucune copie laissée
    base = dataset(3)
    ctx, page, errors = fresh(b, base)
    other = dataset(1); other['exercises'][0]['name'] = 'Autre mouvement fabrique'
    imp = F / 'fab-import.json'; imp.write_text(json.dumps({'app': 'Ovryk', 'exportedAt': '2026-10-01T08:30:00.000Z', 'version': 1, 'data': other}))
    settings(page); before = data(page); n0 = count_points(page)
    page.evaluate("""() => { const orig = Storage.prototype.setItem;
      Storage.prototype.setItem = function (k, v) { if (k === 'ovryk.restoreInProgress') throw new Error('QuotaExceededError simulé'); return orig.call(this, k, v); }; }""")
    page.set_input_files('#dashboard-import-input', str(imp)); page.wait_for_timeout(500)
    page.click('#restore-confirm-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(1500)
    body = page.inner_text('#restore-page') if page.is_visible('#restore-page') else io(page)
    check('stockage plein' in body and data(page) == before and ls(page).get('ovryk.restoreInProgress') is None, 'C2 échec de la marque : "stockage plein", données identiques, aucune marque')
    check(count_points(page) == n0, 'C2 aucune copie laissée dans IndexedDB (%s avant, %s après)' % (n0, count_points(page)))
    ctx.close()

    # C3 : copie abîmée (séances illisibles) seule : jamais proposée, rien écrit à l'ouverture de Réglages
    ctx, page, errors = fresh(b, base)
    broken = raw_of(dataset(1)); broken['ovryk.sessions'] = '{abîmé'
    put_points(page, [point(broken, '2026-10-12T10:00:00.000Z')])
    before = data(page); settings(page)
    check(not page.is_visible('#restore-undo-btn') and data(page) == before and not errors, 'C3 copie illisible seule : ligne d\'annulation masquée, rien écrit')
    ctx.close()

    # C4 : copie qui ferait planter le démarrage (séance sans liste d'exercices) plus récente qu'une copie valide : la valide est proposée
    ctx, page, errors = fresh(b, base)
    crash = dataset(2); crash['sessions'][0].pop('exercises')
    valid = dataset(1)
    put_points(page, [point(raw_of(valid), '2026-10-11T10:00:00.000Z'), point(raw_of(crash), '2026-10-12T10:00:00.000Z')])
    settings(page)
    vis = page.is_visible('#restore-undo-btn')
    if vis: page.click('#restore-undo-btn'); page.wait_for_timeout(500)
    sub = page.inner_text('#restore-page') if page.is_visible('#restore-page') else ''
    check(vis and '11 octobre' in sub and '12 octobre' not in sub, 'C4 copie qui ferait planter ignorée, copie valide plus ancienne proposée (%s)' % ' '.join(sub.split())[:90])
    ctx.close()

    # C5 : bandeau de restauration interrompue pointant vers une copie abîmée : traitée comme introuvable, rien écrit
    ctx, page, errors = fresh(b, base)
    ids = put_points(page, [point(broken, '2026-10-12T10:00:00.000Z')])
    jset(page, 'ovryk.restoreInProgress', {'pointId': ids[0], 'startedAt': '2026-10-12T10:00:00.000Z', 'mode': 'file'})
    page.reload(); page.wait_for_timeout(400); home(page); before = data(page)
    page.click('#restore-interrupted-back-btn')
    page.wait_for_timeout(500)
    msgv = page.is_visible('#restore-interrupted-msg')
    check(msgv and 'introuvable ou abîmée' in page.inner_text('#restore-interrupted-msg') and not page.is_visible('#restore-page') and data(page) == before,
          'C5 bandeau, copie abîmée : message "introuvable ou abîmée", aucun écran, rien écrit')
    ctx.close()

    # C6 : annulation vers un état vide toujours possible (copie d'un téléphone vide : toutes les clés absentes)
    ctx, page, errors = fresh(b, base)
    put_points(page, [point({k: None for k in DATA_KEYS}, '2026-10-12T10:00:00.000Z')])
    settings(page)
    vis = page.is_visible('#restore-undo-btn')
    if vis: page.click('#restore-undo-btn'); page.wait_for_timeout(500)
    check(vis and page.is_visible('#restore-page') and not errors, 'C6 copie d\'un état vide : proposée et écran d\'annulation ouvert')
    ctx.close()

    # C7 : exception dans l'export de fin de séance : la séance reste enregistrée, le cycle avance une seule fois,
    # l'écran de départ s'affiche, activeSession est remis à null, l'envoi automatique part, un second Terminer est impossible
    def live_cycle_dataset():
        d = dataset(2)
        d['exercises'].append({'id': 'ex-fab-cyc', 'name': 'Squat fabrique', 'category': 'Lifting', 'liftBaseMode': 'force', 'equipment': 'Barre', 'unit': 'kg', 'isCustom': True})
        d['forceCycles'] = {'ex-fab-cyc': dict(CYCLE)}
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        lv = done_session('s-live', 1, ex='ex-fab-cyc'); lv.update({'status': 'in_progress', 'date': now, 'startedAt': now}); lv.pop('completedAt')
        d['sessions'].append(lv)
        return d
    ctx, page, errors = fresh(b, live_cycle_dataset())
    jset(page, 'ovryk.cloud.prefs', {'autoUpload': True})
    jset(page, 'ovryk.cloud.auth', {'access_token': 'acc-0', 'refresh_token': 'ref-0', 'expires_at': int(time.time()) + 3600, 'user': {'id': 'u-1', 'email': 'un@exemple.test'}, 'savedAt': '2026-10-14T10:00:00.000Z'})
    page.reload(); page.wait_for_timeout(300)
    calls = []
    page.route(re.compile(r'https://[^/]*\.supabase\.co/.*'), lambda route, request: (calls.append(request.method + ' ' + request.url.split('.supabase.co')[1][:30]), route.fulfill(status=500, body='{}', headers={'content-type': 'application/json'})))
    page.evaluate("() => { URL.createObjectURL = () => { throw new Error('export impossible (simulé)'); }; }")
    page.click('.nav-btn[data-target="seance"]'); page.wait_for_timeout(300)
    page.click('#seance-finish-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(1200)
    week = lambda: json.loads(ls(page)['ovryk.forceCycles'])['ex-fab-cyc']['semaine_actuelle']
    st = {x['id']: x['status'] for x in json.loads(ls(page)['ovryk.sessions'])}
    check(st.get('s-live') == 'completed' and week() == 2, 'C7 export en exception : séance enregistrée (%s), cycle avancé une fois (semaine %s)' % (st.get('s-live'), week()))
    check(page.is_visible('#seance-start-empty-btn') and not page.is_visible('#seance-finish-btn'), 'C7 écran de départ affiché, bouton Terminer absent')
    check(any(c.startswith('POST /rest/v1/backups') for c in calls), 'C7 envoi automatique lancé (%s)' % calls[:2])
    page.evaluate("() => document.getElementById('seance-finish-btn').click()"); page.wait_for_timeout(300)
    page.evaluate("() => { const b = document.getElementById('confirm-modal-confirm'); if (b && b.offsetParent) b.click(); }"); page.wait_for_timeout(500)
    check(week() == 2 and not page.is_visible('#confirm-modal-confirm'), 'C7 second Terminer (même forcé) : cycle toujours en semaine %s, aucune confirmation' % week())
    ctx.close()

    # C8 : option active puis déconnexion : aucune ligne "pas encore en ligne" sur l'Accueil
    ctx, page, errors = fresh(b, dataset(3))
    jset(page, 'ovryk.cloud.prefs', {'autoUpload': True})
    jset(page, 'ovryk.cloud.lastUpload', {'at': '2026-10-14T10:00:00.000Z', 'id': 'x', 'fingerprint': '00000000', 'sessionsCompleted': 2, 'userId': 'u-1'})
    page.reload(); page.wait_for_timeout(300); home(page)
    check(not page.is_visible('#cloud-home-line') and json.loads(ls(page)['ovryk.cloud.prefs']) == {'autoUpload': True}, 'C8 option active, déconnecté, 1 séance non envoyée : aucune ligne, prefs intactes')
    ctx.close()

    b.close()

print('\n%d/%d' % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
