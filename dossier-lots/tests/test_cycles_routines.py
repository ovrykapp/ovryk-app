"""Cycles liés au programme, livraison 1 : confirmation de suppression de
routine (nom, cycles supprimés avec elle, texte exact, bouton "Supprimer",
double tap) et règle A (recopie du dernier 1RM validé dans
exercise.oneRepMax avant la suppression du cycle).
Données FABRIQUÉES ici : aucun vrai export, aucun appel réseau.
Usage : python3 test_cycles_routines.py <dossier de travail>, site servi sur http://127.0.0.1:8765."""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
SP = Path(sys.argv[1]); URL = 'http://127.0.0.1:8765/index.html'
SP.mkdir(parents=True, exist_ok=True)
res = []
def check(c, m): res.append(bool(c)); print(('ok     ' if c else 'ECHEC  ') + m)
DATA_KEYS = ['ovryk.exercises', 'ovryk.routines', 'ovryk.sessions', 'ovryk.settings', 'ovryk.forceCycles', 'ovryk.meta']
NOTE_N = "L'historique de ces cycles sera effacé."
NOTE_1 = "L'historique de ce cycle sera effacé."
STILL = 'Ce mouvement est encore dans une routine : un nouveau cycle démarrera à partir de son 1RM.'
def fail_msg(name, kept_text):
    return ('Le 1RM validé de « %s » n\'a pas pu être enregistré (stockage plein ou indisponible). Rien n\'a été supprimé : %s' % (name, kept_text))
# échec d'écriture simulé : toute écriture de ovryk.exercises lève QuotaExceededError (writeJSON la rattrape et renvoie false)
BREAK_EXERCISES = """() => { const orig = Storage.prototype.setItem; Storage.prototype.setItem = function (k, v) {
  if (k === 'ovryk.exercises') throw new DOMException('quota', 'QuotaExceededError'); return orig.call(this, k, v); }; }"""
def kept(kg): return ". 1RM validé de %s kg conservé sur l'exercice." % str(kg).replace('.', ',')

# ---------- fixtures fabriquées ----------
def ex(eid, name, orm=None, cat='Lifting'):
    return {'id': eid, 'name': name, 'category': cat, 'equipment': 'Barre', 'unit': 'kg', 'isCustom': True,
            'oneRepMax': orm, 'liftBaseMode': 'force'}
def cycle(eid, start, current, tested, cyc='D', week=2):
    hist = [{'date': '2026-08-01T10:00:00.000Z', 'valeur': start}]
    hcyc = []
    if tested:
        hist.append({'date': '2026-09-12T10:00:00.000Z', 'valeur': current})
        hcyc.append({'cycle': 'C', 'debut': '2026-08-01T10:00:00.000Z', 'fin': '2026-09-12T10:00:00.000Z', 'seances': 6,
                     'seances_prevues': 6, 'reussite_pct': 90, 'one_rm_avant': start, 'one_rm_apres': current})
    return {'exercise_id': eid, 'cycle_actif': cyc, 'one_rm_actuel': current, 'semaine_actuelle': week,
            'historique_1rm': hist, 'historique_cycles': hcyc, 'prochain_cycle': None, 'en_attente_de_validation': False,
            'semaines_modifiees': {}, 'test_report_used': False, 'decalage_semaines': 0}
def rex(eid): return {'exerciseId': eid, 'restSeconds': 120, 'sets': [{'reps': 5, 'weight': 0}]}
def routine(rid, name, eids): return {'id': rid, 'name': name, 'weekdays': [], 'updatedAt': '2026-09-01T00:00:00.000Z',
                                      'createdAt': '2026-09-01T00:00:00.000Z', 'exercises': [rex(e) for e in eids]}
def dataset(exercises, routines, cycles):
    return {'exercises': exercises, 'routines': routines, 'sessions': [],
            'settings': {'unit': 'kg', 'restTimerSeconds': 90, 'lastExportAt': None},
            'forceCycles': cycles, 'meta': {'schemaVersion': 2}}

def ls(page): return page.evaluate("() => { const o = {}; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); o[k] = localStorage.getItem(k); } return o; }")
def data(page): return {k: v for k, v in ls(page).items() if k in DATA_KEYS}
def jset(page, key, value): page.evaluate("([k, v]) => localStorage.setItem(k, v)", [key, json.dumps(value)])
def exs(page): return {e['id']: e for e in json.loads(ls(page)['ovryk.exercises'])}
def cycles(page): return json.loads(ls(page)['ovryk.forceCycles'])
def routines(page): return json.loads(ls(page)['ovryk.routines'])
def fresh(b, d):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    page = ctx.new_page(); errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(URL); page.evaluate("() => localStorage.clear()")
    for k, v in d.items(): jset(page, 'ovryk.' + k, v)
    page.reload(); page.wait_for_timeout(300); page.reload(); page.wait_for_timeout(300)
    return ctx, page, errors
def programme(page):
    page.click('.nav-btn[data-target="routine"]'); page.wait_for_timeout(300)
def open_delete(page, name):
    page.locator('.routine-row', has_text=name).first.locator('.routine-action-btn.danger').click(); page.wait_for_timeout(200)
def modal(page):
    return {'visible': page.is_visible('#confirm-modal-overlay'),
            'message': page.inner_text('#confirm-modal-message'),
            'items': page.locator('#confirm-modal-details .modal-details-list li').all_inner_texts(),
            'note': (page.locator('#confirm-modal-details .modal-details-note').all_inner_texts() or [''])[0],
            'notes': page.locator('#confirm-modal-details .modal-details-note').all_inner_texts(),
            'cancel_visible': page.is_visible('#confirm-modal-cancel'),
            # textContent : le texte écrit par l'app, avant la mise en majuscules du CSS
            'confirm': page.text_content('#confirm-modal-confirm'), 'cancel': page.text_content('#confirm-modal-cancel')}
def delete_routine(b, d, name):
    """ouvre Programme, supprime la routine, renvoie (page, ctx, errors) après suppression"""
    ctx, page, errors = fresh(b, d)
    programme(page); open_delete(page, name); page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    return ctx, page, errors

with sync_playwright() as p:
    b = p.chromium.launch()

    BS, DL, ZS = 'ex-bs', 'ex-dl', 'ex-zs'
    base_ex = [ex(BS, 'Back Squat fab', 100), ex(DL, 'Deadlift fab', 130), ex(ZS, 'Zercher fab', 80)]

    # C0 : aucune écriture au lancement, à l'ouverture de Programme ni à l'ouverture puis Annuler de la confirmation
    d = dataset(base_ex, [routine('r-a', 'Jambes fab', [BS, DL])], {BS: cycle(BS, 100, 110, True), DL: cycle(DL, 130, 130, False, 'C', 3)})
    ctx, page, errors = fresh(b, d)
    before = ls(page)
    page.reload(); page.wait_for_timeout(300); programme(page); open_delete(page, 'Jambes fab')
    m = modal(page)
    page.click('#confirm-modal-cancel'); page.wait_for_timeout(200)
    check(ls(page) == before and not errors and page.is_hidden('#confirm-modal-overlay'),
          'C0 lancement, Programme, confirmation puis Annuler : aucune écriture, aucune erreur (%s)' % errors[:1])

    # C1 : texte exact de la confirmation avec cycles concernés
    check(m['visible'] and m['message'] == 'Supprimer la routine « Jambes fab » ?', 'C1 question : "%s"' % m['message'])
    check(m['items'] == ['Back Squat fab, cycle 16, semaine 2 sur 6' + kept(110), 'Deadlift fab, cycle 15, semaine 3 sur 6.'],
          'C1 cycles listés, conservation promise seulement pour Back Squat (testé) : %s' % m['items'])
    check(m['note'] == NOTE_N, 'C1 note exacte : "%s"' % m['note'])
    check(m['confirm'] == 'Supprimer' and m['cancel'] == 'Annuler', 'C1 boutons : "%s" / "%s"' % (m['confirm'], m['cancel']))

    # C2 : tap sur la zone autour de la boîte : annule, rien écrit
    open_delete(page, 'Jambes fab')
    page.mouse.click(10, 10); page.wait_for_timeout(200)
    check(page.is_hidden('#confirm-modal-overlay') and ls(page) == before and len(routines(page)) == 1,
          'C2 tap hors de la boîte : fermée, routine et cycles intacts')

    # C3 : double tap sur "Supprimer" : une seule suppression, aucune erreur
    open_delete(page, 'Jambes fab')
    page.evaluate("() => { const b = document.getElementById('confirm-modal-confirm'); b.click(); b.click(); }")
    page.wait_for_timeout(300)
    check(routines(page) == [] and cycles(page) == {} and not errors and page.is_hidden('#confirm-modal-overlay'),
          'C3 double tap : routine supprimée une fois, cycles supprimés, aucune erreur (%s)' % errors[:1])
    # règle A sur C3 : BS testé (100 -> 110, oneRepMax = départ 100) recopié ; DL sans test validé, rien recopié
    e = exs(page)
    check(e[BS]['oneRepMax'] == 110 and e[DL]['oneRepMax'] == 130, 'C3 règle A : Back Squat 110 recopié, Deadlift sans test 130 inchangé (%s, %s)' % (e[BS]['oneRepMax'], e[DL]['oneRepMax']))
    ctx.close()

    # C4 : routine sans cycle : "Aucun cycle concerné.", pas de liste ni de note sur l'historique
    d = dataset(base_ex, [routine('r-b', 'Haut fab', [BS])], {})
    d['exercises'] = [ex(BS, 'Back Squat fab', None)]  # aucun 1RM : aucune activation automatique au démarrage
    ctx, page, errors = fresh(b, d)
    programme(page); open_delete(page, 'Haut fab'); m = modal(page)
    check(m['items'] == [] and m['note'] == 'Aucun cycle concerné.', 'C4 aucun cycle : "%s", liste %s' % (m['note'], m['items']))
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    check(routines(page) == [] and cycles(page) == {} and exs(page)[BS]['oneRepMax'] is None and not errors, 'C4 supprimée, rien d\'autre écrit')
    ctx.close()

    # C5 : 2 routines, exercice dans les deux : son cycle n'est pas listé et reste ; l'autre est listé et supprimé
    d = dataset(base_ex, [routine('r-a', 'Jambes fab', [BS, ZS]), routine('r-c', 'Force fab', [BS])],
                {BS: cycle(BS, 100, 110, True), ZS: cycle(ZS, 80, 90, True, '6', 4)})
    ctx, page, errors = fresh(b, d)
    c_before = cycles(page)[BS]
    programme(page); open_delete(page, 'Jambes fab'); m = modal(page)
    check(m['items'] == ['Zercher fab, cycle 6, semaine 4 sur 8' + kept(90)] and m['note'] == NOTE_1, 'C5 seul Zercher listé : %s / %s' % (m['items'], m['note']))
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    c = cycles(page); e = exs(page)
    check(list(c) == [BS] and c[BS] == c_before and e[BS]['oneRepMax'] == 100,
          'C5 Back Squat (encore dans "Force fab") : cycle identique, oneRepMax non recopié (%s)' % e[BS]['oneRepMax'])
    check(e[ZS]['oneRepMax'] == 90 and [r['name'] for r in routines(page)] == ['Force fab'], 'C5 Zercher supprimé, 90 recopié')
    # puis la dernière routine : le cycle Back Squat part, 110 recopié
    programme(page); open_delete(page, 'Force fab'); m = modal(page)
    check(m['items'] == ['Back Squat fab, cycle 16, semaine 2 sur 6' + kept(110)], 'C5 dernière routine : Back Squat listé %s' % m['items'])
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    check(cycles(page) == {} and exs(page)[BS]['oneRepMax'] == 110 and not errors, 'C5 dernière routine : cycle supprimé, 110 recopié (%s)' % errors[:1])
    ctx.close()

    # C6 : variantes de la règle A, un cas par exercice, une seule routine
    cases = [
        # (id, nom, oneRepMax de l'exercice, départ, one_rm_actuel, testé, attendu, libellé)
        ('ex-v1', 'Vide fab', None, 100, 112.5, True, 112.5, '1RM vide : recopié'),
        ('ex-v2', 'Egal fab', 100, 100, 105, True, 105, '1RM égal au départ : recopié'),
        ('ex-v3', 'Different fab', 120, 100, 105, True, 120, '1RM changé à la main : non écrasé'),
        ('ex-v4', 'Texte fab', '100', 100, 107.5, True, 107.5, '1RM en texte "100" égal au départ : recopié'),
        ('ex-v5', 'Depart texte fab', 100, '100', 102.5, True, 102.5, 'départ en texte "100" : recopié'),
        ('ex-v6', 'Zero fab', 100, 100, 0, True, 100, 'one_rm_actuel à 0 : rien recopié'),
        ('ex-v7', 'Invalide fab', 100, 100, 'abc', True, 100, 'one_rm_actuel invalide : rien recopié'),
        ('ex-v8', 'Nul fab', None, 100, None, True, None, 'one_rm_actuel nul : rien recopié'),
        ('ex-v9', 'Sans test fab', 100, 100, 100, False, 100, 'cycle sans test validé : rien recopié'),
        ('ex-v10', 'Sans test vide fab', None, 100, 100, False, None, 'cycle sans test validé, 1RM vide : rien recopié'),
        ('ex-v11', 'Deja egal fab', 100, 100, 100, True, 100, 'test validé égal au départ : déjà sur l\'exercice, rien écrit'),
    ]
    # promesse attendue dans la confirmation : seulement si le 1RM validé reste sur l'exercice
    promised = {'ex-v1': 112.5, 'ex-v2': 105, 'ex-v4': 107.5, 'ex-v5': 102.5, 'ex-v11': 100}
    exl = [ex(cid, name, orm) for cid, name, orm, *_ in cases]
    cyc = {cid: cycle(cid, start, cur, tested) for cid, name, orm, start, cur, tested, *_ in cases}
    ctx, page, errors = fresh(b, dataset(exl, [routine('r-v', 'Variantes fab', [c[0] for c in cases])], cyc))
    before_ex = exs(page)
    programme(page); open_delete(page, 'Variantes fab'); m = modal(page)
    expected_items = ['%s, cycle 16, semaine 2 sur 6%s' % (name, kept(promised[cid]) if cid in promised else '.') for cid, name, *_r in cases]
    check(m['items'] == expected_items and m['note'] == NOTE_N, 'C6 %d lignes exactes, promesse sur 5 seulement' % len(m['items']))
    if m['items'] != expected_items:
        print('       attendu', expected_items, '\n       obtenu ', m['items'])
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    e = exs(page)
    for cid, name, orm, start, cur, tested, expected, label in cases:
        got = e[cid]['oneRepMax']
        check(got == expected and type(got) == type(expected), 'C6 %s (%r)' % (label, got))
    untouched = [cid for cid, *_r, expected, _l in cases if expected == before_ex[cid]['oneRepMax']]
    same = all(json.dumps(e[cid], sort_keys=True) == json.dumps(before_ex[cid], sort_keys=True) for cid in untouched)
    check(cycles(page) == {} and same and not errors, 'C6 tous les cycles supprimés ; exercices non recopiés identiques octet pour octet (%s)' % errors[:1])
    ctx.close()

    # C7 : seules ovryk.routines, ovryk.forceCycles et ovryk.exercises changent ; dans exercises, seul oneRepMax de l'exercice recopié
    d = dataset(base_ex, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, 110, True)})
    ctx, page, errors = fresh(b, d)
    before = data(page)
    programme(page); open_delete(page, 'Jambes fab'); page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    after = data(page)
    changed_keys = sorted(k for k in DATA_KEYS if before.get(k) != after.get(k))
    old = {x['id']: x for x in json.loads(before['ovryk.exercises'])}; new = exs(page)
    diff = [k for k in new if json.dumps(new[k], sort_keys=True) != json.dumps(old.get(k), sort_keys=True)]
    only_orm = {k: v for k, v in new[BS].items() if k != 'oneRepMax'} == {k: v for k, v in old[BS].items() if k != 'oneRepMax'}
    check(changed_keys == ['ovryk.exercises', 'ovryk.forceCycles', 'ovryk.routines'] and diff == [BS] and only_orm,
          'C7 clés modifiées %s, exercices modifiés %s, seul oneRepMax' % (changed_keys, diff))
    ctx.close()

    # ---------- bouton × de l'éditeur de routine ----------
    def editor(page, name):
        programme(page); page.locator('.routine-row', has_text=name).first.locator('.routine-row-main').click(); page.wait_for_timeout(300)
    def cross(page, name):
        page.locator('.routine-exercise-block', has_text=name).first.locator('.rex-remove-btn').click(); page.wait_for_timeout(200)
    def rt_ids(page, rid): return [x['exerciseId'] for x in [r for r in routines(page) if r['id'] == rid][0]['exercises']]

    # C8 : × avec test validé : confirmation exacte ; Annuler et tap hors boîte n'écrivent rien ; Supprimer recopie
    d = dataset(base_ex, [routine('r-a', 'Jambes fab', [BS, DL])], {BS: cycle(BS, 100, 110, True), DL: cycle(DL, 130, 130, False, 'C', 3)})
    ctx, page, errors = fresh(b, d)
    before = ls(page)
    editor(page, 'Jambes fab'); cross(page, 'Back Squat fab'); m = modal(page)
    check(ls(page) == before, 'C8 ouverture de l\'éditeur et de la confirmation du × : aucune écriture')
    check(m['message'] == 'Retirer « Back Squat fab » de la routine ?' and m['items'] == ['Back Squat fab, cycle 16, semaine 2 sur 6' + kept(110)]
          and m['note'] == NOTE_1 and m['confirm'] == 'Supprimer' and m['cancel'] == 'Annuler', 'C8 × testé, texte exact : %s' % m)
    page.click('#confirm-modal-cancel'); page.wait_for_timeout(200)
    cross(page, 'Back Squat fab'); page.mouse.click(10, 10); page.wait_for_timeout(200)
    check(ls(page) == before, 'C8 Annuler puis tap hors boîte : rien écrit')
    cross(page, 'Back Squat fab')
    page.evaluate("() => { const b = document.getElementById('confirm-modal-confirm'); b.click(); b.click(); }"); page.wait_for_timeout(300)
    check(rt_ids(page, 'r-a') == [DL] and list(cycles(page)) == [DL] and exs(page)[BS]['oneRepMax'] == 110 and not errors,
          'C8 Supprimer (double tap) : Back Squat retiré une fois, cycle supprimé, 110 recopié (%s)' % errors[:1])

    # C9 : × sans test validé : pas de promesse, rien recopié
    cross(page, 'Deadlift fab'); m = modal(page)
    check(m['items'] == ['Deadlift fab, cycle 15, semaine 3 sur 6.'] and m['note'] == NOTE_1, 'C9 × sans test : %s' % m['items'])
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    check(rt_ids(page, 'r-a') == [] and cycles(page) == {} and exs(page)[DL]['oneRepMax'] == 130 and not errors, 'C9 retiré, cycle supprimé, 130 inchangé')
    ctx.close()

    # C10 : × avec 1RM changé à la main (120, départ 100) : pas de promesse, non écrasé
    d = dataset([ex(BS, 'Back Squat fab', 120)], [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, 110, True)})
    ctx, page, errors = fresh(b, d)
    editor(page, 'Jambes fab'); cross(page, 'Back Squat fab'); m = modal(page)
    check(m['items'] == ['Back Squat fab, cycle 16, semaine 2 sur 6.'], 'C10 × 1RM changé à la main : %s' % m['items'])
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    check(cycles(page) == {} and exs(page)[BS]['oneRepMax'] == 120 and not errors, 'C10 cycle supprimé, 120 non écrasé')
    ctx.close()

    # C11 : × d'un exercice encore présent ailleurs (autre routine, puis deux fois dans la même) : aucune confirmation, cycle intact
    d = dataset(base_ex, [routine('r-a', 'Jambes fab', [BS, BS]), routine('r-c', 'Force fab', [DL])],
                {BS: cycle(BS, 100, 110, True)})
    ctx, page, errors = fresh(b, d)
    c_before = cycles(page)
    editor(page, 'Jambes fab'); cross(page, 'Back Squat fab')
    check(page.is_hidden('#confirm-modal-overlay') and rt_ids(page, 'r-a') == [BS] and cycles(page) == c_before and exs(page)[BS]['oneRepMax'] == 100,
          'C11 × d\'une entrée en double : retrait direct, cycle et 1RM intacts')
    ctx.close()

    # C12 : "Désactiver le cycle" : texte exact, 1RM validé recopié ; l'activation automatique existante peut relancer un cycle neuf depuis ce 1RM
    d = dataset(base_ex, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, 110, True)})
    ctx, page, errors = fresh(b, d)
    before = ls(page)
    page.click('.nav-btn[data-target="exercices"]'); page.wait_for_timeout(250)
    page.locator('.exercise-row', has_text='Back Squat fab').first.locator('.cycle-active-badge').click(); page.wait_for_timeout(300)
    page.click('.cycle-full-deactivate'); page.wait_for_timeout(200); m = modal(page)
    check(ls(page) == before, 'C12 ouverture du cycle et de la confirmation : aucune écriture')
    check(m['message'] == 'Désactiver le cycle de force de « Back Squat fab » ?' and m['items'] == ['Back Squat fab, cycle 16, semaine 2 sur 6' + kept(110)]
          and m['notes'] == [NOTE_1, STILL] and m['confirm'] == 'Désactiver' and m['cancel'] == 'Annuler', 'C12 texte exact, ligne "encore dans une routine" : %s' % m)
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    c = cycles(page).get(BS)
    check(exs(page)[BS]['oneRepMax'] == 110 and (c is None or (c['historique_cycles'] == [] and c['one_rm_actuel'] == 110)) and not errors,
          'C12 1RM 110 recopié, ancien cycle effacé (%s)' % ('aucun cycle' if c is None else 'cycle neuf à 110'))
    ctx.close()

    # C13 : "Désactiver le cycle" avec 1RM changé à la main : pas de promesse, non écrasé
    d = dataset([ex(BS, 'Back Squat fab', 120)], [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, 110, True)})
    ctx, page, errors = fresh(b, d)
    page.click('.nav-btn[data-target="exercices"]'); page.wait_for_timeout(250)
    page.locator('.exercise-row', has_text='Back Squat fab').first.locator('.cycle-active-badge').click(); page.wait_for_timeout(300)
    page.click('.cycle-full-deactivate'); page.wait_for_timeout(200); m = modal(page)
    check(m['items'] == ['Back Squat fab, cycle 16, semaine 2 sur 6.'] and m['notes'] == [NOTE_1, STILL], 'C13 désactivation, 1RM changé à la main : %s %s' % (m['items'], m['notes']))
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    check(exs(page)[BS]['oneRepMax'] == 120 and not errors, 'C13 120 non écrasé')
    ctx.close()

    def open_deactivate(page, name):
        page.click('.nav-btn[data-target="exercices"]'); page.wait_for_timeout(250)
        page.locator('.exercise-row', has_text=name).first.locator('.cycle-active-badge').click(); page.wait_for_timeout(300)
        page.click('.cycle-full-deactivate'); page.wait_for_timeout(200)

    # C14 : "Désactiver" d'un mouvement dans aucune routine : pas de ligne "encore dans une routine", cycle supprimé
    d = dataset(base_ex, [routine('r-a', 'Jambes fab', [DL])], {BS: cycle(BS, 100, 110, True)})
    ctx, page, errors = fresh(b, d)
    open_deactivate(page, 'Back Squat fab'); m = modal(page)
    check(m['notes'] == [NOTE_1] and m['items'] == ['Back Squat fab, cycle 16, semaine 2 sur 6' + kept(110)], 'C14 hors routine : %s' % m['notes'])
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    # Deadlift (dans la routine, avec un 1RM) reçoit son propre cycle par l'activation automatique au démarrage : seul Back Squat compte ici
    check(BS not in cycles(page) and exs(page)[BS]['oneRepMax'] == 110 and not errors, 'C14 cycle supprimé, 110 recopié')
    ctx.close()

    # C15 : suppression de routine, recopie prévue en échec : message à un seul bouton, routine, cycles et 1RM intacts
    d = dataset(base_ex, [routine('r-a', 'Jambes fab', [DL, BS])], {BS: cycle(BS, 100, 110, True), DL: cycle(DL, 130, 130, False, 'C', 3)})
    ctx, page, errors = fresh(b, d)
    before = data(page)
    programme(page); open_delete(page, 'Jambes fab'); page.evaluate(BREAK_EXERCISES)
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300); m = modal(page)
    check(m['visible'] and m['message'] == fail_msg('Back Squat fab', 'la routine et ses cycles sont conservés.') and m['items'] == []
          and m['confirm'] == 'Compris' and not m['cancel_visible'], 'C15 message d\'échec exact, un seul bouton : %s' % m['message'])
    check(data(page) == before and not errors, 'C15 routine, cycles (Deadlift compris) et 1RM identiques octet pour octet (%s)' % errors[:1])
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(200)
    check(page.is_hidden('#confirm-modal-overlay') and page.locator('.routine-row', has_text='Jambes fab').count() >= 1 and len(routines(page)) == 1,
          'C15 Compris ferme, routine toujours listée')
    # puis une autre confirmation : le bouton Annuler est de nouveau visible
    open_delete(page, 'Jambes fab'); m = modal(page)
    check(m['cancel_visible'] and m['cancel'] == 'Annuler', 'C15 confirmation suivante : Annuler de nouveau visible')
    page.click('#confirm-modal-cancel'); page.wait_for_timeout(200)
    ctx.close()

    # C16 : même échec de stockage, mais aucune recopie prévue (cycle sans test validé) : suppression normale
    d = dataset(base_ex, [routine('r-a', 'Jambes fab', [DL])], {DL: cycle(DL, 130, 130, False, 'C', 3)})
    ctx, page, errors = fresh(b, d)
    ex_before = ls(page)['ovryk.exercises']
    programme(page); open_delete(page, 'Jambes fab'); page.evaluate(BREAK_EXERCISES)
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    check(page.is_hidden('#confirm-modal-overlay') and routines(page) == [] and cycles(page) == {} and ls(page)['ovryk.exercises'] == ex_before and not errors,
          'C16 sans recopie prévue : routine et cycle supprimés comme avant, exercices intacts')
    ctx.close()

    # C17 : × en échec de recopie : l'exercice reste dans la routine, cycle intact, message exact
    # Deadlift sans 1RM : pas d'activation automatique, donc vraiment sans cycle
    d = dataset([ex(BS, 'Back Squat fab', 100), ex(DL, 'Deadlift fab', None)], [routine('r-a', 'Jambes fab', [BS, DL])], {BS: cycle(BS, 100, 110, True)})
    ctx, page, errors = fresh(b, d)
    before = data(page)
    editor(page, 'Jambes fab'); cross(page, 'Back Squat fab'); page.evaluate(BREAK_EXERCISES)
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300); m = modal(page)
    check(m['message'] == fail_msg('Back Squat fab', 'l\'exercice reste dans la routine et son cycle est conservé.') and not m['cancel_visible'],
          'C17 × message exact : %s' % m['message'])
    check(data(page) == before and page.locator('.routine-exercise-block', has_text='Back Squat fab').count() == 1 and not errors,
          'C17 routine, cycle et 1RM identiques, exercice toujours affiché dans l\'éditeur (%s)' % errors[:1])
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(200)
    # × d'un exercice sans cycle avec le même stockage en échec : retrait direct, comme avant
    cross(page, 'Deadlift fab')
    check(page.is_hidden('#confirm-modal-overlay') and rt_ids(page, 'r-a') == [BS], 'C17 × sans cycle : retrait direct inchangé')
    ctx.close()

    # C18 : "Désactiver" en échec de recopie : cycle intact, page du cycle toujours ouverte, message exact
    d = dataset(base_ex, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, 110, True)})
    ctx, page, errors = fresh(b, d)
    before = data(page)
    open_deactivate(page, 'Back Squat fab'); page.evaluate(BREAK_EXERCISES)
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300); m = modal(page)
    check(m['message'] == fail_msg('Back Squat fab', 'le cycle est conservé.') and not m['cancel_visible'], 'C18 message exact : %s' % m['message'])
    check(data(page) == before and page.is_visible('#cycle-detail-page') and not errors, 'C18 cycle et 1RM identiques, page du cycle ouverte (%s)' % errors[:1])
    ctx.close()

    # C19 : "Désactiver" d'un cycle sans test validé avec stockage en échec : désactivé comme avant
    d = dataset(base_ex, [routine('r-a', 'Jambes fab', [DL])], {BS: cycle(BS, 100, 100, False)})
    ctx, page, errors = fresh(b, d)
    open_deactivate(page, 'Back Squat fab'); page.evaluate(BREAK_EXERCISES)
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    check(page.is_hidden('#confirm-modal-overlay') and BS not in cycles(page) and not errors, 'C19 sans recopie prévue : désactivé comme avant')
    ctx.close()

    b.close()

print('\n%d/%d' % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
