"""Carte de la séance du jour (Accueil). v170 : une seule salle, On Air, plus de pastille.
A1 créneau avec machine On Air : l'Accueil montre la machine, sans sous-ligne "Remplace" ; logique Indé (appelée avec 'inde') :
   exercice du créneau, aucun remplacement.
A2 créneau sans choix et sans équivalent : même exercice dans les deux salles (logique), séries et reps du créneau.
A3 créneau sans choix avec équivalent de la fiche (lot 18) : On Air = exercice du créneau à l'écran ; logique Indé = équivalent qui remplace.
A4 aucune pastille ni ligne "N remplacé(s)" sur l'Accueil, aucune écriture à l'affichage ni par la logique Indé.
A5 le créneau avec cycle garde son affichage de cycle (jamais remplacé) ; 390 px sans débordement.
Refonte de l'accueil : cartes "Au programme", valeur "séries × reps visées", charge et % dans .dash-prog-load.
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
      sub: (r.querySelector('.dash-session-ex-sub') || {}).textContent || '', value: r.querySelector('.dash-session-ex-value').textContent.trim(),
      load: (r.querySelector('.dash-prog-load') || {}).textContent || '' }))""")
def logic(page, gym):
    """logique des deux salles, gardée en place : séance construite sans écriture (window.__ovrykTest)"""
    return page.evaluate("g => window.__ovrykTest.buildSessionCards('r-a', g)", gym)
def no_overflow(page):
    return page.evaluate("""() => { const el = document.getElementById('dash-session-card');
      return document.documentElement.scrollWidth <= 390 && el.scrollWidth <= el.clientWidth + 1
        && Array.from(el.querySelectorAll('*')).every(c => c.getBoundingClientRect().right <= 391); }""")

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, page, errors = fresh(b, dset(cycle=True))
    page.click('.nav-btn[data-target="dashboard"]'); page.wait_for_timeout(400)
    before = ls(page)
    on = rows(page)
    ind = logic(page, 'inde'); on_l = logic(page, 'onair')
    check(on[0]['name'] == 'Presse onair fab' and on[0]['sub'] == '' and on[0]['value'] == '3 × 8',
          'A1 Accueil (On Air seul) : machine "Presse onair fab", aucune sous-ligne "Remplace", série du créneau 3 × 8 (%s)' % on[0])
    check(on_l[0]['exerciseId'] == 'ex-y' and on_l[0]['replacesExerciseId'] == 'ex-x' and ind[0]['exerciseId'] == 'ex-x' and ind[0]['replacesExerciseId'] is None,
          'A1 logique : On Air = machine qui remplace le créneau, Indé = exercice du créneau sans remplacement (%s / %s)' % (on_l[0]['exerciseId'], ind[0]['exerciseId']))
    check({k: on[1][k] for k in ('name', 'sub', 'value')} == {'name': 'Leg extension fab', 'sub': '', 'value': '4 × 8'} and ind[1]['exerciseId'] == on_l[1]['exerciseId'] == 'ex-z'
          and ind[1]['sets'] == on_l[1]['sets'] == 4, 'A2 créneau sans choix ni équivalent : même exercice dans les deux salles (%s)' % on[1])
    check(on[2]['name'] == 'Curl fab' and on[2]['sub'] == '' and on[2]['value'] == '2 × 8' and ind[2]['exerciseId'] == 'ex-e' and ind[2]['replacesExerciseId'] == 'ex-q'
          and on_l[2]['exerciseId'] == 'ex-q', 'A3 équivalent de la fiche : Accueil "Curl fab" (On Air), logique Indé "Fente fab" qui remplace "Curl fab"')
    no_pill = page.locator('#dash-gym-wrap .gym-switch').count() == 0 and not page.is_visible('#dash-gym-wrap') and 'remplacé' not in page.inner_text('#dash-session-card')
    check(no_pill and ls(page) == before and not errors, 'A4 aucune pastille ni ligne "N remplacé(s)", aucune écriture (affichage et logique Indé)')
    check(on[3]['name'] == 'Squat fab' and ' %' in on[3]['load'] and on[3]['sub'] == '' and ind[3]['exerciseId'] == on_l[3]['exerciseId'] == 'ex-l'
          and ind[3]['replacesExerciseId'] is None, 'A5 créneau avec cycle : affichage de cycle, jamais remplacé dans les deux salles (%s)' % on[3])
    check(no_overflow(page), 'A5 carte à 390 px sans débordement')
    page.screenshot(path=str(F / 'accueil-onair-390.png'))
    ctx.close()
    b.close()
done()
