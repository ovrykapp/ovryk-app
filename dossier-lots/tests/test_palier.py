"""Palier de montée, option "5 kg" (écran de réglages de l'exercice dans l'éditeur de routine).
P1 : les 4 boutons (1, 2, 2,5, 5) tiennent sur une ligne à 390 px, sans débordement, le palier actuel est actif.
P2 : choisir chaque palier l'écrit sur l'exercice (1, 2, 2,5, 5) et seulement celui-là ; 5 survit à un rechargement.
P3 : la montée de charge d'une séance (toutes les séries faites au haut de la plage) utilise le palier : 1, 2, 2,5 et 5 kg.
P4 : export puis restauration (dans un autre téléphone) gardent 5 ; un ancien export sans palier de 5 se restaure comme avant.
P5 : la valeur par défaut des exercices neufs et existants ne change pas (2,5 ; un palier déjà enregistré est conservé).
Données FABRIQUÉES ici. Usage : python3 test_palier.py <dossier de travail>, site servi sur http://127.0.0.1:8765."""
import json, re
from playwright.sync_api import sync_playwright
from restore_commun import *

F = workdir()
def rset(w, actual=None, done=False, lo=8, hi=10):
    return {'repType': 'range', 'repsMin': lo, 'repsMax': hi, 'weightKg': w, 'repsActual': actual, 'done': done}
def dset(step=None, hist=True, weight=60):
    e = ex('ex-pal', 'Presse palier fab', 'Jambes')
    if step is not None: e['progressionStep'] = step
    sessions = []
    if hist:
        sessions = [{'id': 's-pal', 'status': 'completed', 'date': '2026-09-01T10:00:00.000Z', 'startedAt': '2026-09-01T10:00:00.000Z',
                     'completedAt': '2026-09-01T11:00:00.000Z', 'durationSeconds': 3600, 'routineId': 'r-pal', 'routineName': 'Routine palier', 'notes': '',
                     'exercises': [{'id': 'sex-pal', 'exerciseId': 'ex-pal', 'exerciseName': 'Presse palier fab', 'category': 'Jambes', 'restSeconds': 90,
                                    'sets': [rset(weight, 10, True), rset(weight, 10, True)], 'groupId': None, 'groupType': None}]}]
    return {'exercises': [e], 'routines': [{'id': 'r-pal', 'name': 'Routine palier', 'weekdays': [], 'updatedAt': '2026-06-01T00:00:00.000Z',
                                            'exercises': [{'exerciseId': 'ex-pal', 'restSeconds': 90, 'sets': [rset(weight), rset(weight)]}]}],
            'sessions': sessions, 'settings': {'unit': 'kg', 'restTimerSeconds': 90, 'lastExportAt': None}, 'forceCycles': {}, 'meta': {'schemaVersion': 2}}
def step_of(page): return {e['id']: e for e in json.loads(ls(page)['ovryk.exercises'])}['ex-pal'].get('progressionStep')
def open_settings(page):
    page.click('.nav-btn[data-target="routine"]'); page.wait_for_timeout(300)
    page.locator('.routine-row', has_text='Routine palier').first.locator('.routine-row-main').click(); page.wait_for_timeout(400)
    page.locator('.rex-summary-row').first.click(); page.wait_for_timeout(300)
def btns(page): return page.locator('#routine-exercise-settings-body .rex-settings-step-row .rep-type-btn')
def labels(page): return [t.strip() for t in btns(page).all_text_contents()]
def active(page): return [t.strip() for t in page.locator('#routine-exercise-settings-body .rex-settings-step-row .rep-type-btn.active').all_text_contents()]
def no_overflow(page):
    return page.evaluate("""() => { const row = document.querySelector('#routine-exercise-settings-body .rex-settings-step-row');
      const r = row.getBoundingClientRect(); const kids = Array.from(row.children);
      const tops = new Set(kids.map(k => Math.round(k.getBoundingClientRect().top)));
      return kids.length === 4 && tops.size === 1 && r.left >= 0 && r.right <= 390.5 && row.scrollWidth <= row.clientWidth + 1
        && document.documentElement.scrollWidth <= 390 && kids.every(k => k.scrollWidth <= k.clientWidth + 1); }""")
def planned_weight(page):
    page.click('.nav-btn[data-target="seance"]'); page.wait_for_timeout(300)
    page.locator('#seance-routine-list .routine-row-main', has_text='Routine palier').first.click(); page.wait_for_timeout(700)
    live = [x for x in json.loads(ls(page)['ovryk.sessions']) if x['status'] == 'in_progress'][0]
    return [s['weightKg'] for s in live['exercises'][0]['sets']]

with sync_playwright() as p:
    b = p.chromium.launch()

    # P1, P2 : affichage à 390 px, choix de chaque palier, rechargement
    ctx, page, errors = fresh(b, dset(2.5))
    open_settings(page)
    check(labels(page) == ['1 kg', '2 kg', '2,5 kg', '5 kg'] and active(page) == ['2,5 kg'] and no_overflow(page) and not errors,
          'P1 quatre boutons sur une ligne à 390 px, sans débordement, 2,5 kg actif : %s' % labels(page))
    page.screenshot(path=str(F / 'palier-390.png'))
    before_other = {k: v for k, v in data(page).items() if k != 'ovryk.exercises'}
    for label, val in [('1 kg', 1), ('2 kg', 2), ('2,5 kg', 2.5), ('5 kg', 5)]:
        btns(page).filter(has_text=re.compile(r'^\s*' + re.escape(label) + r'\s*$')).first.click(); page.wait_for_timeout(250)
        check(step_of(page) == val and active(page) == [label] and no_overflow(page) and not errors,
              'P2 choix "%s" : palier %s écrit, bouton actif, une ligne' % (label, val))
    check({k: v for k, v in data(page).items() if k != 'ovryk.exercises'} == before_other, 'P2 seul l\'exercice est écrit (routines, séances, réglages, cycles intacts)')
    page.reload(); page.wait_for_timeout(500); page.reload(); page.wait_for_timeout(500)
    check(step_of(page) == 5, 'P2 après rechargement de l\'app : palier 5 conservé')
    open_settings(page)
    check(active(page) == ['5 kg'] and not errors, 'P2 après rechargement : "5 kg" actif sur l\'écran')
    ctx.close()

    # P3 : montée de charge d'une séance, un palier par exercice
    for step, expected in [(1, 61), (2, 62), (2.5, 62.5), (5, 65)]:
        ctx, page, errors = fresh(b, dset(step))
        w = planned_weight(page)
        check(w == [expected, expected] and not errors, 'P3 palier %s : séries à 60 kg tout au haut de la plage -> %s kg (%s)' % (step, expected, w))
        ctx.close()
    ctx, page, errors = fresh(b, dset(5, hist=False))
    w = planned_weight(page)
    check(w == [60, 60] and not errors, 'P3 palier 5 sans séance passée : charge de la routine inchangée (%s)' % w)
    ctx.close()
    ctx, page, errors = fresh(b, dset(5))
    sess = json.loads(ls(page)['ovryk.sessions'])
    sess[0]['exercises'][0]['sets'][1]['repsActual'] = 9
    jset(page, 'ovryk.sessions', sess); page.reload(); page.wait_for_timeout(500)
    w = planned_weight(page)
    check(w == [60, 60] and not errors, 'P3 palier 5, une série sous le haut de la plage : pas de montée (%s)' % w)
    ctx.close()

    # P4 : export puis restauration dans un autre téléphone ; ancien export sans palier de 5
    ctx, page, errors = fresh(b, dset(5))
    downloads = []; page.on('download', lambda d: downloads.append(d))
    settings(page); page.click('#dashboard-export-btn'); page.wait_for_timeout(800)
    exported = F / 'export-palier5.json'
    downloads[0].save_as(str(exported))
    env = json.loads(exported.read_text(encoding='utf-8'))
    check(len(downloads) == 1 and [e for e in env['data']['exercises'] if e['id'] == 'ex-pal'][0].get('progressionStep') == 5 and not errors,
          'P4 le fichier exporté contient progressionStep = 5')
    ctx.close()
    ctx, page, errors = fresh(b, dataset('tel', 2))
    settings(page); import_file(page, exported); confirm_restore(page); wait_reload(page)
    check(step_of(page) == 5 and not errors, 'P4 restauration de l\'export (autre téléphone) : palier 5 conservé (%s)' % step_of(page))
    open_settings(page)
    check(active(page) == ['5 kg'] and not errors, 'P4 après restauration : "5 kg" actif sur l\'écran')
    ctx.close()
    for step in (1, 2, 2.5):
        data_old = dset(step)
        f = write_file(F, 'ancien-%s.json' % str(step).replace('.', '_'), envelope(data_old))
        ctx, page, errors = fresh(b, dataset('tel', 2))
        settings(page); import_file(page, f); confirm_restore(page); wait_reload(page)
        check(step_of(page) == step and not errors, 'P4 ancien export avec palier %s : restauré tel quel (%s)' % (step, step_of(page)))
        ctx.close()

    # P5 : valeurs par défaut inchangées
    ctx, page, errors = fresh(b, dset(None))
    check(step_of(page) == 2.5 and jget(page, 'ovryk.settings').get('defaultProgressionStep') == 2.5 and not errors,
          'P5 exercice sans palier : complété à 2,5 (défaut inchangé)')
    open_settings(page)
    check(active(page) == ['2,5 kg'], 'P5 le défaut 2,5 est le bouton actif')
    ctx.close()
    ctx, page, errors = fresh(b, dset(2))
    check(step_of(page) == 2 and not errors, 'P5 exercice existant à 2 kg : palier conservé au démarrage')
    open_settings(page)
    check(active(page) == ['2 kg'], 'P5 existant à 2 kg : "2 kg" actif')
    ctx.close()
    ctx, page, errors = fresh(b, dset(3))
    open_settings(page)
    body = page.inner_text('#routine-exercise-settings-body')
    check(step_of(page) == 3 and active(page) == [] and 'Valeur actuelle non standard : 3 kg' in body and not errors,
          'P5 palier non standard (3) : conservé, aucun bouton actif, note affichée')
    ctx.close()

    b.close()
done()
