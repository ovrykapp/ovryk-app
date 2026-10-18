"""Carte de la séance du jour (Accueil) : la liste des exercices suit la pastille de salle.
A1 créneau avec machine On Air : pastille On Air = machine + "Remplace <créneau>", pastille Indé = exercice du créneau, sans sous-ligne.
A2 créneau sans choix et sans équivalent : même nom dans les deux salles, séries et reps du créneau inchangés.
A3 créneau sans choix avec équivalent de la fiche (lot 18) : En indé = équivalent + "Remplace", On Air = exercice du créneau.
A4 la liste se redessine à chaque bascule, lecture seule (aucune écriture à la bascule), séries et reps toujours ceux du créneau.
A5 le créneau avec cycle garde son affichage de cycle (jamais remplacé) ; 390 px sans débordement.
Données FABRIQUÉES ici. Usage : python3 test_accueil_salle.py <dossier de travail>, site servi sur http://127.0.0.1:8765."""
import json
from playwright.sync_api import sync_playwright
from restore_commun import *

F = workdir()
X, Y, Z, E, L = 'ex-x', 'ex-y', 'ex-z', 'ex-e', 'ex-l'
def mex(eid, name, cat='Jambes', **kw):
    d = {'id': eid, 'name': name, 'category': cat, 'equipment': 'Machine', 'unit': 'kg', 'isCustom': True}
    if cat == 'Lifting': d['liftBaseMode'] = 'force'
    d.update(kw); return d
def rset(lo=8, hi=10): return {'repType': 'range', 'repsMin': lo, 'repsMax': hi, 'weightKg': 50, 'repsActual': None, 'done': False}
def rex(rid, eid, n=3, **kw):
    d = {'id': rid, 'exerciseId': eid, 'restSeconds': 90, 'sets': [rset() for _ in range(n)]}; d.update(kw); return d
def dset(cycle=False):
    ex_ = [mex(X, 'Presse inde fab'), mex(Y, 'Presse onair fab'), mex(Z, 'Leg extension fab'), mex(E, 'Fente fab'), mex('ex-q', 'Curl fab', gymEquivalentId=E),
           mex(L, 'Squat fab', 'Lifting', oneRepMax=100 if cycle else None)]
    rts = [{'id': 'r-a', 'name': 'Routine A fab', 'weekdays': [], 'createdAt': '2026-06-01T00:00:00.000Z', 'updatedAt': '2026-06-01T00:00:00.000Z',
            'exercises': [rex('rx-x', X, onairExerciseId=Y), rex('rx-z', Z, 4), rex('rx-q', 'ex-q', 2), rex('rx-l', L, 1)]}]
    cyc = {}
    if cycle:
        cyc = {L: {'exercise_id': L, 'cycle_actif': '1', 'one_rm_actuel': 100, 'semaine_actuelle': 2, 'historique_1rm': [{'date': '2026-08-01T10:00:00.000Z', 'valeur': 100}],
                   'historique_cycles': [], 'prochain_cycle': None, 'en_attente_de_validation': False, 'semaines_modifiees': {}, 'test_report_used': False, 'decalage_semaines': 0}}
    return {'exercises': ex_, 'routines': rts, 'sessions': [], 'settings': {'unit': 'kg', 'restTimerSeconds': 90, 'lastExportAt': None}, 'forceCycles': cyc, 'meta': {'schemaVersion': 2}}
def rows(page):
    return page.evaluate("""() => Array.from(document.querySelectorAll('#dash-session-exercises .dash-session-ex-row')).map(r => ({
      name: (r.querySelector('.dash-session-ex-name').childNodes[0] || {}).textContent || '',
      sub: (r.querySelector('.dash-session-ex-sub') || {}).textContent || '', value: r.querySelector('.dash-session-ex-value').textContent.trim() }))""")
def pill(page): return page.locator('#dash-gym-wrap .gym-switch')
def set_gym(page, gym):
    if pill(page).get_attribute('data-gym') != gym: pill(page).click(); page.wait_for_timeout(250)
def no_overflow(page):
    return page.evaluate("""() => { const el = document.getElementById('dash-session-card');
      return document.documentElement.scrollWidth <= 390 && el.scrollWidth <= el.clientWidth + 1
        && Array.from(el.querySelectorAll('*')).every(c => c.getBoundingClientRect().right <= 391); }""")

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, page, errors = fresh(b, dset(cycle=True))
    page.click('.nav-btn[data-target="dashboard"]'); page.wait_for_timeout(400)
    before = ls(page)
    set_gym(page, 'onair'); on = rows(page)
    set_gym(page, 'inde'); ind = rows(page)
    set_gym(page, 'onair'); on2 = rows(page)
    names_on = [r['name'] for r in on[:3]]; names_in = [r['name'] for r in ind[:3]]
    check(on[0]['name'] == 'Presse onair fab' and on[0]['sub'] == 'Remplace Presse inde fab' and on[0]['value'] == '3 x 8-10',
          'A1 On Air : machine "Presse onair fab" + "Remplace Presse inde fab", série du créneau 3 x 8-10 (%s)' % on[0])
    check(ind[0]['name'] == 'Presse inde fab' and ind[0]['sub'] == '' and ind[0]['value'] == '3 x 8-10', 'A1 Indé : exercice du créneau, aucune sous-ligne (%s)' % ind[0])
    check(on[1] == ind[1] == {'name': 'Leg extension fab', 'sub': '', 'value': '4 x 8-10'}, 'A2 créneau sans choix ni équivalent : identique dans les deux salles (%s)' % on[1])
    check(on[2]['name'] == 'Curl fab' and on[2]['sub'] == '' and ind[2]['name'] == 'Fente fab' and ind[2]['sub'] == 'Remplace Curl fab' and on[2]['value'] == ind[2]['value'] == '2 x 8-10',
          'A3 équivalent de la fiche (lot 18) : indé = Fente fab + "Remplace Curl fab" (l\'affichage change aussi en indé), On Air = Curl fab')
    check(on2 == on and ls(page) == before and not errors, 'A4 aller-retour de pastille : liste identique, aucune écriture')
    check(on[3]['name'] == 'Squat fab' and ind[3] == on[3] and ' %' in on[3]['value'] and on[3]['sub'] == '', 'A5 créneau avec cycle : affichage de cycle inchangé dans les deux salles (%s)' % on[3])
    check(no_overflow(page), 'A5 carte à 390 px sans débordement')
    set_gym(page, 'onair')
    page.screenshot(path=str(F / 'accueil-onair-390.png'))
    set_gym(page, 'inde')
    page.screenshot(path=str(F / 'accueil-inde-390.png'))
    ctx.close()
    b.close()
done()
