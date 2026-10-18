"""Lot 19 : machine à On Air par créneau de routine (rex.onairExerciseId, facultatif).
Livraison 1 : mémorisation et éditeur, AUCUN changement des séances.
O1 réglages du créneau : section "Machine à On Air", aucune écriture à l'ouverture, absente pour un mouvement (Lifting).
O2 écran de choix : exercices existants seulement (ni Lifting, ni l'exercice du créneau), aucun bouton de création,
   Fermer sans écriture, choix puis Enregistrer : seul ce champ de ce créneau est écrit, updatedAt intact.
O3 affichage (réglages, résumé du créneau dans l'éditeur), rechargement, retrait (null), "Aucune" sans choix : rien écrit.
O4 machine introuvable : affichée, aucune écriture, choix refusé redevenu invalide au moment d'écrire, double tap.
O5 conservation du champ par chaque chemin de l'éditeur (nom, jours, monter, descendre, grouper, type, dissoudre,
   kilos, repos, ajout, retrait d'un autre créneau, Enregistrer), par la duplication et par le remplacement de la 3a.
O6 export puis restauration gardent le champ ; ancien export sans le champ : aucun champ ajouté.
O7 séances inchangées par la livraison 1 : même construction dans les deux salles avec ou sans choix.
O8 390 px : réglages et écran de choix sans débordement horizontal.
Données FABRIQUÉES ici. Usage : python3 test_onair.py <dossier de travail>, site servi sur http://127.0.0.1:8765."""
import json, copy
from playwright.sync_api import sync_playwright
from restore_commun import *

F = workdir()
X, Y, Z, E, W, L = 'ex-x', 'ex-y', 'ex-z', 'ex-e', 'ex-w', 'ex-l'
def mex(eid, name, cat='Jambes', **kw):
    d = {'id': eid, 'name': name, 'category': cat, 'equipment': 'Machine', 'unit': 'kg', 'isCustom': True}
    if cat == 'Lifting': d['liftBaseMode'] = 'force'
    d.update(kw); return d
def rset(w=50): return {'repType': 'range', 'repsMin': 8, 'repsMax': 10, 'weightKg': w, 'repsActual': None, 'done': False}
def rex(rid, eid, **kw):
    d = {'id': rid, 'exerciseId': eid, 'restSeconds': 90, 'sets': [rset(), rset()]}
    d.update(kw); return d
def rt(rid, name, rexes):
    return {'id': rid, 'name': name, 'weekdays': [], 'createdAt': '2026-06-01T00:00:00.000Z', 'updatedAt': '2026-06-01T00:00:00.000Z', 'exercises': rexes}
def base(extra_rex=None, equiv=True):
    exercises = [mex(X, 'Presse inde fab', gymEquivalentId=E if equiv else None), mex(Y, 'Presse onair fab'), mex(Z, 'Leg extension fab'),
                 mex(E, 'Fente fab'), mex(W, 'Mollets fab'), mex(L, 'Squat fab', 'Lifting', oneRepMax=100)]
    if not equiv: exercises[0].pop('gymEquivalentId')
    r1 = [rex('rx-x', X), rex('rx-z', Z), rex('rx-l', L)] + (extra_rex or [])
    return {'exercises': exercises, 'routines': [rt('r-a', 'Routine A fab', r1), rt('r-b', 'Routine B fab', [rex('rx-b', X)])],
            'sessions': [], 'settings': {'unit': 'kg', 'restTimerSeconds': 90, 'lastExportAt': None}, 'forceCycles': {}, 'meta': {'schemaVersion': 2}}
def routines(page): return {r['id']: r for r in jget(page, 'ovryk.routines')}
def slot(page, rid, rexid): return [x for x in routines(page)[rid]['exercises'] if x['id'] == rexid][0]
def onair(page, rid='r-a', rexid='rx-x'):
    s_ = slot(page, rid, rexid); return s_.get('onairExerciseId', 'ABSENT')
def editor(page, name='Routine A fab'):
    page.click('.nav-btn[data-target="routine"]'); page.wait_for_timeout(300)
    page.locator('.routine-row', has_text=name).first.locator('.routine-row-main').click(); page.wait_for_timeout(400)
def block(page, name): return page.locator('#routine-editor-view .routine-exercise-block', has_text=name).first
def open_slot(page, name='Presse inde fab'):
    block(page, name).locator('.rex-summary-row').click(); page.wait_for_timeout(300)
def close_slot(page): page.click('#routine-exercise-settings-back-btn'); page.wait_for_timeout(300)
def onair_row(page): return page.locator('#rex-settings-onair-btn')
def open_choice(page): onair_row(page).click(); page.wait_for_timeout(250)
def option(page, eid): return page.locator('#routine-onair-list .equiv-option[data-exercise-id="%s"]' % eid)
def none_option(page): return page.locator('#routine-onair-list .equiv-option', has_text='Aucune machine').first
def save(page): page.click('#routine-onair-save-btn'); page.wait_for_timeout(300)
def message(page): return page.inner_text('#routine-onair-message') if page.is_visible('#routine-onair-message') else ''
def no_overflow(page, sel):
    return page.evaluate("""(sel) => { const el = document.querySelector(sel);
      return document.documentElement.scrollWidth <= 390 && el.scrollWidth <= el.clientWidth + 1
        && Array.from(el.querySelectorAll('*')).every(c => c.getBoundingClientRect().right <= 391); }""", sel)
def choose(page, eid, name='Presse inde fab'):
    open_slot(page, name); open_choice(page); option(page, eid).click(); page.wait_for_timeout(150); save(page); close_slot(page)
def launch(page, gym):
    page.click('.nav-btn[data-target="seance"]'); page.wait_for_timeout(300)
    pill = page.locator('#seance-gym-wrap .gym-switch')
    if pill.get_attribute('data-gym') != gym: pill.click(); page.wait_for_timeout(200)
    page.locator('#seance-routine-list .routine-row-main', has_text='Routine A fab').first.click(); page.wait_for_timeout(700)
    live = [x for x in jget(page, 'ovryk.sessions') if x['status'] == 'in_progress'][0]
    return [(c['exerciseId'], c.get('replacesExerciseId')) for c in live['exercises']]

with sync_playwright() as p:
    b = p.chromium.launch()

    # O1, O2, O3 : section, écran de choix, écriture d'un seul champ, affichage, rechargement, retrait
    ctx, page, errors = fresh(b, base())
    before = data(page)
    editor(page); open_slot(page)
    check(onair_row(page).count() == 1 and onair_row(page).inner_text().strip() == 'Machine à On Air · Aucune (même exercice)' and data(page) == before,
          'O1 section "Machine à On Air · Aucune (même exercice)", aucune écriture à l\'ouverture')
    open_choice(page)
    ids = page.evaluate("() => Array.from(document.querySelectorAll('#routine-onair-list .equiv-option')).map(b => b.getAttribute('data-exercise-id'))")
    texts = page.locator('#routine-onair-list').inner_text() + page.locator('#routine-onair-page').inner_text()
    check(ids[0] is None and X not in ids and L not in ids and all(i in ids for i in (Y, Z, E, W)) and 'Créer' not in texts and none_option(page).get_attribute('aria-pressed') == 'true',
          'O2 liste : "Aucune machine" en tête et sélectionnée, ni l\'exercice du créneau ni un Lifting, aucun bouton de création')
    check(no_overflow(page, '#routine-onair-page'), 'O8 écran de choix à 390 px sans débordement')
    page.screenshot(path=str(F / 'onair-choix-390.png'))
    option(page, Y).click(); page.wait_for_timeout(150)
    page.click('#routine-onair-cancel-btn'); page.wait_for_timeout(200)
    check(data(page) == before and not errors, 'O2 choix puis Fermer : aucune écriture')
    open_choice(page); option(page, Y).click(); page.wait_for_timeout(150)
    page.evaluate("() => { const b = document.getElementById('routine-onair-save-btn'); b.click(); b.click(); }"); page.wait_for_timeout(300)
    after = data(page)
    exp = copy.deepcopy(json.loads(before['ovryk.routines'])); exp[0]['exercises'][0]['onairExerciseId'] = Y
    check(json.loads(after['ovryk.routines']) == exp and {k: v for k, v in after.items() if k != 'ovryk.routines'} == {k: v for k, v in before.items() if k != 'ovryk.routines'},
          'O2 Enregistrer (double tap) : seul rx-x.onairExerciseId écrit, updatedAt et tout le reste intacts')
    check(page.is_hidden('#routine-onair-page') and onair_row(page).inner_text().strip() == 'Machine à On Air · Presse onair fab' and no_overflow(page, '#routine-exercise-settings-page'),
          'O3 réglages : "Machine à On Air · Presse onair fab", 390 px sans débordement')
    page.screenshot(path=str(F / 'onair-reglages-390.png'))
    close_slot(page)
    check('On Air : Presse onair fab' in block(page, 'Presse inde fab').locator('.rex-summary-row').inner_text()
          and 'On Air' not in block(page, 'Leg extension fab').locator('.rex-summary-row').inner_text(),
          'O3 résumé du créneau dans l\'éditeur : "On Air : Presse onair fab", rien sur les autres créneaux')
    page.reload(); page.wait_for_timeout(500); page.reload(); page.wait_for_timeout(500)
    check(onair(page) == Y and not errors, 'O3 après deux démarrages (migrateSchema) : choix conservé')
    editor(page); open_slot(page); open_choice(page)
    check(option(page, Y).get_attribute('aria-pressed') == 'true', 'O3 réouverture : la machine enregistrée est présélectionnée')
    none_option(page).click(); page.wait_for_timeout(150); save(page)
    check(onair(page) is None and onair_row(page).inner_text().strip() == 'Machine à On Air · Aucune (même exercice)'
          and routines(page)['r-a']['updatedAt'] == '2026-06-01T00:00:00.000Z', 'O3 retrait : champ à null, "Aucune", updatedAt intact')
    close_slot(page)
    before = data(page)
    open_slot(page, 'Leg extension fab'); open_choice(page); save(page)
    check(data(page) == before and onair(page, 'r-a', 'rx-z') == 'ABSENT', 'O3 "Aucune machine" sur un créneau sans choix : rien écrit, champ toujours absent')
    close_slot(page)
    check(block(page, 'Squat fab').count() == 1, 'O1 (préalable) le créneau Lifting est dans l\'éditeur')
    ctx.close()

    # O1 : mouvement (Lifting) : pas de section (réglages ouverts directement par l'état de l'écran)
    ctx, page, errors = fresh(b, base())
    editor(page)
    has_summary = block(page, 'Squat fab').locator('.rex-summary-row').count()
    if has_summary:
        block(page, 'Squat fab').locator('.rex-summary-row').click(); page.wait_for_timeout(300)
    check(onair_row(page).count() == 0 and not errors, 'O1 mouvement (Lifting) : aucune section "Machine à On Air" (résumé présent : %s)' % bool(has_summary))
    ctx.close()

    # O4 : machine introuvable, choix devenu invalide au moment d'écrire
    d = base(); d['routines'][0]['exercises'][0]['onairExerciseId'] = 'ex-absent'
    ctx, page, errors = fresh(b, d)
    before = data(page)
    editor(page)
    summ = block(page, 'Presse inde fab').locator('.rex-summary-row').inner_text()
    open_slot(page)
    row = onair_row(page).inner_text().strip()
    open_choice(page)
    check('On Air : Machine introuvable' in summ and row == 'Machine à On Air · Machine introuvable' and 'Machine introuvable' in message(page)
          and none_option(page).get_attribute('aria-pressed') == 'true' and data(page) == before and not errors,
          'O4 machine introuvable : affichée (résumé, réglages, écran de choix), aucune écriture')
    page.click('#routine-onair-cancel-btn'); page.wait_for_timeout(200)
    check(data(page) == before, 'O4 Fermer : le champ introuvable est conservé tel quel')
    open_choice(page); option(page, W).click(); page.wait_for_timeout(150)
    page.evaluate("""() => { const l = JSON.parse(localStorage.getItem('ovryk.exercises'));
      l.forEach(e => { if (e.id === 'ex-w') { e.category = 'Lifting'; } }); localStorage.setItem('ovryk.exercises', JSON.stringify(l)); }""")
    before = data(page); save(page)
    check(data(page) == before and 'ne peut pas servir de machine à On Air' in message(page) and 'Rien n’a été enregistré' in message(page),
          'O4 cible devenue Lifting entre le choix et Enregistrer : refus, rien écrit (%s)' % message(page)[:60])
    ctx.close()

    # O5 : conservation du champ par chaque chemin de l'éditeur, sans recharger
    ctx, page, errors = fresh(b, base())
    editor(page); choose(page, Y)
    def kept(label):
        check(onair(page) == Y and not errors, 'O5 %s : champ conservé (%s)' % (label, onair(page)))
    page.fill('#routine-name-input', 'Routine A fab renommee'); page.dispatch_event('#routine-name-input', 'change'); page.wait_for_timeout(250)
    kept('renommer la routine')
    page.click('#routine-weekday-btn'); page.wait_for_timeout(200); page.locator('#routine-weekday-sheet-list .weekday-sheet-row').first.click()
    page.click('#routine-weekday-sheet-confirm'); page.wait_for_timeout(250)
    kept('changer les jours')
    block(page, 'Presse inde fab').locator('.rex-move-btn[aria-label="Descendre"]').click(); page.wait_for_timeout(250)
    order = [x['id'] for x in routines(page)['r-a']['exercises']]
    check(order[:2] == ['rx-z', 'rx-x'], 'O5 (préalable) descendre : ordre %s' % order)
    kept('descendre')
    block(page, 'Presse inde fab').locator('.rex-move-btn[aria-label="Monter"]').click(); page.wait_for_timeout(250)
    kept('monter')
    block(page, 'Presse inde fab').locator('[aria-label="Grouper avec le suivant"]').click(); page.wait_for_timeout(250)
    g = slot(page, 'r-a', 'rx-x')
    check(bool(g.get('groupId')), 'O5 (préalable) grouper : groupId posé')
    kept('grouper en superset')
    page.locator('#routine-editor-view .exercise-group .rep-type-btn', has_text='Circuit').first.click(); page.wait_for_timeout(250)
    check(slot(page, 'r-a', 'rx-x').get('groupType') == 'circuit', 'O5 (préalable) type circuit')
    kept('changer le type du groupe')
    page.locator('#routine-editor-view .exercise-group-dissolve').first.click(); page.wait_for_timeout(250)
    check(slot(page, 'r-a', 'rx-x').get('groupId') is None, 'O5 (préalable) dissoudre')
    kept('dissoudre le groupe')
    inp = block(page, 'Presse inde fab').locator('.load-input').first
    inp.fill('57'); inp.press('Tab'); page.wait_for_timeout(250)
    check(slot(page, 'r-a', 'rx-x')['sets'][0]['weightKg'] == 57, 'O5 (préalable) kilos saisis : %s' % slot(page, 'r-a', 'rx-x')['sets'][0].get('weightKg'))
    kept('saisir des kilos')
    block(page, 'Presse inde fab').locator('.rest-time-btn').first.click(); page.wait_for_timeout(250)
    page.click('#rest-picker-done'); page.wait_for_timeout(250)
    kept('valider le repos')
    page.click('#routine-add-exercise-btn'); page.wait_for_timeout(300)
    page.locator('#picker-exercise-list .picker-row', has_text='Mollets fab').first.click(); page.wait_for_timeout(150)
    page.click('#picker-confirm-btn'); page.wait_for_timeout(400)
    check(any(x['exerciseId'] == W for x in routines(page)['r-a']['exercises']), 'O5 (préalable) ajout de Mollets')
    kept('ajouter un exercice')
    block(page, 'Leg extension fab').locator('.rex-remove-btn').click(); page.wait_for_timeout(300)
    if page.is_visible('#confirm-modal-overlay'): page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    check(not any(x['id'] == 'rx-z' for x in routines(page)['r-a']['exercises']), 'O5 (préalable) retrait de Leg extension')
    kept('retirer un autre créneau')
    page.click('#routine-save-btn-bottom'); page.wait_for_timeout(400)
    kept('Enregistrer l\'éditeur')
    ctx.close()

    # O5 : duplication
    d = base(); d['routines'][0]['exercises'][0]['onairExerciseId'] = Y; d['routines'][0]['exercises'][1]['onairExerciseId'] = None
    ctx, page, errors = fresh(b, d)
    page.click('.nav-btn[data-target="routine"]'); page.wait_for_timeout(300)
    page.locator('.routine-row', has_text='Routine A fab').first.locator('.routine-action-btn', has_text='Dupliquer').click(); page.wait_for_timeout(400)
    rs = jget(page, 'ovryk.routines')
    dup = [r for r in rs if r['name'] == 'Routine A fab (copie)']
    src = [r for r in rs if r['id'] == 'r-a'][0]
    dx = dup[0]['exercises'] if dup else []
    check(len(dup) == 1 and dx[0].get('onairExerciseId') == Y and dx[1].get('onairExerciseId', 'ABSENT') is None and 'onairExerciseId' not in dx[2]
          and dx[0]['id'] != 'rx-x' and src['exercises'][0]['onairExerciseId'] == Y and not errors,
          'O5 dupliquer : choix copié (Y, null, absent conservés tels quels), source intacte')
    ctx.close()

    # O5 : remplacement de la 3a (copie de toutes les clés du créneau) : champ conservé, sans effet (créneau Lifting)
    PC = 'ex-pc'
    pend = {'exercise_id': L, 'cycle_actif': 'C', 'one_rm_actuel': 110, 'semaine_actuelle': 6,
            'historique_1rm': [{'date': '2026-08-01T10:00:00.000Z', 'valeur': 100}, {'date': '2026-09-12T10:00:00.000Z', 'valeur': 110}],
            'historique_cycles': [{'cycle': 'C', 'debut': '2026-08-01T10:00:00.000Z', 'fin': '2026-09-12T10:00:00.000Z', 'seances': 6, 'seances_prevues': 6,
                                   'reussite_pct': 90, 'one_rm_avant': 100, 'one_rm_apres': 110}],
            'prochain_cycle': 'D', 'en_attente_de_validation': True, 'semaines_modifiees': {}, 'test_report_used': False, 'decalage_semaines': 0}
    d = base(); d['exercises'].append(mex(PC, 'Power Clean fab', 'Lifting', oneRepMax=70)); d['forceCycles'] = {L: pend}
    d['routines'][0]['exercises'][2]['onairExerciseId'] = Y
    ctx, page, errors = fresh(b, d)
    page.click('.nav-btn[data-target="exercices"]'); page.wait_for_timeout(300)
    page.locator('.exercise-row', has_text='Squat fab').first.locator('.cycle-active-badge').click(); page.wait_for_timeout(300)
    page.click('#cycle-end-swap-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(500)
    s3 = slot(page, 'r-a', 'rx-l')
    check(s3['exerciseId'] == PC and s3.get('onairExerciseId') == Y and not errors, 'O5 remplacement de la 3a : champ copié tel quel (créneau Lifting, sans effet)')
    ctx.close()

    # O6 : export puis restauration, ancien export sans le champ
    d = base(); d['routines'][0]['exercises'][0]['onairExerciseId'] = Y
    ctx, page, errors = fresh(b, d)
    downloads = []; page.on('download', lambda x: downloads.append(x))
    settings(page); page.click('#dashboard-export-btn'); page.wait_for_timeout(800)
    exported = F / 'export-onair.json'; downloads[0].save_as(str(exported))
    env = json.loads(exported.read_text(encoding='utf-8'))
    check(env['data']['routines'][0]['exercises'][0].get('onairExerciseId') == Y and not errors, 'O6 le fichier exporté contient onairExerciseId')
    ctx.close()
    ctx, page, errors = fresh(b, dataset('tel', 2))
    settings(page); import_file(page, exported); confirm_restore(page); wait_reload(page)
    check(onair(page) == Y and not errors, 'O6 restauration de l\'export (autre téléphone) : choix conservé')
    ctx.close()
    old = base()
    f = write_file(F, 'ancien-sans-onair.json', envelope(old))
    ctx, page, errors = fresh(b, dataset('tel', 2))
    settings(page); import_file(page, f); confirm_restore(page); wait_reload(page)
    check(all('onairExerciseId' not in x for r in jget(page, 'ovryk.routines') for x in r['exercises']) and json.loads(data(page)['ovryk.routines']) == old['routines'] and not errors,
          'O6 ancien export sans le champ : restauré à l\'identique, aucun champ ajouté')
    ctx.close()

    # O7 : livraison 1 : séances construites comme avant, avec ou sans choix, dans les deux salles
    results = {}
    for label, with_choice in (('sans choix', False), ('avec choix', True)):
        for gym in ('onair', 'inde'):
            d = base()
            if with_choice: d['routines'][0]['exercises'][0]['onairExerciseId'] = Y
            ctx, page, errors = fresh(b, d)
            results[(label, gym)] = (launch(page, gym), errors[:1])
            ctx.close()
    check(results[('sans choix', 'onair')] == results[('avec choix', 'onair')] and results[('sans choix', 'inde')] == results[('avec choix', 'inde')]
          and results[('avec choix', 'onair')][0][0] == (X, None) and results[('avec choix', 'inde')][0][0] == (E, X),
          'O7 livraison 1 : séances identiques avec ou sans choix (On Air : X tel quel ; indé : équivalent du lot 18) : %s' % results[('avec choix', 'onair')][0][:2])

    b.close()
done()
