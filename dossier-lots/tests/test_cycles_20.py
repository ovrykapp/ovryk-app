"""v161 : 20 cycles C1 à C20. Cycles actifs d'un vrai export intacts, tirage dans les 20 seulement,
jamais deux fois le même, aucun Intensité après un Intensité, séance C16 (échauffement hors bilan, rappel du
cycle), page détail (type, durée, explication, kg). Site servi sur http://127.0.0.1:8765.
Usage : python3 test_cycles_20.py <dossier de captures> <export JSON>"""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright
SP = Path(sys.argv[1]); URL = 'http://127.0.0.1:8765/index.html'
EXPORT = json.load(open(sys.argv[2]))['data']
res = []
def check(c, m): res.append(bool(c)); print(('ok     ' if c else 'ECHEC  ') + m)
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
NEW = ['C%d' % i for i in range(1, 21)]
INT = ['C8', 'C9', 'C14', 'C17']

with sync_playwright() as p:
    b = p.chromium.launch()
    # T1 : vrai export, cycles C et D intacts
    d = {k: EXPORT[k] for k in ['exercises', 'routines', 'sessions', 'settings', 'forceCycles', 'meta'] if k in EXPORT}
    ctx, page, errors = fresh(b, d)
    fc = cycles(page)
    check(fc['ex-deadlift']['cycle_actif'] == 'C' and fc['ex-deadlift']['semaine_actuelle'] == 2 and fc['ex-back-squat']['cycle_actif'] == 'D'
          and fc['ex-deadlift']['one_rm_actuel'] == 130 and fc['ex-back-squat']['one_rm_actuel'] == 100, 'T1 cycles actifs C et D intacts (semaine, 1RM)')
    check(json.dumps(fc['ex-deadlift'], sort_keys=True) == json.dumps({**EXPORT['forceCycles']['ex-deadlift'], **{k: v for k, v in fc['ex-deadlift'].items() if k not in EXPORT['forceCycles']['ex-deadlift']}}, sort_keys=True), 'T1 cycle Deadlift identique champ par champ')
    nav(page, 'dashboard') if page.query_selector('.nav-btn[data-target="dashboard"]') else None
    body = page.inner_text('body')
    page.screenshot(path=str(SP / 't1-dashboard.png'), full_page=True)
    # tirage depuis l'ancien cycle C : toujours dans les 20
    draws = page.evaluate("""() => { const raw = localStorage.getItem('ovryk.forceCycles'); const out = [];
      for (let i = 0; i < 150; i++) { localStorage.setItem('ovryk.forceCycles', raw); out.push(OvrykDB.closeCycleAndDrawNext('ex-deadlift', 135).prochain_cycle); }
      localStorage.setItem('ovryk.forceCycles', raw); return out; }""")
    check(all(x in NEW for x in draws) and len(set(draws)) >= 15, 'T1 fin de l\'ancien cycle C : prochain tiré parmi C1 à C20 (%d distincts sur 150)' % len(set(draws)))
    check(not errors, 'T1 aucune erreur JS ' + str(errors[:2]))
    ctx.close()

    # T2 : règles de tirage après C8 (Intensité) et C1 (Volume)
    BS = 'ex-bs'
    base = [ex(BS, 'Back Squat fab', 100)]
    for src, intense in [('C8', True), ('C1', False), ('C17', True)]:
        d = dataset(base, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, src, 7)})
        ctx, page, errors = fresh(b, d)
        draws = page.evaluate("""(id) => { const raw = localStorage.getItem('ovryk.forceCycles'); const out = [];
          for (let i = 0; i < 300; i++) { localStorage.setItem('ovryk.forceCycles', raw); const c = OvrykDB.closeCycleAndDrawNext(id, 105); out.push(c.prochain_cycle);
            out.push(OvrykDB.redrawPendingCycle ? (OvrykDB.redrawPendingCycle(id) || {}).prochain_cycle || OvrykDB.getForceCycle(id).prochain_cycle : null); }
          localStorage.setItem('ovryk.forceCycles', raw); return out; }""", BS)
        draws = [x for x in draws if x]
        okset = all(x in NEW and x != src for x in draws)
        hasInt = any(x in INT for x in draws)
        check(okset and (hasInt != intense), 'T2 après %s : %d tirages (dont relances), jamais %s, Intensité %s' % (src, len(draws), src, 'jamais' if not hasInt else 'possible'))
        ctx.close()

    # T3 : séance C16 S1, rappel, échauffement hors bilan
    d = dataset(base, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, 'C16', 1)})
    ctx, page, errors = fresh(b, d)
    start_routine(page, 'Jambes fab')
    sx = live(page)['exercises'][0]
    check(len(sx['sets']) == 10 and [s.get('warmup', False) for s in sx['sets']] == [True] * 6 + [False] * 4
          and [s['percent1rm'] for s in sx['sets']] == [60] * 6 + [60, 62.5, 65, 68], 'T3 séance C16 S1 : 6 singles EMOM fixes à 60 %, puis 4x3 qui monte jusqu\'à 68 % (v162)')
    kgs = [round(100 * s['percent1rm'] / 100 / 2.5) * 2.5 for s in sx['sets'] if not s.get('warmup')]
    check(kgs == sorted(kgs) and kgs[-1] == 67.5, 'T3 kg du bloc de force jamais en baisse, dernière série à la charge du gabarit : %s' % kgs)
    rem = page.inner_text('.live-card.is-open .live-cycle-reminder') if page.query_selector('.live-card.is-open .live-cycle-reminder') else ''
    check(rem == 'C16, S1 : EMOM 6x1 à 60 % puis 4x3 jusqu\'à 68 %', 'T3 rappel en séance : "%s"' % rem)
    live_txt = page.inner_text('.live-card.is-open')
    check(all(x in live_txt for x in ['60 kg, 60 %', '62,5 kg, 63 %', '67,5 kg, 68 %']) or all(x in live_txt for x in ['60 kg', '62.5 kg', '67.5 kg']), 'T3 chaque série affiche sa propre charge en kg')
    tag = page.inner_text('.live-card .live-card-tag')
    check(tag.lower().startswith('cycle 16'), 'T3 étiquette : "%s"' % tag)
    page.screenshot(path=str(SP / 't3-seance-c16.png'), full_page=True)
    validate_one(page)
    finish(page)
    hist = page.evaluate("(id) => OvrykDB.closeCycleAndDrawNext(id, 101).historique_cycles", BS)
    check(hist[-1]['seances'] == 1 and hist[-1]['reussite_pct'] is None, 'T3 série d\'échauffement seule validée : séance comptée, aucun taux de réussite (%s)' % hist[-1])
    check(not errors, 'T3 aucune erreur JS ' + str(errors[:2]))
    ctx.close()

    # T4 : page détail C8 depuis le Dashboard
    d = dataset(base, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, 'C8', 3)})
    ctx, page, errors = fresh(b, d)
    page.evaluate("() => { const r = JSON.parse(localStorage.getItem('ovryk.routines')); r[0].weekdays = [0,1,2,3,4,5,6]; localStorage.setItem('ovryk.routines', JSON.stringify(r)); }")
    page.reload(); page.wait_for_timeout(500)
    dash = page.inner_text('body')
    check('1 rep à 84 % puis 3x2 à 75 %' in dash and '75 % à 75 %' not in dash, 'T4 ligne du Dashboard : format du jour sans doublon de %')
    row = page.locator('.dash-session-ex-value.is-cycle').first
    row.click(); page.wait_for_timeout(500)
    det = page.inner_text('#cycle-detail-page')
    check('cycle 8 · top single + back off' in det.lower() and 'Intensité · 6 semaines + test' in det and 'La série lourde grimpe de 3% par semaine' in det,
          'T4 détail : nom, type, durée, explication')
    check('84% → 85kg' in det and '78% → 77.5kg' in det, 'T4 détail : charges en kg depuis le 1RM (S3 84 %% = 85 kg, S1 78 %% = 77,5 kg)')
    check('–' not in det and '—' not in det, 'T4 aucun tiret long ou moyen dans la page détail')
    page.screenshot(path=str(SP / 't4-detail-c8.png'), full_page=True)
    check(not errors, 'T4 aucune erreur JS ' + str(errors[:2]))
    ctx.close()

    # T5 (v162) : page détail C1, montée série par série, ligne d'explication
    d = dataset(base, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, 'C1', 5)})
    ctx, page, errors = fresh(b, d)
    page.evaluate("() => { const r = JSON.parse(localStorage.getItem('ovryk.routines')); r[0].weekdays = [0,1,2,3,4,5,6]; localStorage.setItem('ovryk.routines', JSON.stringify(r)); }")
    page.reload(); page.wait_for_timeout(500)
    page.locator('.dash-session-ex-value.is-cycle').first.click(); page.wait_for_timeout(500)
    det = page.inner_text('#cycle-detail-page')
    check('La charge monte à chaque série, la dernière série correspond au pourcentage de la semaine.' in det, 'T5 ligne de montée sous l\'explication')
    check(all(x in det for x in ['73% → 72.5kg', '75% → 75kg', '78% → 77.5kg', '80% → 80kg']), 'T5 S5 de C1 : 72,5, 75, 77,5 puis 80 kg')
    page.screenshot(path=str(SP / 't5-detail-c1.png'), full_page=True)
    check(not errors, 'T5 aucune erreur JS ' + str(errors[:2]))
    ctx.close()

    # T6 (v163) : C19 revenu à charge fixe, sans ligne de montée
    d = dataset(base, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 140, 'C19', 1)})
    ctx, page, errors = fresh(b, d)
    page.evaluate("() => { const r = JSON.parse(localStorage.getItem('ovryk.routines')); r[0].weekdays = [0,1,2,3,4,5,6]; localStorage.setItem('ovryk.routines', JSON.stringify(r)); }")
    page.reload(); page.wait_for_timeout(500)
    page.locator('.dash-session-ex-value.is-cycle').first.click(); page.wait_for_timeout(500)
    det = page.inner_text('#cycle-detail-page')
    check('La charge monte à chaque série' not in det and 'jusqu' not in det.lower(), 'T6 C19 : ni ligne de montée ni "jusqu\'à" dans le détail')
    check(det.count('70% → 97.5kg') == 10, 'T6 C19 S1 : 10 singles à 70 %% = 97,5 kg pour 1RM 140 (%d trouvés)' % det.count('70% → 97.5kg'))
    page.click('#cycle-detail-back-btn'); page.wait_for_timeout(300)
    start_routine(page, 'Jambes fab')
    sx = live(page)['exercises'][0]
    check([s['percent1rm'] for s in sx['sets']] == [70] * 10, 'T6 séance C19 S1 : 10 séries à 70 %, charge fixe')
    check(not errors, 'T6 aucune erreur JS ' + str(errors[:2]))
    ctx.close()

    # T7 (v165) : charge changée en séance, confirmation en fin de séance, ajustement des semaines restantes
    def kgs_live(page):
        sx = live(page)['exercises'][0]
        return [round(70 * x['percent1rm'] / 100 / 2.5) * 2.5 for x in sx['sets']], sx
    def validate_current(page):
        page.locator('.live-card.is-open button.live-set-circle.is-current').first.click(); page.wait_for_timeout(250)
        if page.is_visible('#rest-timer-overlay') if page.query_selector('#rest-timer-overlay') else False: pass
    def bump(page):
        page.click('.haltero-charge-toggle'); page.wait_for_timeout(200)
        page.locator('.haltero-charge-card .haltero-charge-step', has_text='+2,5').click(); page.wait_for_timeout(250)
    def finish_with_adjust(page, answer):
        page.click('#seance-finish-btn'); page.wait_for_timeout(200)
        page.click('#confirm-modal-confirm'); page.wait_for_timeout(800)
        msg = page.inner_text('#confirm-modal-message') if page.is_visible('#confirm-modal-overlay') else ''
        if msg: page.click('#confirm-modal-confirm' if answer else '#confirm-modal-cancel'); page.wait_for_timeout(400)
        return msg
    d = dataset(base, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 70, 'C11', 1)})
    ctx, page, errors = fresh(b, d)
    start_routine(page, 'Jambes fab')
    k0, _ = kgs_live(page)
    validate_current(page)
    bump(page)
    k1, sx = kgs_live(page)
    check(k1[0] == k0[0] and k1[1:] == [k + 2.5 for k in k0[1:]], 'T7 C11 S1 1RM 70 : série 2 +2,5 kg, suivantes décalées, série 1 validée intacte (%s puis %s)' % (k0, k1))
    check(all(abs(70 * x['percent1rm'] / 100 - k) < 0.01 for x, k in zip(sx['sets'][1:], k1[1:])), 'T7 % réel stocké (kg / 1RM)')
    for _ in range(4): validate_current(page)
    msg = finish_with_adjust(page, True)
    check(msg == 'Back Squat fab : +2,5 kg sur la dernière série. Appliquer cet écart aux prochaines semaines de ce cycle ?', 'T7 confirmation de fin : "%s"' % msg)
    fc = cycles(page)[BS]
    check(abs(fc.get('ajustement_pct', 0) - 3.57) < 0.001 and fc.get('ajustement_depuis_semaine') == 2 and fc['semaine_actuelle'] == 2, 'T7 Oui : ajustement %s points à partir de S%s' % (fc.get('ajustement_pct'), fc.get('ajustement_depuis_semaine')))
    past = last_done(page)['exercises'][0]['sets']
    def open_detail_programme(page):
        nav(page, 'routine'); page.locator('.programme-cycle-row').first.click(); page.wait_for_timeout(500)
    open_detail_programme(page)
    det = page.inner_text('#cycle-detail-page')
    check('Ajustement actif : +2,5 kg' in det, 'T7 ligne "Ajustement actif : +2,5 kg" dans le détail')
    check(all(x in det for x in ['70% → 47.5kg', '67% → 47.5kg']) or det.count('47.5kg') >= 1, 'T7 S2 recalculée dans le détail')
    page.screenshot(path=str(SP / 't7-detail-ajustement.png'), full_page=True)
    # deuxième séance (même semaine civile : séance légère de S1) à +5 kg : l'ajustement est remplacé, pas additionné
    page.click('#cycle-detail-back-btn'); page.wait_for_timeout(300)
    start_routine(page, 'Jambes fab')
    k2, _ = kgs_live(page)
    bump(page); page.locator('.haltero-charge-card .haltero-charge-step', has_text='+2,5').click(); page.wait_for_timeout(250)
    for _ in range(len(k2)): validate_current(page)
    msg2 = finish_with_adjust(page, True)
    fc = cycles(page)[BS]
    check(msg2.startswith('Back Squat fab : +5 kg') and abs(fc['ajustement_pct'] - 7.14) < 0.001, 'T7 nouvel ajustement +5 kg remplace le précédent (%s points, pas 10,71)' % fc['ajustement_pct'])
    check(json.dumps(last_done(page) and [x for x in json.loads(ls(page)['ovryk.sessions']) if x['status'] == 'completed'][0]['exercises'][0]['sets']) == json.dumps(past), 'T7 séance passée jamais réécrite')
    open_detail_programme(page)
    page.locator('#cycle-detail-page button', has_text='Retirer').click(); page.wait_for_timeout(300)
    fc = cycles(page)[BS]
    check(fc.get('ajustement_pct') is None and 'Ajustement actif' not in page.inner_text('#cycle-detail-page'), 'T7 Retirer supprime l\'ajustement')
    check(not errors, 'T7 aucune erreur JS ' + str(errors[:2]))
    ctx.close()

    # T8 (v165) : Non ne change rien ; ancien cycle D : décalage en séance proposé aussi
    d = dataset(base, [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, 'D', 2)})
    ctx, page, errors = fresh(b, d)
    fc0 = raw_cycles(page)
    start_routine(page, 'Jambes fab')
    sx0 = live(page)['exercises'][0]
    k0 = [round(100 * x['percent1rm'] / 100 / 2.5) * 2.5 for x in sx0['sets']]
    bump(page)
    sx1 = live(page)['exercises'][0]
    k1 = [round(100 * x['percent1rm'] / 100 / 2.5) * 2.5 for x in sx1['sets']]
    check(k1 == [k + 2.5 for k in k0], 'T8 ancien cycle D : toutes les séries non faites décalées de +2,5 kg (%s puis %s)' % (k0, k1))
    for _ in range(len(k1)): validate_current(page)
    msg = finish_with_adjust(page, False)
    fc = cycles(page)[BS]
    check(msg.startswith('Back Squat fab : +2,5 kg') and fc.get('ajustement_pct') is None, 'T8 Non : aucun ajustement stocké')
    check({k: v for k, v in fc.items() if k != 'semaine_actuelle'} == {k: v for k, v in json.loads(fc0)[BS].items() if k != 'semaine_actuelle'}, 'T8 cycle D inchangé hors avancée de semaine')
    check(not errors, 'T8 aucune erreur JS ' + str(errors[:2]))
    ctx.close()
    b.close()
print('\n%d/%d' % (sum(res), len(res)))
