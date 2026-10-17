"""Cycles liés au programme, livraison 2 : cycles hors programme (exercice
dans aucune routine) masqués de l'Accueil, du bandeau, de la carte de
Programme, de la coordination des départs (R7) et de la décharge de la
muscu (lot 13) ; "Tirer mes cycles" filtré ; bouton "Supprimer les cycles
hors programme" ; échecs d'écriture (constats 1 et 2 de l'audit).
Données FABRIQUÉES ici : aucun vrai export, aucun appel réseau.
Usage : python3 test_cycles_programme.py <dossier de travail>, site servi sur http://127.0.0.1:8765."""
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
def kept(kg): return ". 1RM validé de %s kg conservé sur l'exercice." % str(kg).replace('.', ',')
def fail_msg(name, kept_text):
    return 'Le 1RM validé de « %s » n\'a pas pu être enregistré (stockage plein ou indisponible). Rien n\'a été supprimé : %s' % (name, kept_text)
def break_key(key):
    return """() => { const orig = Storage.prototype.setItem; Storage.prototype.setItem = function (k, v) {
  if (k === '%s') throw new DOMException('quota', 'QuotaExceededError'); return orig.call(this, k, v); }; }""" % key

# ---------- fixtures fabriquées ----------
def ex(eid, name, orm=None, cat='Lifting'):
    d = {'id': eid, 'name': name, 'category': cat, 'equipment': 'Barre', 'unit': 'kg', 'isCustom': True, 'oneRepMax': orm}
    if cat == 'Lifting': d['liftBaseMode'] = 'force'
    return d
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
def rex(eid, sets=1, weight=0): return {'exerciseId': eid, 'restSeconds': 120, 'sets': [{'reps': 5, 'weight': weight, 'weightKg': weight} for _ in range(sets)]}
def routine(rid, name, rexes, weekdays=None):
    return {'id': rid, 'name': name, 'weekdays': weekdays or [], 'updatedAt': '2026-09-01T00:00:00.000Z', 'createdAt': '2026-09-01T00:00:00.000Z',
            'exercises': [r if isinstance(r, dict) else rex(r) for r in rexes]}
def dataset(exercises, routines, cycles, settings=None):
    st = {'unit': 'kg', 'restTimerSeconds': 90, 'lastExportAt': None}
    st.update(settings or {})
    return {'exercises': exercises, 'routines': routines, 'sessions': [], 'settings': st, 'forceCycles': cycles, 'meta': {'schemaVersion': 2}}

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
def nav(page, target): page.click('.nav-btn[data-target="%s"]' % target); page.wait_for_timeout(300)
def programme(page): nav(page, 'routine')
def open_activate(page):
    nav(page, 'exercices'); page.click('#exercises-activate-cycles-btn'); page.wait_for_timeout(300)
def activate_names(page): return page.locator('#activate-cycles-list .activate-cycle-row .picker-row-name').all_inner_texts()
def orphan_box(page):
    vis = page.is_visible('#activate-cycles-orphans')
    return {'visible': vis, 'text': page.inner_text('#activate-cycles-orphans .activate-cycles-orphans-text') if vis else '',
            'btn': page.text_content('#activate-cycles-orphans-btn') if vis else ''}
def modal(page):
    return {'visible': page.is_visible('#confirm-modal-overlay'),
            'message': page.inner_text('#confirm-modal-message'),
            'items': page.locator('#confirm-modal-details .modal-details-list li').all_inner_texts(),
            'notes': page.locator('#confirm-modal-details .modal-details-note').all_inner_texts(),
            'confirm': page.text_content('#confirm-modal-confirm'), 'cancel': page.text_content('#confirm-modal-cancel'),
            'cancel_visible': page.is_visible('#confirm-modal-cancel')}
def open_delete(page, name):
    page.locator('.routine-row', has_text=name).first.locator('.routine-action-btn.danger').click(); page.wait_for_timeout(200)

with sync_playwright() as p:
    b = p.chromium.launch()
    BS, DL, ZS, SN, CJ = 'ex-bs', 'ex-dl', 'ex-zs', 'ex-sn', 'ex-cj'

    # P0 : aucun cycle hors programme : pas d'encart, aucune écriture à l'ouverture de "Tirer mes cycles"
    d = dataset([ex(BS, 'Back Squat fab', 100), ex(SN, 'Snatch fab', 60)], [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, 110, True)})
    ctx, page, errors = fresh(b, d)
    before = ls(page)
    open_activate(page)
    ob = orphan_box(page)
    check(not ob['visible'] and activate_names(page) == ['Back Squat fab'] and ls(page) == before and not errors,
          'P0 aucun orphelin : encart absent, seul le mouvement de la routine proposé (%s), aucune écriture' % activate_names(page))
    ctx.close()

    # P1 : un orphelin (Zercher, testé, semaine 5 sur 6), Back Squat dans une routine, Deadlift dans deux routines
    base = [ex(BS, 'Back Squat fab', 100), ex(DL, 'Deadlift fab', 130), ex(ZS, 'Zercher fab', 80), ex(SN, 'Snatch fab', None)]
    d = dataset(base, [routine('r-a', 'Jambes fab', [BS, DL]), routine('r-b', 'Dos fab', [DL])],
                {BS: cycle(BS, 100, 110, True, 'D', 2), DL: cycle(DL, 130, 130, False, 'C', 3), ZS: cycle(ZS, 80, 90, True, 'D', 5)})
    ctx, page, errors = fresh(b, d)
    before = ls(page)
    page.reload(); page.wait_for_timeout(400)
    banner_hidden = page.is_hidden('#cycle-alert-banner')
    next_test = page.inner_text('#dash-next-test-name') if page.is_visible('#dash-next-test') else ''
    check(banner_hidden and next_test == 'Deadlift fab, semaine 6',
          'P1 Accueil : bandeau "semaine de test bientôt" de Zercher masqué, carte Prochain test = "%s"' % next_test)
    programme(page)
    prog = page.locator('#programme-cycles-body .programme-cycle-name').all_text_contents()  # texte avant majuscules CSS
    check(sorted(prog) == ['Back Squat fab', 'Deadlift fab'], 'P1 carte de Programme sans Zercher : %s' % prog)
    open_activate(page)
    ob = orphan_box(page)
    check(activate_names(page) == ['Back Squat fab', 'Deadlift fab'], 'P1 "Tirer mes cycles" : seulement les mouvements des routines %s' % activate_names(page))
    check(ob['visible'] and ob['text'] == "1 cycle n'est lié à aucune routine : Zercher fab. Il est masqué de l'Accueil et de Programme."
          and ob['btn'] == 'Supprimer les cycles hors programme', 'P1 encart : "%s"' % ob['text'])
    check(ls(page) == before and not errors, 'P1 Accueil, Programme et "Tirer mes cycles" : aucune écriture, aucune erreur (%s)' % errors[:1])
    page.click('#activate-cycles-orphans-btn'); page.wait_for_timeout(200); m = modal(page)
    check(m['message'] == 'Supprimer les cycles hors programme ?' and m['items'] == ['Zercher fab, cycle 16, semaine 5 sur 6' + kept(90)]
          and m['notes'] == [NOTE_1] and m['confirm'] == 'Supprimer' and m['cancel'] == 'Annuler' and m['cancel_visible'],
          'P1 confirmation exacte : %s' % m)
    page.click('#confirm-modal-cancel'); page.wait_for_timeout(200)
    page.click('#activate-cycles-orphans-btn'); page.wait_for_timeout(200); page.mouse.click(10, 10); page.wait_for_timeout(200)
    check(ls(page) == before and page.is_hidden('#confirm-modal-overlay'), 'P1 Annuler puis tap hors boîte : rien ne change')
    page.click('#activate-cycles-orphans-btn'); page.wait_for_timeout(200)
    page.evaluate("() => { const b = document.getElementById('confirm-modal-confirm'); b.click(); b.click(); }"); page.wait_for_timeout(300)
    c = cycles(page); e = exs(page); old_c = json.loads(before['ovryk.forceCycles'])
    check(sorted(c) == [BS, DL] and c[BS] == old_c[BS] and c[DL] == old_c[DL] and e[ZS]['oneRepMax'] == 90 and not orphan_box(page)['visible'] and not errors,
          'P1 Supprimer (double tap) : Zercher supprimé, 90 recopié, Back Squat et Deadlift identiques, encart disparu (%s)' % errors[:1])
    check(routines(page) == json.loads(before['ovryk.routines']), 'P1 routines inchangées')
    ctx.close()

    # P2 : plusieurs orphelins : testé, sans test, 1RM changé à la main ; ordre alphabétique, texte au pluriel
    d = dataset([ex(BS, 'Back Squat fab', 100), ex(ZS, 'Zercher fab', 80), ex(SN, 'Snatch fab', 60), ex(CJ, 'Clean fab', 120)],
                [routine('r-a', 'Jambes fab', [BS])],
                {BS: cycle(BS, 100, 110, True), ZS: cycle(ZS, 80, 90, True, 'D', 5), SN: cycle(SN, 60, 60, False, 'C', 3), CJ: cycle(CJ, 100, 105, True, '6', 4)})
    ctx, page, errors = fresh(b, d)
    open_activate(page); ob = orphan_box(page)
    check(ob['text'] == "3 cycles ne sont liés à aucune routine : Clean fab, Snatch fab, Zercher fab. Ils sont masqués de l'Accueil et de Programme.",
          'P2 encart pluriel : "%s"' % ob['text'])
    page.click('#activate-cycles-orphans-btn'); page.wait_for_timeout(200); m = modal(page)
    check(m['items'] == ['Clean fab, cycle 6, semaine 4 sur 8.', 'Snatch fab, cycle 15, semaine 3 sur 6.', 'Zercher fab, cycle 16, semaine 5 sur 6' + kept(90)]
          and m['notes'] == [NOTE_N], 'P2 promesse seulement pour Zercher : %s' % m['items'])
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    e = exs(page)
    check(list(cycles(page)) == [BS] and e[ZS]['oneRepMax'] == 90 and e[SN]['oneRepMax'] == 60 and e[CJ]['oneRepMax'] == 120 and not errors,
          'P2 trois orphelins supprimés ; 90 recopié, 60 (sans test) et 120 (changé à la main) inchangés')
    ctx.close()

    # P3 : aucun mouvement Lifting dans une routine : message clair ; l'orphelin reste proposé au nettoyage
    d = dataset([ex(ZS, 'Zercher fab', 80), ex('ex-m', 'Presse fab', None, 'Jambes')], [routine('r-m', 'Muscu fab', ['ex-m'])], {ZS: cycle(ZS, 80, 90, True)})
    ctx, page, errors = fresh(b, d)
    before = ls(page)
    open_activate(page)
    empty = page.inner_text('#activate-cycles-list')
    check("Ajoute d'abord un mouvement Lifting à une routine." in empty and activate_names(page) == [] and orphan_box(page)['visible']
          and page.is_disabled('#activate-cycles-draw-btn') and ls(page) == before, 'P3 message "%s", bouton Tirer désactivé, encart présent' % empty.replace('\n', ' / '))
    ctx.close()

    # P4 : bouton de nettoyage, recopie prévue en échec : rien supprimé, message exact à un seul bouton
    d = dataset([ex(BS, 'Back Squat fab', 100), ex(ZS, 'Zercher fab', 80), ex(SN, 'Snatch fab', 60)], [routine('r-a', 'Jambes fab', [BS])],
                {BS: cycle(BS, 100, 110, True), ZS: cycle(ZS, 80, 90, True, 'D', 5), SN: cycle(SN, 60, 60, False, 'C', 3)})
    ctx, page, errors = fresh(b, d)
    before = data(page)
    open_activate(page); page.click('#activate-cycles-orphans-btn'); page.wait_for_timeout(200)
    page.evaluate(break_key('ovryk.exercises'))
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300); m = modal(page)
    check(m['message'] == fail_msg('Zercher fab', 'les cycles hors programme sont conservés.') and m['confirm'] == 'Compris' and not m['cancel_visible'],
          'P4 message exact : %s' % m['message'])
    check(data(page) == before and not errors, 'P4 aucun cycle supprimé (Snatch sans recopie compris), données identiques octet pour octet (%s)' % errors[:1])
    ctx.close()

    # P5 (constat 2) : vraie exception levée par OvrykDB.updateExerciseOneRepMax : try/catch de writeValidatedOneRMs
    d = dataset([ex(BS, 'Back Squat fab', 100)], [routine('r-a', 'Jambes fab', [BS])], {BS: cycle(BS, 100, 110, True)})
    ctx, page, errors = fresh(b, d)
    before = data(page)
    programme(page); open_delete(page, 'Jambes fab')
    page.evaluate("() => { window.OvrykDB.updateExerciseOneRepMax = function () { throw new Error('panne simulée'); }; }")
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300); m = modal(page)
    check(m['message'] == fail_msg('Back Squat fab', 'la routine et ses cycles sont conservés.') and data(page) == before and not errors,
          'P5 exception rattrapée : message exact, routine et cycle intacts, aucune erreur non rattrapée (%s)' % errors[:1])
    ctx.close()

    # P6 (constat 2) : deux cycles testés, première recopie réussie, seconde en échec, puis nouvel essai
    d = dataset([ex(BS, 'Back Squat fab', 100), ex(DL, 'Deadlift fab', 130)], [routine('r-a', 'Jambes fab', [BS, DL])],
                {BS: cycle(BS, 100, 110, True), DL: cycle(DL, 130, 140, True, 'C', 3)})
    ctx, page, errors = fresh(b, d)
    before = data(page)
    programme(page); open_delete(page, 'Jambes fab')
    page.evaluate("""() => { const real = window.OvrykDB.updateExerciseOneRepMax; let n = 0; window.__realUpdate = real;
      window.OvrykDB.updateExerciseOneRepMax = function (id, v) { n++; if (n === 2) throw new Error('panne simulée'); return real.call(this, id, v); }; }""")
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300); m = modal(page)
    e = exs(page)
    check(m['message'] == fail_msg('Deadlift fab', 'la routine et ses cycles sont conservés.') and routines(page) == json.loads(before['ovryk.routines'])
          and cycles(page) == json.loads(before['ovryk.forceCycles']) and e[BS]['oneRepMax'] == 110 and e[DL]['oneRepMax'] == 130 and not errors,
          'P6 seconde recopie en échec : routine et deux cycles intacts, Back Squat déjà à 110, Deadlift 130 inchangé')
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(200)
    page.evaluate("() => { window.OvrykDB.updateExerciseOneRepMax = window.__realUpdate; }")
    open_delete(page, 'Jambes fab'); m = modal(page)
    check(m['items'] == ['Back Squat fab, cycle 16, semaine 2 sur 6.', 'Deadlift fab, cycle 15, semaine 3 sur 6' + kept(140)],
          'P6 nouvel essai : plus de promesse pour Back Squat (déjà recopié), promesse pour Deadlift : %s' % m['items'])
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    e = exs(page)
    check(routines(page) == [] and cycles(page) == {} and e[BS]['oneRepMax'] == 110 and e[DL]['oneRepMax'] == 140 and not errors,
          'P6 nouvel essai : routine et cycles supprimés, 110 et 140 conservés, aucune double écriture fausse')
    ctx.close()

    # P7 (constat 1) : écriture des routines en échec après la recopie : message, routine et cycles conservés
    d = dataset([ex(BS, 'Back Squat fab', 100), ex(DL, 'Deadlift fab', None)], [routine('r-a', 'Jambes fab', [BS, DL])], {BS: cycle(BS, 100, 110, True)})
    ctx, page, errors = fresh(b, d)
    before = data(page)
    programme(page); open_delete(page, 'Jambes fab'); page.evaluate(break_key('ovryk.routines'))
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300); m = modal(page)
    check(m['message'] == "La routine « Jambes fab » n'a pas pu être supprimée (stockage plein ou indisponible). Elle et ses cycles sont conservés."
          and m['confirm'] == 'Compris' and not m['cancel_visible'], 'P7 suppression de routine, message exact : %s' % m['message'])
    check(routines(page) == json.loads(before['ovryk.routines']) and cycles(page) == json.loads(before['ovryk.forceCycles'])
          and exs(page)[BS]['oneRepMax'] == 110 and not errors, 'P7 routine et cycle intacts, 110 déjà recopié (valeur juste)')
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(200)
    # × de l'éditeur, même panne : l'exercice reste affiché et stocké, son cycle aussi
    page.locator('.routine-row', has_text='Jambes fab').first.locator('.routine-row-main').click(); page.wait_for_timeout(300)
    page.locator('.routine-exercise-block', has_text='Back Squat fab').first.locator('.rex-remove-btn').click(); page.wait_for_timeout(200)
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300); m = modal(page)
    stored = [x['exerciseId'] for x in routines(page)[0]['exercises']]
    check(m['message'] == "« Back Squat fab » n'a pas pu être retiré de la routine (stockage plein ou indisponible). L'exercice et son cycle sont conservés."
          and stored == [BS, DL] and BS in cycles(page) and page.locator('.routine-exercise-block', has_text='Back Squat fab').count() == 1 and not errors,
          'P7 × : message exact, exercice toujours stocké et affiché, cycle intact (%s)' % m['message'])
    ctx.close()

    # P8 (A, R7) : seuil lourd à 0 (toute semaine compte), 1 cycle lourd par semaine. Un cycle fixe en semaine 1 de A
    # occupe les semaines 1 à 6 ; un nouveau mouvement de la routine (1RM, sans cycle) est activé au démarrage.
    NW, FX = 'ex-nw', 'ex-fx'
    st = {'heavyThreshold': 0, 'maxHeavyCyclesPerWeek': 1}
    def r7(fixed_in_programme):
        rts = [routine('r-a', 'Force fab', [NW])] + ([routine('r-b', 'Fixe fab', [FX])] if fixed_in_programme else [])
        dd = dataset([ex(NW, 'Nouveau fab', 100), ex(FX, 'Fixe fab mvt', 120)], rts, {FX: cycle(FX, 120, 120, False, 'A', 1)}, st)
        c2, pg, er = fresh(b, dd)
        cy = cycles(pg)
        out = (cy.get(NW, {}).get('decalage_semaines'), pg.is_visible('#confirm-modal-overlay'), cy.get(FX) == dd['forceCycles'][FX], er)
        c2.close()
        return out
    off_orphan, modal_orphan, fx_same_o, er_o = r7(False)
    off_prog, modal_prog, fx_same_p, er_p = r7(True)
    check(off_orphan == 0 and not modal_orphan and fx_same_o and not er_o, 'P8 R7 : cycle fixe hors programme ignoré, nouveau cycle sans décalage (%s)' % off_orphan)
    check(off_prog == 6 and not modal_prog and fx_same_p and not er_p, 'P8 R7 : même cycle fixe dans le programme, décalage actuel inchangé (%s)' % off_prog)

    # P9 (B, lot 13) : cycle '2' en semaine 7 (allégée), décharge automatique ; séance de muscu à 3 séries
    LX, MX = 'ex-lx', 'ex-mx'
    def deload(cycle_in_programme):
        rts = [routine('r-m', 'Muscu fab', [rex(MX, 3, 50)])] + ([routine('r-f', 'Force fab', [LX])] if cycle_in_programme else [])
        dd = dataset([ex(LX, 'Lift fab', 100), ex(MX, 'Presse fab', None, 'Jambes')], rts, {LX: cycle(LX, 100, 100, False, '2', 7)},
                     {'deloadMuscuMode': 'auto'})
        c2, pg, er = fresh(b, dd)
        pg.click('#dash-settings-btn'); pg.wait_for_timeout(300)
        section = pg.is_visible('#profile-deload-section')
        nav(pg, 'seance'); pg.locator('#seance-routine-list .routine-row-main', has_text='Muscu fab').first.click(); pg.wait_for_timeout(700)
        live = [x for x in json.loads(ls(pg)['ovryk.sessions']) if x['status'] == 'in_progress']
        n = len(live[0]['exercises'][0]['sets']) if live else None
        c2.close()
        return section, n, er
    sec_o, n_o, er_o = deload(False)
    sec_p, n_p, er_p = deload(True)
    check(not sec_o and n_o == 3 and not er_o, 'P9 décharge : cycle hors programme, réglage masqué et séance non allégée (%s séries)' % n_o)
    check(sec_p and n_p == 2 and not er_p, 'P9 décharge : même cycle dans le programme, réglage affiché et séance allégée comme avant (%s séries)' % n_p)

    b.close()

print('\n%d/%d' % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
