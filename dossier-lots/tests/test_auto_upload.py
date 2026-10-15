"""Lot 16, livraison 5 : envoi automatique de la sauvegarde en ligne après une séance.
Supabase simulé (routes Playwright), données FABRIQUÉES ici : aucun vrai
export, aucune vraie clé de session, aucun appel réseau réel.
Usage : python3 test_auto_upload.py <dossier de travail>, site servi sur http://127.0.0.1:8765."""
import sys, json, time, re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright
SP = Path(sys.argv[1]); URL = 'http://127.0.0.1:8765/index.html'
HOST = 'https://hroxwrcxvhpvlpmxeixw.supabase.co'
F = SP / 'files'; F.mkdir(exist_ok=True)
res = []
def check(c, m): res.append(bool(c)); print(('ok     ' if c else 'ECHEC  ') + m)
DATA_KEYS = ['ovryk.exercises', 'ovryk.routines', 'ovryk.sessions', 'ovryk.settings', 'ovryk.forceCycles', 'ovryk.meta']
CLOUD_KEYS = ['ovryk.cloud.auth', 'ovryk.cloud.lastUpload', 'ovryk.cloud.prefs', 'ovryk.cloud.lastAttempt']
POST = 'POST /rest/v1/backups'
VERIFY = 'VERIFY'
REFRESH = 'POST /auth/v1/token?grant_type=refresh_token'
LIST_PREFIX = 'GET /rest/v1/backups?select=id,created_at'

# ---------- fixtures fabriquées ----------
def done_session(sid, day):
    return {'id': sid, 'status': 'completed', 'date': '2026-09-%02dT10:00:00.000Z' % day, 'completedAt': '2026-09-%02dT11:00:00.000Z' % day,
            'startedAt': '2026-09-%02dT10:00:00.000Z' % day, 'routineId': None,
            'exercises': [{'id': 'sex-%s' % sid, 'exerciseId': 'ex-fab-1', 'exerciseName': 'Mouvement fabrique', 'category': 'Pectoraux',
                           'restSeconds': 90, 'sets': [{'reps': 5, 'weight': 60, 'done': True}]}]}
def live_session(sid):
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    s = done_session(sid, 1); s.update({'status': 'in_progress', 'date': now, 'startedAt': now}); s.pop('completedAt')
    return s
def dataset(n):
    return {'exercises': [{'id': 'ex-fab-1', 'name': 'Mouvement fabrique', 'category': 'Pectoraux', 'equipment': 'Barre', 'unit': 'kg', 'isCustom': True}],
            'routines': [], 'sessions': [done_session('s-%d' % i, 1 + i) for i in range(n)],
            'settings': {'unit': 'kg', 'restTimerSeconds': 90, 'lastExportAt': None}, 'forceCycles': {}, 'meta': {'schemaVersion': 2}}
LOCAL = dataset(3)
def iso(days_ago=0): return (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
def tok(access='acc-1', refresh='ref-1'):
    return {'access_token': access, 'refresh_token': refresh, 'expires_in': 3600, 'user': {'id': 'u-1', 'email': 'un@exemple.test'}}

class Fake:
    """plan : 'METHODE chemin' -> liste de réponses (status, corps) | ('hang', None) | ('abort', None).
    VERIFY : relecture d'une ligne envoyée ; 'echo' renvoie l'empreinte et le nombre de séances réellement envoyés."""
    def __init__(self, page, plan):
        self.plan = plan; self.calls = []; self.sent = []
        page.route(re.compile(r'https://[^/]*\.supabase\.co/.*'), self.handle)
    def handle(self, route, request):
        path = request.url.replace(HOST, '')
        key = request.method + ' ' + path
        if key.startswith('GET /rest/v1/backups?id=eq.') and key.endswith('&select=fingerprint,sessions_count'): key = VERIFY
        if key.startswith(LIST_PREFIX): key = 'LIST'
        self.calls.append({'key': key, 'headers': request.headers})
        if key == POST:
            try: self.sent.append(json.loads(request.post_data))
            except Exception: self.sent.append(None)
        seq = self.plan.get(key)
        if not seq: route.fulfill(status=599, body='inattendu'); return
        st, body = seq.pop(0) if len(seq) > 1 else seq[0]
        if st == 'hang': return
        if st == 'abort': route.abort(); return
        if body == 'echo':
            last = self.sent[-1] or {}
            body = [{'fingerprint': last.get('fingerprint'), 'sessions_count': last.get('sessions_count')}]
        route.fulfill(status=st, body=body if isinstance(body, str) else json.dumps(body), headers={'content-type': 'application/json'})
    def keys(self): return [c['key'] for c in self.calls]

ADD_LIVE = "() => { const s = JSON.parse(localStorage.getItem('ovryk.sessions')); const n = JSON.parse(JSON.stringify(s[0])); n.id = 's-live' + s.length; n.status = 'in_progress'; delete n.completedAt; n.date = n.startedAt = new Date().toISOString(); s.push(n); localStorage.setItem('ovryk.sessions', JSON.stringify(s)); }"
OK_PLAN = lambda: {POST: [(201, '')], VERIFY: [(200, 'echo')]}

def ls(page): return page.evaluate("() => { const o = {}; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); o[k] = localStorage.getItem(k); } return o; }")
def jget(page, key):
    v = page.evaluate("(k) => localStorage.getItem(k)", key); return json.loads(v) if v else None
def jset(page, key, value): page.evaluate("([k, v]) => localStorage.setItem(k, v)", [key, json.dumps(value)])
def fresh(b, local=LOCAL, session=True, prefs=None, last_upload=None, last_attempt=None, live=True):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', accept_downloads=True)
    page = ctx.new_page(); errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(URL); page.evaluate("() => localStorage.clear()")
    d = json.loads(json.dumps(local))
    if live: d['sessions'].append(live_session('s-live'))
    for k, v in d.items(): jset(page, 'ovryk.' + k, v)
    if session: jset(page, 'ovryk.cloud.auth', {'access_token': 'acc-0', 'refresh_token': 'ref-0', 'expires_at': int(time.time()) + 3600, 'user': {'id': 'u-1', 'email': 'un@exemple.test'}, 'savedAt': iso()})
    if prefs is not None: jset(page, 'ovryk.cloud.prefs', prefs)
    if last_upload is not None: jset(page, 'ovryk.cloud.lastUpload', last_upload)
    if last_attempt is not None: jset(page, 'ovryk.cloud.lastAttempt', last_attempt)
    # deux démarrages : la migration existante complète le catalogue au premier, liftBaseMode au second
    page.reload(); page.wait_for_timeout(300); page.reload(); page.wait_for_timeout(300)
    return ctx, page, errors
def settings(page):
    page.click('.nav-btn[data-target="dashboard"]'); page.wait_for_timeout(150); page.click('#dash-settings-btn'); page.wait_for_timeout(300)
def home(page):
    page.click('.nav-btn[data-target="dashboard"]'); page.wait_for_timeout(250)
def text(page, sel): return page.inner_text(sel) if page.is_visible(sel) else ''
def finish(page, wait=900):
    page.click('.nav-btn[data-target="seance"]'); page.wait_for_timeout(300)
    page.click('#seance-finish-btn'); page.wait_for_timeout(200)
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(wait)
def statuses(page): return {s['id']: s['status'] for s in jget(page, 'ovryk.sessions')}

with sync_playwright() as p:
    b = p.chromium.launch()

    # A0 : rien au lancement ni à l'ouverture de Réglages ou de l'Accueil, même avec un échec enregistré
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}, last_upload={'at': iso(9), 'id': 'x', 'fingerprint': '00000000', 'sessionsCompleted': 1, 'userId': 'u-1'},
                              last_attempt={'at': iso(1), 'origin': 'auto', 'outcome': 'failed', 'reason': 'Pas de connexion internet. Rien n’a été envoyé.'})
    fk = Fake(page, {}); before = ls(page)
    page.reload(); page.wait_for_timeout(400); fk2 = Fake(page, {}); home(page); settings(page); home(page)
    check(ls(page) == before and not fk.calls and not fk2.calls and not errors, 'A0 lancement, Accueil et Réglages : aucune écriture, aucun appel (%s)' % errors[:1])
    ctx.close()

    # A1 : option désactivée par défaut, aucun appel à la fin de séance, aucune clé
    ctx, page, errors = fresh(b); fk = Fake(page, OK_PLAN())
    settings(page)
    toggle = page.locator('#cloud-auto-row .profile-toggle')
    check(toggle.count() == 1 and toggle.get_attribute('aria-pressed') == 'false' and jget(page, 'ovryk.cloud.prefs') is None,
          'A1 interrupteur visible une fois connecté, désactivé par défaut, ovryk.cloud.prefs absente')
    finish(page)
    check(statuses(page).get('s-live') == 'completed' and not fk.calls and jget(page, 'ovryk.cloud.lastAttempt') is None and not errors,
          'A1 option désactivée : séance terminée, aucun appel, aucun dernier essai écrit')
    ctx.close()

    # A2 : interrupteur, écrit au seul appui
    ctx, page, errors = fresh(b); fk = Fake(page, {}); settings(page)
    b0 = ls(page); page.click('#cloud-auto-row .profile-toggle'); page.wait_for_timeout(150)
    b1 = ls(page)
    changed = {k for k in set(b0) | set(b1) if b0.get(k) != b1.get(k)}
    check(changed == {'ovryk.cloud.prefs'} and jget(page, 'ovryk.cloud.prefs') == {'autoUpload': True} and
          page.locator('#cloud-auto-row .profile-toggle').get_attribute('aria-pressed') == 'true' and not fk.calls,
          'A2 appui : seule ovryk.cloud.prefs écrite (autoUpload true), aucun appel')
    ctx.close()

    # A3 : envoi automatique réussi et vérifié ; la séance est terminée avant la réponse
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}); fk = Fake(page, {POST: [('hang', None)]})
    finish(page, wait=400)
    check(statuses(page).get('s-live') == 'completed' and page.is_visible('#seance-start-empty-btn') and fk.keys() == [POST],
          'A3 séance terminée et écran de départ affiché pendant que l\'envoi attend encore')
    att = jget(page, 'ovryk.cloud.lastAttempt')
    check(att and att['outcome'] == 'in_progress' and att['origin'] == 'auto' and att['sessionId'] == 's-live' and att['sessionsCompleted'] == 4,
          'A3 dernier essai "en cours" écrit avant la réponse (%s)' % (att and att['outcome']))
    sent = fk.sent[0] or {}
    payload = json.loads(sent.get('payload', '{}'))
    live_in_payload = [s for s in payload.get('data', {}).get('sessions', []) if s['id'] == 's-live']
    check(sent.get('sessions_count') == 4 and live_in_payload and live_in_payload[0]['status'] == 'completed' and 'cloud' not in json.dumps(payload.get('data', {})),
          'A3 ligne envoyée : 4 séances, la séance terminée incluse (completed), aucune clé cloud dans les données')
    ctx.close()
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}); fk = Fake(page, OK_PLAN())
    finish(page)
    att = jget(page, 'ovryk.cloud.lastAttempt'); lu = jget(page, 'ovryk.cloud.lastUpload')
    check(fk.keys() == [POST, VERIFY] and att['outcome'] == 'ok' and lu and lu['sessionsCompleted'] == 4 and lu['userId'] == 'u-1' and not errors,
          'A3 envoi puis relecture, dernier essai ok, lastUpload avec userId u-1 et 4 séances')
    settings(page)
    check('réussi et vérifié' in text(page, '#cloud-last-attempt') and not page.is_visible('#cloud-pending') and not page.is_visible('#cloud-reminder'),
          'A3 Réglages : "%s", rien à renvoyer' % text(page, '#cloud-last-attempt'))
    home(page)
    check(not page.is_visible('#cloud-home-line'), 'A3 Accueil : aucune ligne quand tout va bien')
    ctx.close()

    # A4 : hors ligne, la séance se termine, échec visible, rattrapé par l'envoi manuel
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}, last_upload={'at': iso(1), 'id': 'x', 'fingerprint': '00000000', 'sessionsCompleted': 3, 'userId': 'u-1'})
    # hors ligne : navigator.onLine faux et requête coupée (une route simulée n'est pas coupée par set_offline)
    fk = Fake(page, {POST: [('abort', None)], VERIFY: [(200, 'echo')]}); ctx.set_offline(True)
    finish(page)
    fk.plan[POST] = [(201, '')]
    att = jget(page, 'ovryk.cloud.lastAttempt')
    check(statuses(page).get('s-live') == 'completed' and att['outcome'] == 'failed' and 'Pas de connexion internet' in att['reason'] and not errors,
          'A4 hors ligne : séance terminée, essai en échec "%s"' % att['reason'][:60])
    home(page)
    check('dernier envoi échoué' in text(page, '#cloud-home-line'), 'A4 Accueil : "%s"' % text(page, '#cloud-home-line'))
    settings(page)
    check('À renvoyer : 1 séance terminée' in text(page, '#cloud-pending') and 'Pas de connexion internet' in text(page, '#cloud-last-attempt'),
          'A4 Réglages : "%s"' % text(page, '#cloud-pending'))
    ctx.set_offline(False); page.click('#cloud-upload-btn'); page.wait_for_timeout(900)
    att = jget(page, 'ovryk.cloud.lastAttempt')
    check(att['outcome'] == 'ok' and att['origin'] == 'manual' and not page.is_visible('#cloud-pending'), 'A4 envoi manuel : essai manuel ok, plus rien à renvoyer')
    home(page)
    check(not page.is_visible('#cloud-home-line'), 'A4 Accueil : ligne disparue après l\'envoi réussi')
    ctx.close()

    # A5 : appli fermée pendant l'envoi : "interrompu" au rechargement, sans écriture au lancement
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}); fk = Fake(page, {POST: [('hang', None)]})
    finish(page, wait=400)
    # appli tuée : la page est fermée sans que son JavaScript ne continue, puis rouverte
    before = ls(page); page.close()
    page = ctx.new_page(); Fake(page, {}); page.goto(URL); page.wait_for_timeout(400)
    home(page)
    check(ls(page) == before and 'interrompu' in text(page, '#cloud-home-line'), 'A5 rechargement en plein envoi : rien écrit, Accueil "%s"' % text(page, '#cloud-home-line'))
    settings(page)
    check('interrompu' in text(page, '#cloud-last-attempt'), 'A5 Réglages : "%s"' % text(page, '#cloud-last-attempt')[:90])
    ctx.close()

    # A6 : garde-fou (même compte), envoi manuel toujours possible ; autre compte : pas de garde-fou
    lu_high = {'at': iso(1), 'id': 'x', 'fingerprint': '00000000', 'sessionsCompleted': 10, 'userId': 'u-1'}
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}, last_upload=lu_high); fk = Fake(page, OK_PLAN())
    finish(page)
    att = jget(page, 'ovryk.cloud.lastAttempt')
    check(not fk.calls and att['outcome'] == 'skipped' and 'suspendu' in att['reason'] and jget(page, 'ovryk.cloud.lastUpload') == lu_high,
          'A6 garde-fou : aucun appel, essai noté "%s"' % att['reason'][:70])
    home(page)
    check('suspendu' in text(page, '#cloud-home-line'), 'A6 Accueil : "%s"' % text(page, '#cloud-home-line'))
    settings(page)
    check('4 séances terminées' in text(page, '#cloud-pending') and 'en avait 10' in text(page, '#cloud-pending'), 'A6 Réglages : message du garde-fou')
    page.click('#cloud-upload-btn'); page.wait_for_timeout(900)
    check(fk.keys() == [POST, VERIFY] and jget(page, 'ovryk.cloud.lastUpload')['sessionsCompleted'] == 4 and not page.is_visible('#cloud-pending'),
          'A6 envoi manuel accepté, garde-fou levé')
    ctx.close()
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}, last_upload=dict(lu_high, userId='u-9')); fk = Fake(page, OK_PLAN())
    finish(page)
    check(fk.keys() == [POST, VERIFY], 'A6 dernier envoi d\'un autre compte : pas de garde-fou, envoi fait')
    ctx.close()
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}, last_upload={'at': iso(1), 'id': 'x', 'fingerprint': '00000000', 'sessionsCompleted': 10}); fk = Fake(page, OK_PLAN())
    finish(page)
    check(not fk.calls, 'A6 dernier envoi sans userId (avant la livraison 5) : garde-fou appliqué par prudence')
    ctx.close()

    # A7 : délai de 2 minutes entre deux envois automatiques
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}, last_attempt={'at': iso(0), 'origin': 'auto', 'outcome': 'ok', 'reason': ''})
    fk = Fake(page, OK_PLAN())
    finish(page)
    att = jget(page, 'ovryk.cloud.lastAttempt')
    check(not fk.calls and att['outcome'] == 'ok' and statuses(page).get('s-live') == 'completed',
          'A7 envoi automatique récent : rien envoyé, le dernier essai réel (ok) n\'est pas écrasé par un "non envoyé"')
    ctx.close()
    # A7b : le délai part du dernier vrai essai, même après un "non envoyé" puis un rechargement (mémoire perdue)
    at90 = (datetime.now(timezone.utc) - timedelta(seconds=90)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}, last_attempt={'at': at90, 'origin': 'auto', 'outcome': 'ok', 'reason': ''})
    fk = Fake(page, OK_PLAN())
    finish(page)
    page.evaluate(ADD_LIVE); page.reload(); page.wait_for_timeout(400); fk2 = Fake(page, OK_PLAN())
    finish(page)
    check(not fk.calls and not fk2.calls and jget(page, 'ovryk.cloud.lastAttempt')['at'] == at90,
          'A7b "non envoyé" puis rechargement, toujours dans les 2 minutes du dernier vrai essai : rien envoyé, essai réel gardé')
    ctx.close()

    # A8 : verrou pris (liste en cours) : rien envoyé, noté
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}); fk = Fake(page, {'LIST': [('hang', None)]})
    settings(page); page.click('#cloud-list-btn'); page.wait_for_timeout(200)
    finish(page)
    att = jget(page, 'ovryk.cloud.lastAttempt')
    check(fk.keys() == ['LIST'] and att['outcome'] == 'skipped' and 'autre opération' in att['reason'] and statuses(page).get('s-live') == 'completed',
          'A8 verrou pris : aucun envoi, essai noté, séance terminée')
    ctx.close()

    # A9 : 401 puis renouvellement et un seul rejeu ; renouvellement refusé : échec, session effacée
    ctx, page, errors = fresh(b, prefs={'autoUpload': True})
    fk = Fake(page, {POST: [(401, {'code': 'PGRST301'}), (201, '')], REFRESH: [(200, tok())], VERIFY: [(200, 'echo')]})
    finish(page, wait=1200)
    check(fk.keys() == [POST, REFRESH, POST, VERIFY] and fk.calls[2]['headers'].get('authorization') == 'Bearer acc-1' and jget(page, 'ovryk.cloud.lastAttempt')['outcome'] == 'ok',
          'A9 401 : renouvellement, un seul rejeu avec le nouveau jeton, essai ok')
    ctx.close()
    ctx, page, errors = fresh(b, prefs={'autoUpload': True})
    fk = Fake(page, {POST: [(401, {'code': 'PGRST301'})], REFRESH: [(400, {'error_code': 'refresh_token_already_used'})]})
    finish(page, wait=1200)
    att = jget(page, 'ovryk.cloud.lastAttempt')
    check(att['outcome'] == 'failed' and 'Reconnecte-toi' in att['reason'] and jget(page, 'ovryk.cloud.auth') is None and statuses(page).get('s-live') == 'completed',
          'A9 session révoquée : essai en échec "%s", session effacée, séance intacte' % att['reason'][:50])
    ctx.close()

    # A10 : relecture différente : non vérifié, jamais "réussi"
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}); fk = Fake(page, {POST: [(201, '')], VERIFY: [(200, [])]})
    finish(page)
    att = jget(page, 'ovryk.cloud.lastAttempt')
    check(att['outcome'] == 'unverified' and jget(page, 'ovryk.cloud.lastUpload') is None, 'A10 relecture absente : non vérifié, lastUpload non écrit')
    home(page)
    check('non confirmé' in text(page, '#cloud-home-line'), 'A10 Accueil : "%s"' % text(page, '#cloud-home-line'))
    ctx.close()

    # A11 : rappel de plus de 7 jours, connecté ou non, seulement s'il reste des séances à renvoyer
    for name, lu, sess, expect in [
            ('8 jours, 2 séances à renvoyer, déconnecté', {'at': iso(8), 'id': 'x', 'fingerprint': '00000000', 'sessionsCompleted': 1, 'userId': 'u-1'}, False, True),
            ('8 jours, rien à renvoyer', {'at': iso(8), 'id': 'x', 'fingerprint': '00000000', 'sessionsCompleted': 3, 'userId': 'u-1'}, True, False),
            ('3 jours, 2 séances à renvoyer', {'at': iso(3), 'id': 'x', 'fingerprint': '00000000', 'sessionsCompleted': 1, 'userId': 'u-1'}, True, False),
            ('aucun envoi jamais réussi', None, True, False)]:
        ctx, page, errors = fresh(b, session=sess, last_upload=lu, live=False); fk = Fake(page, {})
        before = ls(page); home(page); line = text(page, '#cloud-home-line'); settings(page); rem = text(page, '#cloud-reminder')
        line, rem = line.lower(), rem.lower()   # le rappel de Réglages est en capitales (CSS)
        ok = (('7 jours' in line and '2 séances terminées' in line and 'il y a 8 jours' in rem) if expect else (not line and not rem))
        check(ok and ls(page) == before and not fk.calls, 'A11 %s : Accueil "%s", Réglages "%s"' % (name, line, rem[:70]))
        ctx.close()

    # A12 : clés cloud hors export et hors restauration ; effacées par Réinitialiser l'app
    cloud_state = {'prefs': {'autoUpload': True}, 'last_upload': {'at': iso(1), 'id': 'x', 'fingerprint': '00000000', 'sessionsCompleted': 3, 'userId': 'u-1'},
                   'last_attempt': {'at': iso(1), 'origin': 'manual', 'outcome': 'ok', 'reason': 'x'}}
    ctx, page, errors = fresh(b, live=False, **cloud_state); settings(page)
    with page.expect_download() as dl: page.click('#dashboard-export-btn')
    exp = F / 'fab-auto-export.json'; dl.value.save_as(str(exp)); exported = exp.read_text()
    check('autoUpload' not in exported and 'lastAttempt' not in exported and 'lastUpload' not in exported and 'acc-0' not in exported,
          'A12 export : aucune clé ovryk.cloud.* ni jeton dans le fichier')
    cloud_before = {k: ls(page).get(k) for k in CLOUD_KEYS}
    env = json.loads(exported); env['data']['sessions'] = env['data']['sessions'][:2]
    env['summary'].pop('checksum', None)
    imp = F / 'fab-auto-import.json'; imp.write_text(json.dumps(env))
    page.set_input_files('#dashboard-import-input', str(imp)); page.wait_for_timeout(500)
    page.click('#restore-confirm-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(1500)
    cloud_after = {k: ls(page).get(k) for k in CLOUD_KEYS}
    check(len(jget(page, 'ovryk.sessions')) == 2 and cloud_after == cloud_before, 'A12 restauration d\'un fichier : clés ovryk.cloud.* inchangées')
    settings(page)
    page.click('#reset-app-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(1500)
    left = [k for k in ls(page) if k.startswith('ovryk.cloud.')]
    check(not left, 'A12 Réinitialiser l\'app : plus aucune clé ovryk.cloud.* (%s)' % left)
    ctx.close()

    # A13 : un échec, puis une séance dans les 2 minutes : l'alerte de l'échec reste, le délai part de l'échec
    ref = {'at': iso(1), 'id': 'x', 'fingerprint': '00000000', 'sessionsCompleted': 3, 'userId': 'u-1'}
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}, last_upload=ref); fk = Fake(page, {POST: [(500, '')]})
    finish(page)
    first = jget(page, 'ovryk.cloud.lastAttempt')
    home(page)
    check(first['outcome'] == 'failed' and 'échoué' in text(page, '#cloud-home-line'), 'A13 échec automatique : Accueil "%s"' % text(page, '#cloud-home-line'))
    page.evaluate("() => { const s = JSON.parse(localStorage.getItem('ovryk.sessions')); const n = JSON.parse(JSON.stringify(s[0])); n.id = 's-live2'; n.status = 'in_progress'; delete n.completedAt; n.date = n.startedAt = new Date().toISOString(); s.push(n); localStorage.setItem('ovryk.sessions', JSON.stringify(s)); }")
    page.reload(); page.wait_for_timeout(400); fk = Fake(page, OK_PLAN())
    finish(page)
    second = jget(page, 'ovryk.cloud.lastAttempt')
    home(page)
    check(not fk.calls and second == first, 'A13 deuxième séance dans les 2 minutes : rien envoyé, lastAttempt inchangé (échec et date gardés)')
    check('échoué' in text(page, '#cloud-home-line'), 'A13 l\'Accueil signale toujours le problème : "%s"' % text(page, '#cloud-home-line'))
    settings(page)
    check('À renvoyer : 2 séances terminées' in text(page, '#cloud-pending'), 'A13 Réglages : "%s"' % text(page, '#cloud-pending'))
    page.click('#cloud-upload-btn'); page.wait_for_timeout(900)
    home(page)
    check(jget(page, 'ovryk.cloud.lastAttempt')['outcome'] == 'ok' and not page.is_visible('#cloud-home-line'), 'A13 envoi manuel réussi : alerte levée')
    ctx.close()

    # A14 : aucun envoi de référence (absent, ou d'un autre compte) : l'Accueil ne reste pas muet, "À renvoyer" compte les séances du téléphone
    for name, lu, att, expect_line, expect_pending in [
            ('aucun lastUpload, échec', None, {'at': iso(1), 'origin': 'auto', 'outcome': 'failed', 'reason': 'Pas de connexion internet. Rien n’a été envoyé.'}, 'échoué', '3 séances terminées'),
            ('aucun lastUpload, non confirmé', None, {'at': iso(1), 'origin': 'manual', 'outcome': 'unverified', 'reason': 'x'}, 'non confirmé', '3 séances terminées'),
            ('aucun lastUpload, non envoyé', None, {'at': iso(1), 'origin': 'auto', 'outcome': 'skipped', 'reason': 'Non envoyé (x). À renvoyer.'}, 'non effectué', '3 séances terminées'),
            ('lastUpload d\'un autre compte, échec', dict(ref, userId='u-9', sessionsCompleted=1), {'at': iso(1), 'origin': 'auto', 'outcome': 'failed', 'reason': 'x'}, 'échoué', '3 séances terminées'),
            ('aucun lastUpload, dernier essai réussi', None, {'at': iso(1), 'origin': 'manual', 'outcome': 'ok', 'reason': ''}, '', ''),
            ('aucun lastUpload, aucun essai', None, None, '', '')]:
        ctx, page, errors = fresh(b, prefs={'autoUpload': True}, live=False, last_upload=lu, last_attempt=att); fk = Fake(page, {})
        before = ls(page); home(page); line = text(page, '#cloud-home-line'); settings(page); pend = text(page, '#cloud-pending')
        ok = (expect_line in line and expect_line != '' and expect_pending in pend) if expect_line else (not line and not pend)
        check(ok and ls(page) == before and not fk.calls, 'A14 %s : Accueil "%s", Réglages "%s"' % (name, line, pend))
        ctx.close()
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}); fk = Fake(page, {POST: [(500, '')]})
    finish(page); settings(page)
    check('À renvoyer : 4 séances terminées' in text(page, '#cloud-pending'), 'A14 de bout en bout (aucune référence, échec de la fin de séance) : "%s"' % text(page, '#cloud-pending'))
    ctx.close()

    # A15 : déconnecté après une session révoquée : Réglages explique l'échec hors de la zone connectée
    ctx, page, errors = fresh(b, prefs={'autoUpload': True})
    fk = Fake(page, {POST: [(401, {'code': 'PGRST301'})], REFRESH: [(400, {'error_code': 'refresh_token_already_used'})]})
    finish(page, wait=1200)
    home(page); line = text(page, '#cloud-home-line'); settings(page)
    out = text(page, '#cloud-last-attempt-out')
    check('échoué' in line and page.is_visible('#cloud-signin-form') and not page.is_visible('#cloud-connected') and 'Reconnecte-toi' in out and not page.is_visible('#cloud-last-attempt'),
          'A15 déconnecté : Accueil "%s", Réglages "%s"' % (line, out[:80]))
    ctx.close()
    ctx, page, errors = fresh(b, session=False, live=False); Fake(page, {}); settings(page)
    check(not page.is_visible('#cloud-last-attempt-out'), 'A15 déconnecté sans dernier essai : rien d\'affiché')
    ctx.close()

    # A16 (nettoyage lot 16) : envoi réussi puis séance "non envoyée" : l'Accueil signale les séances pas encore en ligne
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}); fk = Fake(page, {POST: [('hang', None)]})
    finish(page, wait=400); home(page)
    check(not page.is_visible('#cloud-home-line'), 'A16 envoi en cours : aucune ligne sur l\'Accueil')
    ctx.close()
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}); fk = Fake(page, OK_PLAN())
    finish(page); home(page)
    check(not page.is_visible('#cloud-home-line'), 'A16 envoi réussi : aucune ligne')
    page.evaluate(ADD_LIVE); page.reload(); page.wait_for_timeout(400); fk = Fake(page, OK_PLAN())
    finish(page); home(page)
    line = text(page, '#cloud-home-line')
    check(not fk.calls and '1 séance terminée pas encore en ligne' in line, 'A16 séance dans les 2 minutes : Accueil "%s"' % line)
    page.click('#cloud-home-line'); page.wait_for_timeout(300)
    check(page.is_visible('#cloud-upload-btn'), 'A16 appui sur la ligne : Réglages ouvert')
    page.click('#cloud-upload-btn'); page.wait_for_timeout(900); home(page)
    check(not page.is_visible('#cloud-home-line'), 'A16 envoi manuel réussi : ligne levée')
    ctx.close()
    ctx, page, errors = fresh(b, live=False, last_upload={'at': iso(1), 'id': 'x', 'fingerprint': '00000000', 'sessionsCompleted': 2, 'userId': 'u-1'}); Fake(page, {})
    home(page)
    check(not page.is_visible('#cloud-home-line'), 'A16 envoi automatique désactivé, 1 séance non envoyée depuis 1 jour : aucune ligne (pas de rappel avant 7 jours)')
    ctx.close()
    ctx, page, errors = fresh(b, session=False, live=False, prefs={'autoUpload': True}, last_upload={'at': iso(1), 'id': 'x', 'fingerprint': '00000000', 'sessionsCompleted': 2, 'userId': 'u-1'}); Fake(page, {})
    home(page)
    check(not page.is_visible('#cloud-home-line'), 'A16 envoi automatique actif mais déconnecté : aucune ligne "%s"' % text(page, '#cloud-home-line'))
    ctx.close()

    # A17 (nettoyage lot 16) : Réinitialiser refusé pendant un envoi en cours
    ctx, page, errors = fresh(b, prefs={'autoUpload': True}); fk = Fake(page, {POST: [('hang', None)]})
    finish(page, wait=400); settings(page); before = ls(page)
    page.click('#reset-app-btn'); page.wait_for_timeout(300)
    io = page.inner_text('#dashboard-io-status')
    check('en cours' in io and 'Rien n’a été supprimé' in io and not page.is_visible('#confirm-modal-confirm') and ls(page) == before,
          'A17 Réinitialiser pendant un envoi : refus "%s", aucune fenêtre, rien effacé' % io[:70])
    ctx.close()

    b.close()

print('\n%d/%d' % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
