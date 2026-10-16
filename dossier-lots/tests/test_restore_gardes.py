"""Gardes de lecture (mini-lot) : un exercice de séance sans liste de séries, dans une séance de la
SEMAINE EN COURS, ne fait plus planter la tuile "Volume cette semaine" de l'Accueil (sessionVolume).
G1 : semaine saine : volume strictement égal à la valeur calculée à la main (2290 kg, identique avant
     et après la garde) ; même semaine avec l'exercice sans séries ajouté : aucune erreur, volume
     inchangé (l'exercice compte zéro), séance comptée, tour des onglets sans erreur, et les six clés
     ovryk.* identiques octet pour octet au rechargement (lecture tolérante, rien n'est réécrit).
Données FABRIQUÉES ici. Usage : python3 test_restore_gardes.py <dossier de travail>."""
import copy
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
from restore_commun import *

F = workdir()
TODAY = datetime.now(timezone.utc).strftime('%Y-%m-%dT08:00:00.000Z')
# volume attendu, calculé à la main : séance 1 = 8 x 62,5 + 6 x 70 (la 3e série n'est pas faite) = 920 ;
# séance 2 = 920 + une série en plage 8-10 reps à 50 kg (milieu de plage : 9 x 50 = 450) ; total 920 + 1370 = 2290
EXPECTED_KG = 2290

def week_data():
    d = dataset('sem', 2, 20)
    for i, s in enumerate(d['sessions']):
        s['date'] = s['startedAt'] = s['completedAt'] = TODAY
        s['exercises'][0]['sets'] = [{'reps': 8, 'weightKg': 62.5, 'done': True}, {'reps': 6, 'weightKg': 70, 'done': True},
                                     {'reps': 6, 'weightKg': 70, 'done': False}]
        if i == 1:
            s['exercises'].append({'id': 'sex-plage', 'exerciseId': 'ex-fab-1', 'exerciseName': 'Plage', 'category': 'Pectoraux', 'restSeconds': 90,
                                   'sets': [{'repType': 'range', 'repsMin': 8, 'repsMax': 10, 'weightKg': 50, 'done': True}]})
    return d
def with_defect(d):
    d = copy.deepcopy(d)
    s = done_session('s-sem-sanssets', 21); s['date'] = s['startedAt'] = s['completedAt'] = TODAY
    s['exercises'][0].pop('sets')
    d['sessions'].append(s)
    return d
def tiles(page): return page.text_content('#dash-week-count').strip(), page.text_content('#dash-week-volume').strip()

with sync_playwright() as p:
    b = p.chromium.launch()
    control_fixtures(b, F)

    ctx, page, errors = fresh(b, week_data()); home(page)
    count, vol = tiles(page)
    check(vol == '%d kg' % EXPECTED_KG and count == '2' and not errors,
          'G1 semaine saine : volume "%s" (attendu %d kg, valeur calculée à la main), %s séances, aucune erreur' % (vol, EXPECTED_KG, count))
    ctx.close()

    ctx, page, errors = fresh(b, with_defect(week_data())); home(page)
    count, vol = tiles(page)
    ok_tiles = vol == '%d kg' % EXPECTED_KG and count == '3'
    for t in ('routine', 'seance', 'progression', 'exercices'):
        page.click('.nav-btn[data-target="%s"]' % t); page.wait_for_timeout(250)
    settings(page); home(page)
    page.click('.nav-btn[data-target="progression"]'); page.wait_for_timeout(250)
    page.click('#history-open-btn'); page.wait_for_timeout(300)
    page.locator('#history-list .history-row').first.click(); page.wait_for_timeout(300)
    before = data(page)
    page.reload(); page.wait_for_timeout(500); home(page)
    count2, vol2 = tiles(page)
    check(ok_tiles and (count2, vol2) == (count, vol) and not errors and data(page) == before and 'ovryk.sessions' in before
          and '"sex-s-sem-sanssets"' in before['ovryk.sessions'],
          'G1 exercice sans séries, séance de la semaine : Accueil "%s" / %s séances (volume inchangé), 4 onglets, Réglages et historique sans erreur, '
          'clés ovryk.* identiques octet pour octet après rechargement' % (vol, count))
    check(not page.net, 'aucun appel réseau')
    ctx.close()

    b.close()
done()
