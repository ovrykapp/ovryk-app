"""Constat 1 du second audit de la livraison 2 (cycles liés au programme) :
en séance, le cycle d'un exercice hors programme est ignoré (ni
prescription, ni choix du test, ni formulaire de test, ni avancement de
semaine). Séance libre avec un exercice du programme, séance lancée depuis
une routine : comportement inchangé. Routine supprimée pendant la séance :
aucune erreur, séries conservées.
Données FABRIQUÉES ici : aucun vrai export, aucun appel réseau.
Usage : python3 test_cycles_seance.py <dossier de travail>, site servi sur http://127.0.0.1:8765."""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
SP = Path(sys.argv[1]); URL = 'http://127.0.0.1:8765/index.html'
SP.mkdir(parents=True, exist_ok=True)
res = []
def check(c, m): res.append(bool(c)); print(('ok     ' if c else 'ECHEC  ') + m)

# ---------- fixtures fabriquées ----------
def ex(eid, name, orm=None, cat='Lifting'):
    d = {'id': eid, 'name': name, 'category': cat, 'equipment': 'Barre', 'unit': 'kg', 'isCustom': True, 'oneRepMax': orm}
    if cat == 'Lifting': d['liftBaseMode'] = 'force'
    return d
def cycle(eid, orm, cyc='D', week=2):
    return {'exercise_id': eid, 'cycle_actif': cyc, 'one_rm_actuel': orm, 'semaine_actuelle': week,
            'historique_1rm': [{'date': '2026-08-01T10:00:00.000Z', 'valeur': orm}], 'historique_cycles': [], 'prochain_cycle': None,
            'en_attente_de_validation': False, 'semaines_modifiees': {}, 'test_report_used': False, 'decalage_semaines': 0}
def rex(eid): return {'exerciseId': eid, 'restSeconds': 120, 'sets': [{'reps': 5, 'weight': 40, 'weightKg': 40}]}
def routine(rid, name, eids):
    return {'id': rid, 'name': name, 'weekdays': [], 'updatedAt': '2026-09-01T00:00:00.000Z', 'createdAt': '2026-09-01T00:00:00.000Z',
            'exercises': [rex(e) for e in eids]}
def dataset(exercises, routines, cycles):
    return {'exercises': exercises, 'routines': routines, 'sessions': [], 'forceCycles': cycles, 'meta': {'schemaVersion': 2},
            'settings': {'unit': 'kg', 'restTimerSeconds': 90, 'lastExportAt': None}}

def ls(page): return page.evaluate("() => { const o = {}; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); o[k] = localStorage.getItem(k); } return o; }")
def raw_cycles(page): return ls(page).get('ovryk.forceCycles')
def cycles(page): return json.loads(raw_cycles(page))
def live(page):
    l = [x for x in json.loads(ls(page)['ovryk.sessions']) if x['status'] == 'in_progress']
    return l[0] if l else None
def last_done(page):
    l = [x for x in json.loads(ls(page)['ovryk.sessions']) if x['status'] == 'completed']
    return l[-1] if l else None
def fresh(b, d):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    page = ctx.new_page(); errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(URL); page.evaluate("() => localStorage.clear()")
    for k, v in d.items(): page.evaluate("([k, v]) => localStorage.setItem(k, v)", ['ovryk.' + k, json.dumps(v)])
    page.reload(); page.wait_for_timeout(300); page.reload(); page.wait_for_timeout(300)
    return ctx, page, errors
def nav(page, target): page.click('.nav-btn[data-target="%s"]' % target); page.wait_for_timeout(300)
def start_empty(page): nav(page, 'seance'); page.click('#seance-start-empty-btn'); page.wait_for_timeout(500)
def start_routine(page, name):
    nav(page, 'seance'); page.locator('#seance-routine-list .routine-row-main', has_text=name).first.click(); page.wait_for_timeout(700)
def add_ex(page, name):
    page.click('#seance-add-exercise-btn'); page.wait_for_timeout(300)
    page.locator('#seance-exercise-picker .picker-row', has_text=name).first.click(); page.wait_for_timeout(400)
def choice_visible(page): return page.is_visible('#cycle-test-choice-modal-overlay')
def validate_one(page):
    page.locator('.live-card.is-open button.live-set-circle').first.click(); page.wait_for_timeout(300)
def finish(page):
    page.click('#seance-finish-btn'); page.wait_for_timeout(200)
    msg = page.inner_text('#confirm-modal-message')
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(800)
    return msg
ADV = 'Terminer la séance fera avancer tes cycles.'

with sync_playwright() as p:
    b = p.chromium.launch()
    BS, ZS, DL = 'ex-bs', 'ex-zs', 'ex-dl'
    base = [ex(BS, 'Back Squat fab', 100), ex(ZS, 'Zercher fab', 80), ex(DL, 'Presse fab', None, 'Jambes')]

    # S1 : séance libre, orphelin en semaine 2 : comme un exercice sans cycle, forceCycles intact octet pour octet
    d = dataset(base, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100), ZS: cycle(ZS, 80, 'D', 2)})
    ctx, page, errors = fresh(b, d)
    fc0 = raw_cycles(page)
    start_empty(page); add_ex(page, 'Zercher fab')
    sx = live(page)['exercises'][0]
    check(not choice_visible(page) and sx['cycleIdUsed'] is None and sx['cycleWeekUsed'] is None and len(sx['sets']) == 1
          and sx['oneRepMaxSnapshot'] == 80 and sx['restSeconds'] == 90 and not sx['isLightSession'] and raw_cycles(page) == fc0,
          'S1 orphelin ajouté : aucune prescription du cycle (cycleIdUsed %s, %d série, 1RM figé %s)' % (sx['cycleIdUsed'], len(sx['sets']), sx['oneRepMaxSnapshot']))
    validate_one(page)
    msg = finish(page)
    check(ADV not in msg and raw_cycles(page) == fc0 and last_done(page) and not errors,
          'S1 fin de séance : message sans "fera avancer", forceCycles identique octet pour octet (%s)' % errors[:1])
    ctx.close()

    # S2 : séance libre, orphelin en semaine de test : pas de choix du test, pas de formulaire, rien écrit
    d = dataset(base, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100), ZS: cycle(ZS, 80, 'D', 6)})
    ctx, page, errors = fresh(b, d)
    fc0 = raw_cycles(page)
    start_empty(page); add_ex(page, 'Zercher fab')
    lv = live(page)
    check(not choice_visible(page) and lv and len(lv['exercises']) == 1 and lv['exercises'][0]['cycleIdUsed'] is None
          and page.locator('.cycle-test-form').count() == 0 and raw_cycles(page) == fc0,
          'S2 orphelin en semaine de test : ni choix du test, ni formulaire, exercice ajouté sans cycle')
    validate_one(page)
    msg = finish(page)
    check(ADV not in msg and raw_cycles(page) == fc0 and not errors, 'S2 fin de séance : forceCycles identique octet pour octet (%s)' % errors[:1])
    ctx.close()

    # S3 : séance libre, exercice du programme (cycle dans une autre routine) : comportement actuel
    d = dataset(base, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, 'D', 2)})
    ctx, page, errors = fresh(b, d)
    start_empty(page); add_ex(page, 'Back Squat fab')
    sx = live(page)['exercises'][0]
    check(sx['cycleIdUsed'] == 'D' and sx['cycleWeekUsed'] == 2 and sx['oneRepMaxSnapshot'] == 100 and len(sx['sets']) > 1,
          'S3 exercice du programme : prescription du cycle 16 semaine 2 (%d séries)' % len(sx['sets']))
    validate_one(page)
    msg = finish(page)
    check(ADV in msg and cycles(page)[BS]['semaine_actuelle'] == 3 and not errors, 'S3 fin de séance : "fera avancer" affiché, semaine 2 vers 3')
    ctx.close()

    # S3b : séance libre, exercice du programme en semaine de test : le choix du test apparaît toujours
    d = dataset(base, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, 'D', 6)})
    ctx, page, errors = fresh(b, d)
    start_empty(page)
    page.click('#seance-add-exercise-btn'); page.wait_for_timeout(300)
    page.locator('#seance-exercise-picker .picker-row', has_text='Back Squat fab').first.click(); page.wait_for_timeout(400)
    check(choice_visible(page) and not errors, 'S3b exercice du programme en semaine de test : choix du test proposé comme avant')
    ctx.close()

    # S4 : séance lancée depuis la routine : prescription et avancement inchangés
    d = dataset(base, [routine('r-a', 'Jambes fab', [BS, DL])], {BS: cycle(BS, 100, 'D', 2)})
    ctx, page, errors = fresh(b, d)
    start_routine(page, 'Jambes fab')
    sx = live(page)['exercises'][0]
    check(sx['exerciseId'] == BS and sx['cycleIdUsed'] == 'D' and sx['cycleWeekUsed'] == 2 and len(sx['sets']) > 1,
          'S4 séance de routine : prescription du cycle inchangée')
    validate_one(page)
    msg = finish(page)
    check(ADV in msg and cycles(page)[BS]['semaine_actuelle'] == 3 and not errors, 'S4 fin de séance : semaine 2 vers 3 comme avant')
    ctx.close()

    # S5 : routine supprimée pendant la séance : aucune erreur, séries conservées, aucun cycle avancé
    d = dataset(base, [routine('r-a', 'Jambes fab', [BS, DL])], {BS: cycle(BS, 100, 'D', 2)})
    ctx, page, errors = fresh(b, d)
    start_routine(page, 'Jambes fab')
    validate_one(page)
    done_before = [s for s in live(page)['exercises'][0]['sets'] if s.get('done')]
    nav(page, 'routine')
    page.locator('.routine-row', has_text='Jambes fab').first.locator('.routine-action-btn.danger').click(); page.wait_for_timeout(200)
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    gone = json.loads(ls(page)['ovryk.routines']) == [] and BS not in cycles(page)
    nav(page, 'seance')
    lv = live(page)
    kept = lv and [s for s in lv['exercises'][0]['sets'] if s.get('done')] == done_before
    msg = finish(page)
    dn = last_done(page)
    check(gone and kept and dn and [s for s in dn['exercises'][0]['sets'] if s.get('done')] == done_before
          and ADV not in msg and cycles(page) == {} and not errors,
          'S5 routine supprimée en cours de séance : séries validées conservées, séance terminée, aucun cycle avancé (%s)' % errors[:1])
    ctx.close()

    b.close()

print('\n%d/%d' % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
