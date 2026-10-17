"""Cycles liés au programme, livraison 3a : "Tirer un autre mouvement" sur
l'écran de fin de cycle. Pool du tirage, confirmation, remplacement dans
toutes les routines (créneau conservé, prise remise à null), entrée du
mouvement terminé laissée en place, reprise d'une entrée en attente hors
programme, échecs d'écriture et remise en état, double tap, R7, séance en
cours, aucune écriture à l'ouverture ni à l'annulation.
Données FABRIQUÉES ici : aucun vrai export, aucun appel réseau.
Usage : python3 test_cycles_fin.py <dossier de travail>, site servi sur http://127.0.0.1:8765."""
import sys, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright
SP = Path(sys.argv[1]); URL = 'http://127.0.0.1:8765/index.html'
SP.mkdir(parents=True, exist_ok=True)
res = []
def check(c, m): res.append(bool(c)); print(('ok     ' if c else 'ECHEC  ') + m)
DATA_KEYS = ['ovryk.exercises', 'ovryk.routines', 'ovryk.sessions', 'ovryk.settings', 'ovryk.forceCycles', 'ovryk.meta']
FAIL = "Le changement de mouvement a échoué (stockage plein ou indisponible). "
KEPT = FAIL + "Tes routines et tes cycles sont restés comme avant."
ONERM = " Seul le 1RM validé de Deadlift fab (110 kg) a été enregistré sur l'exercice."
EMPTY = "Aucun mouvement disponible. 20 mouvements Lifting n'ont pas de 1RM saisi. Le 1RM se saisit dans Exercices."
MSG_RE = re.compile(r"^Remplacer Deadlift fab par (.+?) dans (.+) \? (.+?), cycle (\d+), semaine 1, 1RM ([\d,]+) kg\.$")
LETTERS = {'13': 'A', '14': 'B', '15': 'C', '16': 'D', '17': 'E'}

# ---------- fixtures fabriquées ----------
def ex(eid, name, orm=None, cat='Lifting', start=None):
    d = {'id': eid, 'name': name, 'category': cat, 'equipment': 'Barre', 'unit': 'kg', 'isCustom': True, 'oneRepMax': orm}
    if cat == 'Lifting': d['liftBaseMode'] = 'force'
    if start: d['forceCycleStartDate'] = start
    return d
def active(eid, orm, cyc='D', week=2):
    return {'exercise_id': eid, 'cycle_actif': cyc, 'one_rm_actuel': orm, 'semaine_actuelle': week,
            'historique_1rm': [{'date': '2026-08-01T10:00:00.000Z', 'valeur': orm}], 'historique_cycles': [], 'prochain_cycle': None,
            'en_attente_de_validation': False, 'semaines_modifiees': {}, 'test_report_used': False, 'decalage_semaines': 0}
def pending(eid, start, after, cyc='C', nxt='D'):
    return {'exercise_id': eid, 'cycle_actif': cyc, 'one_rm_actuel': after, 'semaine_actuelle': 6,
            'historique_1rm': [{'date': '2026-08-01T10:00:00.000Z', 'valeur': start}, {'date': '2026-09-12T10:00:00.000Z', 'valeur': after}],
            'historique_cycles': [{'cycle': cyc, 'debut': '2026-08-01T10:00:00.000Z', 'fin': '2026-09-12T10:00:00.000Z', 'seances': 6,
                                   'seances_prevues': 6, 'reussite_pct': 90, 'one_rm_avant': start, 'one_rm_apres': after}],
            'prochain_cycle': nxt, 'en_attente_de_validation': True, 'semaines_modifiees': {}, 'test_report_used': False, 'decalage_semaines': 0}
def rex(eid, sets=1, weight=40, rest=120, **extra):
    d = {'exerciseId': eid, 'restSeconds': rest, 'sets': [{'reps': 5, 'weight': weight, 'weightKg': weight} for _ in range(sets)]}
    d.update(extra); return d
def routine(rid, name, rexes):
    return {'id': rid, 'name': name, 'weekdays': [], 'updatedAt': '2026-09-01T00:00:00.000Z', 'createdAt': '2026-09-01T00:00:00.000Z',
            'exercises': [r if isinstance(r, dict) else rex(r) for r in rexes]}
def dataset(exercises, routines, cycles, settings=None):
    st = {'unit': 'kg', 'restTimerSeconds': 90, 'lastExportAt': None}
    st.update(settings or {})
    return {'exercises': exercises, 'routines': routines, 'sessions': [], 'settings': st, 'forceCycles': cycles, 'meta': {'schemaVersion': 2}}

def ls(page): return page.evaluate("() => { const o = {}; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); o[k] = localStorage.getItem(k); } return o; }")
def data(page): return {k: v for k, v in ls(page).items() if k in DATA_KEYS}
def cycles(page): return json.loads(ls(page)['ovryk.forceCycles'])
def routines(page): return json.loads(ls(page)['ovryk.routines'])
def exs(page): return {e['id']: e for e in json.loads(ls(page)['ovryk.exercises'])}
def fresh(b, d):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    page = ctx.new_page(); errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(URL); page.evaluate("() => localStorage.clear()")
    for k, v in d.items(): page.evaluate("([k, v]) => localStorage.setItem(k, v)", ['ovryk.' + k, json.dumps(v)])
    page.reload(); page.wait_for_timeout(300); page.reload(); page.wait_for_timeout(300)
    return ctx, page, errors
def nav(page, target): page.click('.nav-btn[data-target="%s"]' % target); page.wait_for_timeout(300)
def open_end(page):
    nav(page, 'exercices')
    page.locator('.exercise-row', has_text='Deadlift fab').first.locator('.cycle-active-badge').click(); page.wait_for_timeout(300)
def modal(page):
    return {'visible': page.is_visible('#confirm-modal-overlay'), 'message': page.inner_text('#confirm-modal-message'),
            'confirm': page.text_content('#confirm-modal-confirm'), 'cancel': page.text_content('#confirm-modal-cancel'),
            'cancel_visible': page.is_visible('#confirm-modal-cancel'),
            'items': page.locator('#confirm-modal-details .modal-details-list li').all_inner_texts()}
def swap(page): page.click('#cycle-end-swap-btn'); page.wait_for_timeout(200); return modal(page)
def confirm(page): page.click('#confirm-modal-confirm'); page.wait_for_timeout(400)
def break_key(key, after=0):
    return """() => { const orig = Storage.prototype.setItem; let n = 0; Storage.prototype.setItem = function (k, v) {
  if (k === '%s' && ++n > %d) throw new DOMException('quota', 'QuotaExceededError'); return orig.call(this, k, v); }; }""" % (key, after)

DL, PC, BS, NO, FU, MU, OA, ZS, FX = 'ex-dl', 'ex-pc', 'ex-bs', 'ex-no', 'ex-fu', 'ex-mu', 'ex-oa', 'ex-zs', 'ex-fx'
def full_pool():
    """Deadlift terminé dans deux routines ; seul Power Clean est éligible."""
    exercises = [ex(DL, 'Deadlift fab', 100), ex(PC, 'Power Clean fab', 70), ex(BS, 'Back Squat fab', 120), ex(NO, 'Sans 1RM fab', None),
                 ex(FU, 'Futur fab', 90, start='2099-01-01'), ex(MU, 'Presse fab', 150, 'Jambes'), ex(OA, 'Orphelin actif fab', 60)]
    rts = [routine('r-a', 'Force fab', [rex(BS), rex(DL, 3, 80, 180, groupId='g1', groupType='superset', grip='pronation'), rex(MU)]),
           routine('r-b', 'Force fab (indé)', [rex(DL, 2, 60, 150), rex(BS)])]
    cyc = {DL: pending(DL, 100, 110), BS: active(BS, 120), OA: active(OA, 60, 'B', 3)}
    return dataset(exercises, rts, cyc)

with sync_playwright() as p:
    b = p.chromium.launch()

    # F0 : ouverture de l'écran, quatre commandes inchangées, bloc présent, aucune écriture ; Annuler sans écriture
    ctx, page, errors = fresh(b, full_pool())
    before = ls(page)
    open_end(page)
    body = page.text_content('#cycle-end-body')
    check(all(t in body for t in ['Relancer', 'Garder ce cycle', 'Choisir moi même', 'Lancer ce cycle', 'CHANGER DE MOUVEMENT'])
          and page.is_visible('#cycle-end-swap-btn') and page.text_content('#cycle-end-swap-btn') == 'Tirer un autre mouvement' and ls(page) == before,
          'F0 écran de fin : quatre commandes, bloc "Changer de mouvement", aucune écriture à l\'ouverture')
    check(page.locator('.cycle-end-launch-btn').count() == 1, 'F0 mouvement du programme : "Lancer ce cycle" présent')
    m = swap(page)
    g = MSG_RE.match(m['message'])
    check(g and g.group(1) == 'Power Clean fab' and g.group(2) == '« Force fab » et « Force fab (indé) »' and g.group(3) == 'Power Clean fab'
          and m['confirm'] == 'Confirmer' and m['cancel'] == 'Annuler' and m['cancel_visible'],
          'F1 confirmation : seul Power Clean tiré (sans 1RM, date future, cycle actif, muscu, cycle en cours hors programme exclus), deux routines nommées : %s' % m['message'])
    page.click('#confirm-modal-cancel'); page.wait_for_timeout(200)
    check(ls(page) == before and not errors, 'F1 Annuler : aucune écriture')
    m = swap(page); g = MSG_RE.match(m['message']); n = g.group(4); cyc = LETTERS.get(n, n)
    old = {'r': json.loads(before['ovryk.routines']), 'c': json.loads(before['ovryk.forceCycles'])}
    page.evaluate("() => { const b = document.getElementById('confirm-modal-confirm'); b.click(); b.click(); }"); page.wait_for_timeout(400)
    r = routines(page); c = cycles(page); e = exs(page)
    exp_a = [old['r'][0]['exercises'][0], dict(old['r'][0]['exercises'][1], exerciseId=PC, grip=None), old['r'][0]['exercises'][2]]
    exp_b = [dict(old['r'][1]['exercises'][0], exerciseId=PC, grip=None), old['r'][1]['exercises'][1]]
    check(r[0]['exercises'] == exp_a and r[1]['exercises'] == exp_b and r[0]['updatedAt'] == old['r'][0]['updatedAt'] and r[1]['updatedAt'] == old['r'][1]['updatedAt'],
          'F1 deux routines remplacées à la même place : séries, repos, groupId, groupType conservés, prise remise à null, updatedAt inchangé (R5)')
    check(g.group(5) == '70', 'F1 la confirmation affiche le 1RM utilisé (%s kg)' % g.group(5))
    check(sorted(c) == sorted([DL, PC, BS, OA]) and c[DL] == old['c'][DL] and c[BS] == old['c'][BS] and c[OA] == old['c'][OA]
          and c[PC]['cycle_actif'] == cyc and cyc != 'C' and c[PC]['semaine_actuelle'] == 1 and c[PC]['one_rm_actuel'] == 70
          and not c[PC]['en_attente_de_validation'] and c[PC]['historique_cycles'] == [],
          'F1 cycle %s semaine 1 créé pour Power Clean (1RM 70), entrée de Deadlift intacte (en attente, historique), autres cycles intacts' % n)
    check(e[DL]['oneRepMax'] == 110 and page.is_hidden('#cycle-end-page') and not errors,
          'F1 1RM validé 110 recopié sur Deadlift, écran fermé, double tap sans second effet (%s)' % errors[:1])
    after = data(page)
    page.reload(); page.wait_for_timeout(500)
    check(data(page) == after, 'F1 rechargement (activation automatique au démarrage) : aucun second cycle, rien de changé')
    nav(page, 'exercices'); page.click('#exercises-activate-cycles-btn'); page.wait_for_timeout(300)
    box = page.inner_text('#activate-cycles-orphans') if page.is_visible('#activate-cycles-orphans') else ''
    page.click('#activate-cycles-orphans-btn'); page.wait_for_timeout(200); m = modal(page)
    check('Deadlift fab' in box and m['message'] == 'Supprimer les cycles hors programme ?' and m['items'] == ['Deadlift fab, cycle 15, semaine 6 sur 6.', 'Orphelin actif fab, cycle 14, semaine 3 sur 6.'],
          'F2 "Supprimer les cycles hors programme" propose Deadlift (et l\'orphelin actif fabriqué) avec le texte habituel : %s' % m['items'])
    page.click('#confirm-modal-cancel'); page.wait_for_timeout(200)
    check(DL in cycles(page) and data(page) == after, 'F2 rien supprimé sans confirmation')
    ctx.close()

    # F3 : pool vide : message exact, rien n'est créé
    d = dataset([ex(DL, 'Deadlift fab', 100), ex(NO, 'Sans 1RM fab', None), ex(FU, 'Futur fab', 90, start='2099-01-01')],
                [routine('r-a', 'Force fab', [DL])], {DL: pending(DL, 100, 110)})
    ctx, page, errors = fresh(b, d)
    before = ls(page)
    open_end(page); m = swap(page)
    check(m['message'] == EMPTY and m['confirm'] == 'Compris' and not m['cancel_visible'], 'F3 pool vide : message exact')
    confirm(page)
    check(ls(page) == before and not errors, 'F3 rien n\'est créé ni écrit')
    ctx.close()

    # F4 : ancien mouvement terminé, en attente et hors programme : éligible, son entrée et son historique sont repris
    d = dataset([ex(DL, 'Deadlift fab', 100), ex(ZS, 'Zercher fab', 90)], [routine('r-a', 'Force fab', [DL])],
                {DL: pending(DL, 100, 110), ZS: pending(ZS, 80, 90, 'A', 'B')})
    ctx, page, errors = fresh(b, d)
    old_z = cycles(page)[ZS]
    open_end(page); m = swap(page); g = MSG_RE.match(m['message'])
    check(g and g.group(1) == 'Zercher fab', 'F4 Zercher (en attente, hors programme) éligible : %s' % m['message'])
    cyc = LETTERS.get(g.group(4), g.group(4)); confirm(page)
    z = cycles(page)[ZS]
    check(z['historique_cycles'] == old_z['historique_cycles'] and z['historique_1rm'][:-1] == old_z['historique_1rm']
          and len(z['historique_1rm']) == len(old_z['historique_1rm']) + 1 and z['historique_1rm'][-1]['valeur'] == 90 and g.group(5) == '90' and z['one_rm_actuel'] == 90
          and z['cycle_actif'] == cyc and cyc != 'C' and z['semaine_actuelle'] == 1 and not z['en_attente_de_validation'] and z['prochain_cycle'] is None
          and [x['exerciseId'] for x in routines(page)[0]['exercises']] == [ZS] and not errors,
          'F4 entrée de Zercher reprise (1RM identique) : historiques conservés, point de départ daté ajouté, cycle %s semaine 1, routine remplacée' % g.group(4))
    ctx.close()

    # F4b : 1RM de l'exercice (95) différent de celui de l'ancienne entrée (90) : la saisie à la main prime
    d = dataset([ex(DL, 'Deadlift fab', 100), ex(ZS, 'Zercher fab', 95)], [routine('r-a', 'Force fab', [DL])],
                {DL: pending(DL, 100, 110), ZS: pending(ZS, 80, 90, 'A', 'B')})
    ctx, page, errors = fresh(b, d)
    old_z = cycles(page)[ZS]
    open_end(page); m = swap(page); g = MSG_RE.match(m['message'])
    check(g and g.group(1) == 'Zercher fab' and g.group(5) == '95', 'F4b la confirmation affiche le 1RM de l\'exercice (95), pas celui de l\'ancienne entrée (90) : %s' % m['message'])
    confirm(page)
    z = cycles(page)[ZS]
    check(z['one_rm_actuel'] == 95 and z['historique_1rm'][:-1] == old_z['historique_1rm'] and z['historique_1rm'][-1]['valeur'] == 95
          and z['historique_cycles'] == old_z['historique_cycles'] and z['semaine_actuelle'] == 1 and not z['en_attente_de_validation']
          and exs(page)[ZS]['oneRepMax'] == 95 and not errors,
          'F4b cycle relancé à 95 kg : historique_1rm = ancien + point à 95, historique_cycles intact, 1RM de l\'exercice inchangé (%s)' % errors[:1])
    ctx.close()

    # F4c : 1RM de l'exercice absent : jamais tiré (décision 3), pool vide, rien n'est écrit
    d = dataset([ex(DL, 'Deadlift fab', 100), ex(ZS, 'Zercher fab', None)], [routine('r-a', 'Force fab', [DL])],
                {DL: pending(DL, 100, 110), ZS: pending(ZS, 80, 90, 'A', 'B')})
    ctx, page, errors = fresh(b, d)
    before = ls(page)
    open_end(page); m = swap(page); confirm(page)
    check(m['message'] == EMPTY and ls(page) == before and not errors, 'F4c entrée en attente sans 1RM sur l\'exercice : exclue du pool, message de pool vide, rien n\'est écrit')
    ctx.close()

    # F5 : écriture des routines en échec : forceCycles remis depuis la copie, message, routines intactes
    ctx, page, errors = fresh(b, full_pool())
    before = data(page)
    open_end(page); swap(page); page.evaluate(break_key('ovryk.routines')); confirm(page); m = modal(page)
    e = exs(page)
    check(m['message'] == KEPT + ONERM and m['confirm'] == 'Compris' and ls(page)['ovryk.routines'] == before['ovryk.routines']
          and ls(page)['ovryk.forceCycles'] == before['ovryk.forceCycles'] and e[DL]['oneRepMax'] == 110 and not errors,
          'F5 routines en échec : message exact avec la mention du 1RM déjà recopié, routines et forceCycles identiques octet pour octet (%s)' % m['message'])
    ctx.close()

    # F6 : routines en échec ET remise de forceCycles en échec : message clair, nouveau cycle hors programme
    ctx, page, errors = fresh(b, full_pool())
    before = data(page)
    open_end(page); swap(page)
    page.evaluate(break_key('ovryk.routines')); page.evaluate(break_key('ovryk.forceCycles', 1)); confirm(page); m = modal(page)
    check(m['message'].startswith(FAIL + "Tes routines n'ont pas changé. Le cycle de Power Clean fab a été lancé") and m['message'].endswith(ONERM)
          and ls(page)['ovryk.routines'] == before['ovryk.routines'] and PC in cycles(page) and not errors,
          'F6 remise en échec : message clair, routines intactes, cycle de Power Clean hors programme (%s)' % m['message'])
    ctx.close()

    # F7 : écriture du cycle en échec : rien n'a changé
    ctx, page, errors = fresh(b, full_pool())
    before = data(page)
    open_end(page); swap(page); page.evaluate(break_key('ovryk.forceCycles')); confirm(page); m = modal(page)
    check(m['message'] == KEPT + ONERM and ls(page)['ovryk.routines'] == before['ovryk.routines'] and ls(page)['ovryk.forceCycles'] == before['ovryk.forceCycles'] and not errors,
          'F7 cycle en échec : message exact avec la mention du 1RM, routines et forceCycles intacts')
    ctx.close()

    # F5b : le 1RM de l'exercice vaut déjà 110 (rien à recopier) : le message ne mentionne aucun 1RM
    d = full_pool(); d['exercises'][0]['oneRepMax'] = 110
    ctx, page, errors = fresh(b, d)
    before = data(page)
    open_end(page); swap(page); page.evaluate(break_key('ovryk.routines')); confirm(page); m = modal(page)
    check(m['message'] == KEPT and data(page) == before and not errors,
          'F5b routines en échec sans recopie du 1RM : message sans mention du 1RM, toutes les données identiques octet pour octet (%s)' % m['message'])
    ctx.close()

    # F5c : la sauvegarde du jour de forceCycles échoue avant toute écriture : rien n'est écrit, pas de mention du 1RM
    ctx, page, errors = fresh(b, full_pool())
    before = data(page)
    open_end(page); swap(page)
    page.evaluate("() => { Object.keys(localStorage).filter(k => k.indexOf('ovryk.backup.forceCycles.') === 0).forEach(k => localStorage.removeItem(k)); }")
    before = data(page)
    page.evaluate("""() => { const orig = Storage.prototype.setItem; Storage.prototype.setItem = function (k, v) {
      if (k.indexOf('ovryk.backup.forceCycles.') === 0) throw new DOMException('quota', 'QuotaExceededError'); return orig.call(this, k, v); }; }""")
    confirm(page); m = modal(page)
    check(m['message'] == KEPT and data(page) == before and exs(page)[DL]['oneRepMax'] == 100 and not errors,
          'F5c sauvegarde du jour en échec : message sans mention du 1RM, 1RM non recopié, données identiques (%s)' % m['message'])
    ctx.close()

    # F8 : R7 : seuil lourd 0, 1 cycle lourd par semaine, un cycle fixe dans le programme en semaine 1 de A : Power Clean décalé de 6
    d = dataset([ex(DL, 'Deadlift fab', 100), ex(PC, 'Power Clean fab', 70), ex(FX, 'Fixe fab', 120)],
                [routine('r-a', 'Force fab', [DL]), routine('r-f', 'Fixe fab r', [FX])], {DL: pending(DL, 100, 110), FX: active(FX, 120, 'A', 1)},
                {'heavyThreshold': 0, 'maxHeavyCyclesPerWeek': 1})
    ctx, page, errors = fresh(b, d)
    open_end(page); swap(page); confirm(page)
    c = cycles(page)
    check(c[PC]['decalage_semaines'] == 6 and c[FX] == d['forceCycles'][FX] and not errors,
          'F8 R7 : Power Clean coordonné contre le cycle fixe (décalage %s), cycle fixe inchangé' % c[PC]['decalage_semaines'])
    ctx.close()

    # F9 : séance en cours au moment du remplacement : séance intacte, aucune erreur, fin de séance sans avancer Power Clean
    ctx, page, errors = fresh(b, full_pool())
    nav(page, 'seance'); page.locator('#seance-routine-list .routine-row-main', has_text='Force fab').first.click(); page.wait_for_timeout(700)
    live0 = [x for x in json.loads(ls(page)['ovryk.sessions']) if x['status'] == 'in_progress'][0]
    open_end(page); swap(page); confirm(page)
    live1 = [x for x in json.loads(ls(page)['ovryk.sessions']) if x['status'] == 'in_progress'][0]
    nav(page, 'seance')
    page.locator('.live-card.is-open button.live-set-circle').first.click(); page.wait_for_timeout(300)
    page.click('#seance-finish-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(800)
    c = cycles(page)
    check(live1['exercises'] == live0['exercises'] and c[PC]['semaine_actuelle'] == 1 and c[DL]['en_attente_de_validation'] and not errors,
          'F9 séance en cours : cartes inchangées par le remplacement, séance terminée, Power Clean en semaine 1, Deadlift toujours en attente (%s)' % errors[:1])
    ctx.close()

    # F10 : "Lancer ce cycle" inchangé : même mouvement, routines inchangées
    ctx, page, errors = fresh(b, full_pool())
    before = data(page)
    open_end(page); page.click('.cycle-end-launch-btn'); page.wait_for_timeout(400)
    c = cycles(page)
    check(c[DL]['cycle_actif'] == 'D' and c[DL]['semaine_actuelle'] == 1 and not c[DL]['en_attente_de_validation'] and PC not in c
          and ls(page)['ovryk.routines'] == before['ovryk.routines'] and not errors, 'F10 "Lancer ce cycle" : Deadlift relancé en cycle 16, routines inchangées')
    ctx.close()

    # F11 : mouvement terminé dans aucune routine : pas de bloc (rien à remplacer)
    d = dataset([ex(DL, 'Deadlift fab', 100), ex(PC, 'Power Clean fab', 70)], [], {DL: pending(DL, 100, 110)})
    ctx, page, errors = fresh(b, d)
    open_end(page)
    check(page.locator('#cycle-end-swap-btn').count() == 0 and 'CHANGER DE MOUVEMENT' not in page.inner_text('#cycle-end-body') and not errors,
          'F11 mouvement hors programme : bloc absent')
    # F12 : « Lancer ce cycle » masqué hors programme, les trois autres commandes restent
    body = page.text_content('#cycle-end-body')
    check(page.locator('.cycle-end-launch-btn').count() == 0 and 'Lancer ce cycle' not in body
          and all(t in body for t in ['Relancer', 'Garder ce cycle', 'Choisir moi même']), 'F12 hors programme : "Lancer ce cycle" masqué, Relancer / Garder / Choisir présents')
    ctx.close()

    # G1 (R5) : la routine contient Deadlift et Presse, séance précédente de Presse à 150 kg : après le remplacement de
    # Deadlift, la séance suivante reprend 150 kg pour la Presse (updatedAt non touché), et le créneau remplacé suit son cycle
    def prev_session():
        sets = [{'repType': 'range', 'repsMin': 8, 'repsMax': 10, 'weightKg': 150, 'repsActual': 9, 'done': True} for _ in range(3)]
        return {'id': 's-prev', 'status': 'completed', 'date': '2026-09-20T10:00:00.000Z', 'startedAt': '2026-09-20T10:00:00.000Z',
                'completedAt': '2026-09-20T11:00:00.000Z', 'durationSeconds': 3600, 'routineId': 'r-a', 'routineName': 'Force fab', 'notes': '',
                'exercises': [{'id': 'sex-prev-0', 'exerciseId': MU, 'exerciseName': 'Presse fab', 'category': 'Jambes', 'restSeconds': 90,
                               'sets': sets, 'groupId': None, 'groupType': None}]}
    d = dataset([ex(DL, 'Deadlift fab', 100), ex(PC, 'Power Clean fab', 70), ex(MU, 'Presse fab', 150, 'Jambes')],
                [routine('r-a', 'Force fab', [rex(DL), rex(MU, 3, 40)])], {DL: pending(DL, 100, 110)})
    d['sessions'] = [prev_session()]
    ctx, page, errors = fresh(b, d)
    open_end(page); swap(page); confirm(page)
    r = routines(page)
    nav(page, 'seance'); page.locator('#seance-routine-list .routine-row-main', has_text='Force fab').first.click(); page.wait_for_timeout(700)
    lv = [x for x in json.loads(ls(page)['ovryk.sessions']) if x['status'] == 'in_progress'][0]
    pc_card = [x for x in lv['exercises'] if x['exerciseId'] == PC][0]
    mu_card = [x for x in lv['exercises'] if x['exerciseId'] == MU][0]
    check(r[0]['updatedAt'] == '2026-09-01T00:00:00.000Z' and [x['exerciseId'] for x in r[0]['exercises']] == [PC, MU]
          and len(mu_card['sets']) == 3 and all(st['weightKg'] == 150 for st in mu_card['sets']) and not errors,
          'G1 séance suivante après remplacement : Presse reprend ses 150 kg (%s), updatedAt inchangé (%s)' % ([st['weightKg'] for st in mu_card['sets']], r[0]['updatedAt']))
    check(pc_card['cycleIdUsed'] is not None and pc_card['cycleWeekUsed'] == 1 and pc_card['oneRepMaxSnapshot'] == 70,
          'G1 le créneau remplacé suit le cycle de Power Clean (cycle %s, semaine %s, 1RM figé %s)' % (pc_card['cycleIdUsed'], pc_card['cycleWeekUsed'], pc_card['oneRepMaxSnapshot']))
    ctx.close()

    # E1 / E2 : éditeur de routine ouvert sur une routine qui contient le mouvement terminé ; on remplace depuis l'écran
    # de fin de cycle (ouvert par le clic du bandeau, en JS : l'éditeur plein écran le recouvre), puis on agit dans
    # l'éditeur et on l'enregistre. Le nouveau mouvement reste, l'ancien ne revient pas.
    def open_editor_then_swap(page):
        nav(page, 'routine')
        page.locator('.routine-row', has_text='Force fab').first.locator('.routine-row-main').click(); page.wait_for_timeout(400)
        page.evaluate("() => document.getElementById('cycle-alert-banner').click()"); page.wait_for_timeout(300)
        page.evaluate("() => document.getElementById('cycle-end-swap-btn').click()"); page.wait_for_timeout(200)
        confirm(page)
    def editor_names(page): return page.locator('#routine-editor-view .routine-exercise-block').count(), \
        page.locator('#routine-editor-view .routine-exercise-block', has_text='Deadlift fab').count(), \
        page.locator('#routine-editor-view .routine-exercise-block', has_text='Power Clean fab').count()

    ctx, page, errors = fresh(b, full_pool())
    open_editor_then_swap(page)
    total, n_dl, n_pc = editor_names(page)
    check(page.is_visible('#routine-editor-view') and n_dl == 0 and n_pc == 1 and total == 3,
          'E1 éditeur ouvert pendant le remplacement : il affiche Power Clean et plus Deadlift (%d blocs, Deadlift %d, Power Clean %d)' % (total, n_dl, n_pc))
    page.locator('#routine-editor-view .routine-exercise-block', has_text='Back Squat fab').first.locator('.rex-remove-btn').click(); page.wait_for_timeout(300)
    page.click('#routine-save-btn'); page.wait_for_timeout(400)
    r = routines(page)
    ids_a = [x['exerciseId'] for x in r[0]['exercises']]
    ids_b = [x['exerciseId'] for x in r[1]['exercises']]
    check(ids_a == [PC, MU] and ids_b == [PC, BS] and r[0]['exercises'][0]['restSeconds'] == 180 and r[0]['exercises'][0].get('groupId') == 'g1'
          and page.is_hidden('#routine-editor-view') and PC in cycles(page) and not errors,
          'E1 retrait d\'une autre ligne puis Enregistrer : Power Clean toujours là, Deadlift pas revenu (%s / %s) (%s)' % (ids_a, ids_b, errors[:1]))
    ctx.close()

    ctx, page, errors = fresh(b, full_pool())
    open_editor_then_swap(page)
    page.fill('#routine-name-input', 'Force renommée fab'); page.dispatch_event('#routine-name-input', 'change'); page.wait_for_timeout(300)
    page.click('#routine-save-btn-bottom'); page.wait_for_timeout(400)
    r = routines(page)
    check([x['exerciseId'] for x in r[0]['exercises']] == [BS, PC, MU] and r[0]['name'] == 'Force renommée fab'
          and [x['exerciseId'] for x in r[1]['exercises']] == [PC, BS] and page.is_hidden('#routine-editor-view') and not errors,
          'E2 renommage puis Enregistrer : nom pris, Power Clean toujours là, Deadlift pas revenu (%s)' % errors[:1])
    ctx.close()

    b.close()

print('\n%d/%d' % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
