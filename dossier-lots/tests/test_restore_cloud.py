"""Lot 16, livraison 4 : restauration depuis la sauvegarde en ligne.
Supabase simulé (routes Playwright), données FABRIQUÉES ici : aucun vrai
export, aucune vraie clé de session, aucun appel réseau réel."""
import sys, json, time, re, copy
from pathlib import Path
from playwright.sync_api import sync_playwright
SP = Path(sys.argv[1]); URL = 'http://127.0.0.1:8765/index.html'
HOST = 'https://hroxwrcxvhpvlpmxeixw.supabase.co'
PUB = 'sb_publishable_06uyz-13yFi8DjmFc_6nuA_ZJiWcEch'
F = SP / 'files'; F.mkdir(exist_ok=True)
res = []
def check(c, m): res.append(bool(c)); print(('ok     ' if c else 'ECHEC  ') + m)
DATA_KEYS = ['ovryk.exercises', 'ovryk.routines', 'ovryk.sessions', 'ovryk.settings', 'ovryk.forceCycles', 'ovryk.meta']

# ---------- fixtures fabriquées ----------
def js_stringify(v): return json.dumps(v, separators=(',', ':'), ensure_ascii=False)
def fnv(s):
    h = 0x811c9dc5
    for ch in s.encode('utf-16-le').decode('utf-16-le'):
        for unit in ([ord(ch)] if ord(ch) < 0x10000 else [0xD800 + ((ord(ch) - 0x10000) >> 10), 0xDC00 + ((ord(ch) - 0x10000) & 0x3FF)]):
            h ^= unit
            h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) & 0xFFFFFFFF
    return '%08x' % h
def session(sid, day, ex='ex-fab-1'):
    return {'id': sid, 'status': 'completed', 'date': '2026-09-%02dT10:00:00.000Z' % day, 'completedAt': '2026-09-%02dT11:00:00.000Z' % day,
            'routineId': None, 'exercises': [{'exerciseId': ex, 'name': 'Mouvement fabrique', 'sets': [{'reps': 5, 'weight': 60, 'done': True}]}]}
def dataset(tag, n_sessions, first_day):
    return {'exercises': [{'id': 'ex-fab-1', 'name': 'Mouvement fabrique ' + tag, 'category': 'muscu'}],
            'routines': [],
            'sessions': [session('s-%s-%d' % (tag, i), first_day + i) for i in range(n_sessions)],
            'settings': {'unit': 'kg', 'restTimerSeconds': 90, 'lastExportAt': None},
            'forceCycles': {}, 'meta': {'schemaVersion': 2}}
def envelope(data):
    done = [s for s in data['sessions'] if s.get('status') == 'completed']
    summ = {'sessionsCompleted': len(done), 'sessionsTotal': len(data['sessions']), 'inProgressIds': [],
            'lastSessionAt': max(s['completedAt'] for s in done) if done else None, 'routines': len(data['routines']),
            'exercises': len(data['exercises']), 'cycles': len(data['forceCycles']), 'schemaVersion': data['meta'].get('schemaVersion')}
    summ['checksum'] = fnv(js_stringify(data))
    return {'app': 'Ovryk', 'exportedAt': '2026-10-01T08:30:00.000Z', 'version': 1, 'data': data, 'summary': summ}

LOCAL = dataset('a', 3, 1)       # "téléphone" : 3 séances
INCOMING = dataset('b', 2, 10)   # sauvegarde en ligne : 2 autres séances
ENV = envelope(INCOMING)
ID1 = '11111111-1111-4111-8111-111111111111'; ID2 = '22222222-2222-4222-8222-222222222222'; ID3 = '33333333-3333-4333-8333-333333333333'
LIST_PATH = '/rest/v1/backups?select=id,created_at,sessions_count,fingerprint,last_session:summary-%3E%3ElastSessionAt&order=created_at.desc&limit=40'
LIST = 'GET ' + LIST_PATH
def dl_key(i): return 'GET /rest/v1/backups?id=eq.%s&select=payload,fingerprint,sessions_count' % i
def row(i, env, created='2026-10-12T09:15:00+00:00', fp=None, sc=None):
    return {'id': i, 'created_at': created, 'sessions_count': env['summary']['sessionsCompleted'] if sc is None else sc,
            'fingerprint': fp or env['summary']['checksum'], 'last_session': env['summary']['lastSessionAt']}
def dl_body(env, fp=None, sc=None, payload=None):
    return [{'payload': js_stringify(env) if payload is None else payload, 'fingerprint': fp or env['summary']['checksum'],
             'sessions_count': env['summary']['sessionsCompleted'] if sc is None else sc}]
BIG = envelope(dataset('c', 5, 1))   # plus complète, plus ancienne
STD_LIST = [row(ID1, ENV), row(ID2, BIG, created='2026-10-05T09:15:00+00:00')]

class Fake:
    def __init__(self, page, plan):
        self.plan = plan; self.calls = []; self.page = page
        self.pattern = re.compile(r'https://[^/]*\.supabase\.co/.*')
        page.route(self.pattern, self.handle)
    def stop(self): self.page.unroute(self.pattern)
    def handle(self, route, request):
        path = request.url.replace(HOST, '')
        key = request.method + ' ' + path
        self.calls.append({'key': key, 'headers': request.headers})
        seq = self.plan.get(key)
        if not seq: route.fulfill(status=599, body='inattendu'); return
        st, body = seq.pop(0) if len(seq) > 1 else seq[0]
        if st == 'hang': return
        if st == 'abort': route.abort(); return
        route.fulfill(status=st, body=body if isinstance(body, str) else json.dumps(body), headers={'content-type': 'application/json'})

def ls(page): return page.evaluate("() => { const o = {}; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); o[k] = localStorage.getItem(k); } return o; }")
def data(page): return {k: v for k, v in ls(page).items() if k in DATA_KEYS}
def dbs(page): return page.evaluate("() => indexedDB.databases().then(l => l.map(d => d.name))")
def fresh(b, local=LOCAL, clock=False):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', accept_downloads=True)
    page = ctx.new_page(); errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
    if clock: page.clock.install()
    page.goto(URL); page.evaluate("() => localStorage.clear()")
    if local is not None:
        for k, v in local.items(): page.evaluate("([k, v]) => localStorage.setItem('ovryk.' + k, v)", [k, json.dumps(v)])
    page.reload(); page.wait_for_timeout(300)
    return ctx, page, errors
def put_session(page, user='u-1', email='un@exemple.test', access='acc-0', refresh='ref-0', exp_in=3600):
    page.evaluate("(s) => localStorage.setItem('ovryk.cloud.auth', JSON.stringify(s))", {'access_token': access, 'refresh_token': refresh, 'expires_at': int(time.time()) + exp_in, 'user': {'id': user, 'email': email}, 'savedAt': '2026-10-14T10:00:00.000Z'})
def settings(page):
    page.click('.nav-btn[data-target="dashboard"]'); page.wait_for_timeout(150); page.click('#dash-settings-btn'); page.wait_for_timeout(300)
def msg(page): return page.inner_text('#cloud-message') if page.is_visible('#cloud-message') else ''
def items(page): return page.locator('.cloud-backup-item')
def load_list(page, wait=600): page.click('#cloud-list-btn'); page.wait_for_timeout(wait)
def wait_offline_msg(page, timeout=15000):
    """attend, ENCORE HORS LIGNE, que l'échec de la requête soit affiché, au lieu d'une attente fixe : sous charge,
    la requête peut ne pas avoir échoué au bout de 600 ou 800 ms ; remise en ligne trop tôt, elle partait alors
    vers le vrai service (la route simulée est retirée), et le contrôle lisait encore "Chargement…"."""
    try: page.wait_for_function("() => (document.getElementById('cloud-message') || {}).textContent.indexOf('Pas de connexion internet') !== -1", timeout=timeout)
    except Exception: pass   # le contrôle qui suit échoue alors, avec le message affiché
def restore_open(page): return page.is_visible('#restore-page')
def setup(b, plan, local=LOCAL, clock=False):
    ctx, page, errors = fresh(b, local, clock); put_session(page); page.reload(); page.wait_for_timeout(300)
    fk = Fake(page, plan); settings(page)
    return ctx, page, errors, fk

def untouched_after_failure(b, name, dl_response, expect, extra_plan=None):
    plan = {LIST: [(200, STD_LIST)], dl_key(ID1): [dl_response]}
    if extra_plan: plan.update(extra_plan)
    ctx, page, errors, fk = setup(b, plan)
    load_list(page); before = ls(page); dbs0 = dbs(page)
    items(page).nth(0).click(); page.wait_for_timeout(800)
    m = msg(page)
    check(expect in m and 'Tes données ne sont pas touchées' in m and not restore_open(page) and ls(page) == before and dbs(page) == dbs0 and not errors,
          '%s : refus "%s", aucun écran de restauration, localStorage et IndexedDB identiques' % (name, m[:110]))
    ctx.close()

with sync_playwright() as p:
    b = p.chromium.launch()

    # Contrôle des fixtures : l'empreinte calculée ici est celle de l'app (export de l'app sur les mêmes données)
    ctx, page, errors = fresh(b, INCOMING)
    settings(page)
    with page.expect_download() as dl: page.click('#dashboard-export-btn')
    exp_path = F / 'fab-export.json'; dl.value.save_as(str(exp_path)); app_env = json.loads(exp_path.read_text())
    check(app_env['summary']['checksum'] == fnv(js_stringify(app_env['data'])) and app_env['summary']['sessionsCompleted'] == envelope(app_env['data'])['summary']['sessionsCompleted'], 'F0 fixtures : empreinte calculée par le test = empreinte calculée par l\'app sur les mêmes données (%s)' % app_env['summary']['checksum'])
    ctx.close()

    # R0 : pas de bouton déconnecté, aucun appel au lancement ni à l'ouverture de Réglages
    ctx, page, errors = fresh(b); fk = Fake(page, {}); settings(page)
    check(not page.is_visible('#cloud-list-btn') and not fk.calls, 'R0 déconnecté : pas de bouton de restauration, aucun appel')
    ctx.close()
    ctx, page, errors, fk = setup(b, {LIST: [(200, STD_LIST)]})
    check(page.is_visible('#cloud-list-btn') and not fk.calls and not page.is_visible('#cloud-backup-list'), 'R0 connecté : bouton visible, liste fermée, aucun appel au lancement ni à l\'ouverture')

    # R1 : liste
    before = ls(page)
    load_list(page)
    c = fk.calls
    check(len(c) == 1 and c[0]['key'] == LIST and 'payload' not in c[0]['key'], 'R1 un seul appel, sans payload : %s' % (c[0]['key'][:100] if c else None))
    h = c[0]['headers'] if c else {}
    check(h.get('apikey') == PUB and h.get('authorization') == 'Bearer acc-0', 'R1 en-têtes apikey et Bearer')
    texts = [items(page).nth(i).inner_text() for i in range(items(page).count())]
    check(len(texts) == 2 and 'Envoyée le 12' in texts[0] and '2 séances terminées' in texts[0] and 'dernière le 11' in texts[0] and 'Empreinte ' + ENV['summary']['checksum'] in texts[0],
          'R1 ligne 1 : date d\'envoi, séances, dernière séance, empreinte (%r)' % (texts[0].replace('\n', ' | ') if texts else None))
    check('La plus complète' in texts[1] and 'La plus complète' not in texts[0], 'R1 repère "La plus complète" sur la plus grande, pas ailleurs')
    check(ls(page) == before, 'R1 afficher la liste n\'écrit rien')
    ctx.close()

    # R1b : repères "envoyée depuis cet appareil" et "identique à ce téléphone", lignes invalides ignorées, last_session absente
    ctx, page, errors, fk = setup(b, {})
    stored = {k[6:]: json.loads(v) for k, v in data(page).items()}
    stored = {k: stored[k] for k in ['exercises', 'routines', 'sessions', 'settings', 'forceCycles', 'meta']}
    lst = [row(ID1, ENV), dict(row(ID3, envelope(stored)), last_session=None),
           {'id': 'pas-un-uuid', 'created_at': 'x', 'sessions_count': 1, 'fingerprint': '00000000'},
           {'id': ID2, 'created_at': '2026-10-01T00:00:00+00:00', 'sessions_count': -1, 'fingerprint': 'zz'}]
    fk.plan[LIST] = [(200, lst)]
    page.evaluate("(id) => localStorage.setItem('ovryk.cloud.lastUpload', JSON.stringify({ at: '2026-10-12T09:15:00.000Z', id: id, fingerprint: 'x', sessionsCompleted: 2 }))", ID1)
    load_list(page)
    texts = [items(page).nth(i).inner_text() for i in range(items(page).count())]
    check(len(texts) == 2, 'R1b lignes mal formées ignorées (%d affichées)' % len(texts))
    check(len(texts) == 2 and 'Envoyée depuis cet appareil' in texts[0] and 'Identique à ce téléphone' in texts[1] and 'Identique' not in texts[0] and 'dernière' not in texts[1],
          'R1b repères : envoyée depuis cet appareil, identique à ce téléphone ; pas de "dernière" sans date')
    ctx.close()

    # R2 : liste vide
    ctx, page, errors, fk = setup(b, {LIST: [(200, [])]})
    load_list(page)
    check('Aucune sauvegarde en ligne pour ce compte' in msg(page) and not page.is_visible('#cloud-backup-list'), 'R2 liste vide : message, pas de liste')
    ctx.close()

    # R3 : erreurs de liste
    for name, plan, expect in [
        ('503', {LIST: [(503, '')]}, 'indisponible'),
        ('table absente', {LIST: [(404, {'code': 'PGRST205', 'message': 'x'})]}, 'n’existe pas encore'),
        ('droits', {LIST: [(401, {'code': '42501', 'message': 'permission denied'})], 'POST /auth/v1/token?grant_type=refresh_token': [(200, {'access_token': 'acc-1', 'refresh_token': 'ref-1', 'expires_in': 3600, 'user': {'id': 'u-1', 'email': 'un@exemple.test'}})]}, 'Reconnecte-toi'),
        ('non JSON', {LIST: [(200, 'pas du json')]}, 'indisponible'),
        ('objet au lieu d\'une liste', {LIST: [(200, {'a': 1})]}, 'Réponse inattendue')]:
        ctx, page, errors, fk = setup(b, plan); before = ls(page)
        load_list(page)
        check(expect in msg(page) and not page.is_visible('#cloud-backup-list') and data(page) == data(page) and {k: v for k, v in ls(page).items() if k != 'ovryk.cloud.auth'} == {k: v for k, v in before.items() if k != 'ovryk.cloud.auth'},
              'R3 liste %s : "%s", aucune liste, données intactes' % (name, msg(page)[:90]))
        ctx.close()
    # hors ligne
    ctx, page, errors, fk = setup(b, {}); before = ls(page)
    fk.stop(); ctx.set_offline(True); load_list(page, wait=0); wait_offline_msg(page); ctx.set_offline(False)
    check('Pas de connexion internet' in msg(page) and ls(page) == before, 'R3 liste hors ligne : "%s"' % msg(page)[:80])
    ctx.close()
    # 401 puis renouvellement puis liste
    ctx, page, errors, fk = setup(b, {LIST: [(401, {'code': 'PGRST301', 'message': 'JWT expired'}), (200, STD_LIST)],
                                      'POST /auth/v1/token?grant_type=refresh_token': [(200, {'access_token': 'acc-1', 'refresh_token': 'ref-1', 'expires_in': 3600, 'user': {'id': 'u-1', 'email': 'un@exemple.test'}})]})
    load_list(page)
    keys = [x['key'] for x in fk.calls]
    check(keys == [LIST, 'POST /auth/v1/token?grant_type=refresh_token', LIST] and fk.calls[2]['headers'].get('authorization') == 'Bearer acc-1' and items(page).count() == 2,
          'R3 401 : un renouvellement puis un seul rejeu avec le nouveau jeton, liste affichée')
    ctx.close()
    # renouvellement refusé définitivement : session effacée, liste vidée
    ctx, page, errors, fk = setup(b, {LIST: [(200, STD_LIST), (401, {'code': 'PGRST301'})],
                                      'POST /auth/v1/token?grant_type=refresh_token': [(400, {'error_code': 'refresh_token_already_used'})]})
    load_list(page); n1 = items(page).count(); load_list(page)
    check(n1 == 2 and 'n’est plus valable' in msg(page) and not page.is_visible('#cloud-backup-list') and page.is_visible('#cloud-signin-form'),
          'R3 session révoquée : "%s", liste retirée, formulaire de connexion' % msg(page)[:70])
    ctx.close()

    # R4 : restauration réussie, chemin identique au fichier
    ctx, page, errors, fk = setup(b, {LIST: [(200, STD_LIST)], dl_key(ID1): [(200, dl_body(ENV))]})
    load_list(page); before = ls(page); dbs0 = dbs(page)
    items(page).nth(0).click(); page.wait_for_timeout(800)
    keys = [x['key'] for x in fk.calls]
    check(keys == [LIST, dl_key(ID1)] and fk.calls[1]['headers'].get('authorization') == 'Bearer acc-0', 'R4 téléchargement du seul payload choisi : %s' % [k[:70] for k in keys])
    sub = page.inner_text('#restore-sub') if restore_open(page) else ''
    body = page.inner_text('#restore-body') if restore_open(page) else ''
    check(restore_open(page) and 'Sauvegarde en ligne, exportée le 1' in sub and '3 séances terminées de ce téléphone ne sont pas' in body,
          'R4 écran de comparaison du fichier : "%s", avertissement des séances perdues' % sub)
    check(ls(page) == before and dbs(page) == dbs0, 'R4 rien écrit (localStorage, IndexedDB) avant les confirmations')
    page.click('#restore-confirm-btn'); page.wait_for_timeout(200)
    check(ls(page) == before, 'R4 rien écrit après la première confirmation')
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(1500)
    after = data(page)
    check([x['id'] for x in json.loads(after['ovryk.sessions'])] == [x['id'] for x in INCOMING['sessions']] and json.loads(after['ovryk.exercises'])[0]['name'] == INCOMING['exercises'][0]['name'] and not errors,
          'R4 après confirmation : données de la sauvegarde en ligne en place (%s)' % errors[:1])
    check('ovryk.cloud.auth' in ls(page) and ls(page).get('ovryk.restoreInProgress') is None, 'R4 session gardée, aucune marque de restauration restante')
    settings(page)
    check(page.is_visible('#restore-undo-btn') and 'Annuler la dernière restauration' in page.inner_text('#restore-undo-btn'), 'R4 ligne "Annuler la dernière restauration" présente')
    page.click('#restore-undo-btn'); page.wait_for_timeout(500); page.click('#restore-confirm-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(1500)
    check([x['id'] for x in json.loads(data(page)['ovryk.sessions'])] == [x['id'] for x in LOCAL['sessions']], 'R4 annulation : les séances du téléphone reviennent')
    cloud_after = after
    ctx.close()
    # même enveloppe importée en fichier : mêmes écritures
    ctx, page, errors = fresh(b); settings(page)
    fp = F / 'fab-env.json'; fp.write_text(js_stringify(ENV))
    page.set_input_files('#dashboard-import-input', str(fp)); page.wait_for_timeout(500)
    page.click('#restore-confirm-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(1500)
    fa = data(page)
    def ddiff(a, b, path=''):
        if type(a) != type(b): print('   diff', path, repr(a)[:80], '||', repr(b)[:80]); return
        if isinstance(a, dict):
            for k in set(a) | set(b): ddiff(a.get(k), b.get(k), path + '.' + str(k))
        elif isinstance(a, list):
            if len(a) != len(b): print('   diff len', path, len(a), len(b)); return
            for i, (x, y) in enumerate(zip(a, b)): ddiff(x, y, path + '[%d]' % i)
        elif a != b: print('   diff', path, repr(a)[:80], '||', repr(b)[:80])
    def norm(d):
        # seule différence admise : createdAt des exercices du catalogue ajoutés par l'app au rechargement (heure du rechargement)
        out = {k: json.loads(v) for k, v in d.items()}
        for e in out.get('ovryk.exercises', []):
            if e.get('id') not in ('ex-fab-1',): e.pop('createdAt', None)
        return out
    for k in DATA_KEYS: ddiff(norm(fa).get(k), norm(cloud_after).get(k), k)
    check(norm(fa) == norm(cloud_after), 'R4 écritures identiques à l\'import du même contenu en fichier (six clés, hors heure d\'ajout du catalogue au rechargement)')
    ctx.close()

    # R5 : téléchargement refusé, rien touché
    untouched_after_failure(b, 'R5 ligne disparue', (200, []), 'n’existe plus en ligne')
    untouched_after_failure(b, 'R5 empreinte de la ligne différente', (200, dl_body(ENV, fp='0badf00d')), 'empreinte différente')
    untouched_after_failure(b, 'R5 séances de la ligne différentes', (200, dl_body(ENV, sc=7)), 'nombre de séances différent')
    untouched_after_failure(b, 'R5 payload vide', (200, dl_body(ENV, payload='  ')), 'illisible')
    untouched_after_failure(b, 'R5 payload non JSON', (200, dl_body(ENV, payload=js_stringify(ENV)[:-40])), 'illisible')
    no_sum = copy.deepcopy(ENV); del no_sum['summary']['checksum']
    untouched_after_failure(b, 'R5 empreinte absente du payload', (200, dl_body(ENV, payload=js_stringify(no_sum))), 'empreinte différente')
    other = copy.deepcopy(ENV); other['summary']['checksum'] = 'abcdef12'
    untouched_after_failure(b, 'R5 empreinte du payload différente de la ligne', (200, dl_body(ENV, payload=js_stringify(other))), 'empreinte différente')
    modified = copy.deepcopy(ENV); modified['data']['exercises'][0]['name'] = 'modifie'
    untouched_after_failure(b, 'R5 données modifiées (empreinte recalculée par validateBackupFile)', (200, dl_body(ENV, payload=js_stringify(modified))), 'Restauration refusée (sauvegarde en ligne contrôlée comme un fichier d’export) : fichier abîmé ou modifié')
    fewer = copy.deepcopy(ENV); fewer['data']['sessions'] = fewer['data']['sessions'][:1]
    untouched_after_failure(b, 'R5 séances du payload différentes (empreinte de la ligne recopiée)', (200, dl_body(ENV, payload=js_stringify(fewer))), 'nombre de séances différent')
    newer_data = copy.deepcopy(INCOMING); newer_data['meta']['schemaVersion'] = 9; newer = envelope(newer_data)
    ctx, page, errors, fk = setup(b, {LIST: [(200, [row(ID1, newer)])], dl_key(ID1): [(200, dl_body(newer))]})
    load_list(page); before = ls(page); items(page).nth(0).click(); page.wait_for_timeout(800)
    check('Restauration refusée (sauvegarde en ligne contrôlée comme un fichier d’export) : sauvegarde faite par une version plus récente' in msg(page) and not restore_open(page) and ls(page) == before,
          'R5 schéma plus récent (empreinte valide) : refus de validateBackupFile, message "fichier" inchangé')
    ctx.close()
    untouched_after_failure(b, 'R5 téléchargement 503', (503, ''), 'indisponible')
    ctx, page, errors, fk = setup(b, {LIST: [(200, STD_LIST)], dl_key(ID1): [(200, dl_body(ENV))]})
    load_list(page); before = ls(page); fk.stop(); ctx.set_offline(True); items(page).nth(0).click(); wait_offline_msg(page); ctx.set_offline(False)
    check('Pas de connexion internet' in msg(page) and not restore_open(page) and ls(page) == before, 'R5 téléchargement hors ligne : "%s"' % msg(page)[:70])
    ctx.close()

    # R5b : délai de 60 s sur le téléchargement (horloge simulée)
    ctx, page, errors, fk = setup(b, {LIST: [(200, STD_LIST)], dl_key(ID1): [('hang', None)]}, clock=True)
    load_list(page); page.clock.run_for(1000); page.wait_for_timeout(300); before = ls(page)
    items(page).nth(0).click(); page.wait_for_timeout(300)
    page.clock.run_for(30000); page.wait_for_timeout(200); still = page.locator('#cloud-list-btn').is_disabled()
    page.clock.run_for(31000); page.wait_for_timeout(400)
    check(still and 'n’a pas répondu à temps' in msg(page) and not page.locator('#cloud-list-btn').is_disabled() and ls(page) == before,
          'R5b toujours en attente à 30 s, abandon à 60 s, boutons rendus, rien écrit : "%s"' % msg(page)[:70])
    ctx.close()

    # R5c : 401 au téléchargement, renouvellement puis un seul rejeu
    ctx, page, errors, fk = setup(b, {LIST: [(200, STD_LIST)], dl_key(ID1): [(401, {'code': 'PGRST301'}), (200, dl_body(ENV))],
                                      'POST /auth/v1/token?grant_type=refresh_token': [(200, {'access_token': 'acc-1', 'refresh_token': 'ref-1', 'expires_in': 3600, 'user': {'id': 'u-1', 'email': 'un@exemple.test'}})]})
    load_list(page); items(page).nth(0).click(); page.wait_for_timeout(1000)
    keys = [x['key'] for x in fk.calls]
    check(keys == [LIST, dl_key(ID1), 'POST /auth/v1/token?grant_type=refresh_token', dl_key(ID1)] and restore_open(page), 'R5c 401 au téléchargement : renouvellement, un seul rejeu, écran ouvert')
    ctx.close()

    # R6 : double appui, un seul téléchargement ; boutons désactivés pendant l'appel
    ctx, page, errors, fk = setup(b, {LIST: [(200, STD_LIST)], dl_key(ID1): [('hang', None)]})
    load_list(page); items(page).nth(0).click(); page.wait_for_timeout(100)
    dis = items(page).nth(1).is_disabled() and page.locator('#cloud-upload-btn').is_disabled()
    items(page).nth(0).click(force=True); items(page).nth(1).click(force=True); page.wait_for_timeout(300)
    check(dis and [x['key'] for x in fk.calls].count(dl_key(ID1)) == 1 and dl_key(ID2) not in [x['key'] for x in fk.calls], 'R6 pendant un téléchargement : lignes et boutons désactivés, un seul appel')
    ctx.close()

    # R7 : abandon à l'écran puis à la deuxième confirmation
    ctx, page, errors, fk = setup(b, {LIST: [(200, STD_LIST)], dl_key(ID1): [(200, dl_body(ENV))]})
    load_list(page); before = ls(page); dbs0 = dbs(page)
    items(page).nth(0).click(); page.wait_for_timeout(600); page.click('#restore-cancel-btn'); page.wait_for_timeout(200)
    a1 = not restore_open(page) and ls(page) == before
    items(page).nth(0).click(); page.wait_for_timeout(600); page.click('#restore-confirm-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-cancel'); page.wait_for_timeout(300)
    check(a1 and ls(page) == before and dbs(page) == dbs0, 'R7 Annuler à l\'écran puis à la dernière confirmation : rien écrit, aucune copie IndexedDB')
    ctx.close()

    # R8 : déconnexion puis autre compte : jamais la liste du compte précédent
    ctx, page, errors, fk = setup(b, {LIST: [(200, STD_LIST)], 'POST /auth/v1/logout?scope=local': [(204, '')]})
    load_list(page); n1 = items(page).count()
    page.click('#cloud-signout-btn'); page.wait_for_timeout(500)
    gone = items(page).count() == 0
    put_session(page, user='u-2', email='deux@exemple.test', access='acc-b', refresh='ref-b'); page.reload(); page.wait_for_timeout(300); settings(page)
    check(n1 == 2 and gone and items(page).count() == 0 and not page.is_visible('#cloud-backup-list'), 'R8 déconnexion : liste effacée ; autre compte : aucune ligne du compte précédent avant chargement')
    ctx.close()

    # R9 : appli vierge (rien sur le téléphone) : restauration possible, aucun blocage d'export
    ctx, page, errors, fk = setup(b, {LIST: [(200, STD_LIST)], dl_key(ID1): [(200, dl_body(ENV))]}, local=None)
    load_list(page); items(page).nth(0).click(); page.wait_for_timeout(800)
    opened = restore_open(page)
    page.click('#restore-confirm-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(1500)
    check(opened and [x['id'] for x in json.loads(data(page)['ovryk.sessions'])] == [x['id'] for x in INCOMING['sessions']] and not errors, 'R9 appli vierge : restauration en ligne aboutie (getBackupBlocker non utilisé) %s' % errors[:1])
    ctx.close()

    # R10 : un payload de 2 Mo passe (taille maximale d'un envoi)
    big_data = dataset('d', 2, 1); big_data['settings']['note'] = 'x' * 2000000; big_env = envelope(big_data)
    ctx, page, errors, fk = setup(b, {LIST: [(200, [row(ID1, big_env)])], dl_key(ID1): [(200, dl_body(big_env))]})
    load_list(page); items(page).nth(0).click(); page.wait_for_timeout(2000)
    check(restore_open(page) and not errors, 'R10 payload d\'environ 2 Mo : écran de restauration ouvert')
    ctx.close()

    # R11 (nettoyage lot 16) : réponse tardive du téléchargement ignorée si le compte a changé, si Réglages a été quitté
    # ou si un écran de restauration est déjà ouvert (fichier importé entre temps). Témoin : réponse à temps, écran ouvert.
    OTHER = envelope(dataset('d', 1, 20)); other_path = F / 'fab-autre.json'; other_path.write_text(json.dumps(OTHER))
    def late(name, during, expect_msg, keep_restore_text=False):
        ctx, page, errors, fk = setup(b, {LIST: [(200, STD_LIST)]})
        held = []
        page.route(re.compile(r'https://[^/]*\.supabase\.co/rest/v1/backups\?id=eq\..*'), lambda route, request: held.append(route))
        load_list(page); before = data(page)
        items(page).nth(0).click(); page.wait_for_timeout(400)
        during(page)
        shown = page.inner_text('#restore-page') if restore_open(page) else None
        held[0].fulfill(status=200, body=json.dumps(dl_body(ENV)), headers={'content-type': 'application/json'}); page.wait_for_timeout(600)
        after_shown = page.inner_text('#restore-page') if restore_open(page) else None
        if not restore_open(page) and not page.is_visible('#cloud-message'): settings(page)
        m = page.inner_text('#cloud-message') if restore_open(page) else msg(page)
        ok_screen = (after_shown == shown and shown is not None) if keep_restore_text else (after_shown is None)
        ok = (expect_msg in m and ok_screen and data(page) == before and not errors) if expect_msg else (after_shown is not None and 'Sauvegarde en ligne' in after_shown)
        check(ok, 'R11 %s : message "%s"' % (name, m[:100]))
        ctx.close()
    late('témoin, réponse à temps', lambda page: None, None)
    late('fichier importé pendant le téléchargement', lambda page: (page.set_input_files('#dashboard-import-input', str(other_path)), page.wait_for_timeout(500)),
         'un autre écran a été ouvert', keep_restore_text=True)
    late('Réglages quitté pendant le téléchargement', lambda page: (page.click('.nav-btn[data-target="seance"]'), page.wait_for_timeout(200)), 'un autre écran a été ouvert')
    late('autre compte pendant le téléchargement', lambda page: put_session(page, user='u-2', email='deux@exemple.test'), 'la connexion a changé')
    late('déconnecté dans une autre fenêtre', lambda page: page.evaluate("() => localStorage.removeItem('ovryk.cloud.auth')"), 'la connexion a changé')

    b.close()
print('\n%d/%d' % (sum(res), len(res)))
