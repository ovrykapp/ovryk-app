"""Lot 18 : choix de la salle (Indé / On Air) et équivalents d'exercices.
Livraison 1 : champ exercise.gymEquivalentId et écran de la fiche exercice,
sans aucun changement des séances.
Données FABRIQUÉES ici : aucun vrai export, aucun appel réseau.
Usage : python3 test_gym.py <dossier de travail>, site servi sur http://127.0.0.1:8765."""
import sys, json
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright
SP = Path(sys.argv[1]); URL = 'http://127.0.0.1:8765/index.html'
F = SP / 'files'; F.mkdir(parents=True, exist_ok=True)
res = []
def check(c, m): res.append(bool(c)); print(('ok     ' if c else 'ECHEC  ') + m)
DATA_KEYS = ['ovryk.exercises', 'ovryk.routines', 'ovryk.sessions', 'ovryk.settings', 'ovryk.forceCycles', 'ovryk.meta']

# ---------- fixtures fabriquées ----------
def ex(eid, name, cat='Jambes', **kw):
    d = {'id': eid, 'name': name, 'category': cat, 'equipment': 'Machine', 'unit': 'kg', 'isCustom': True}
    d.update(kw); return d
def done_session(sid, day, exid='ex-x'):
    return {'id': sid, 'status': 'completed', 'date': '2026-09-%02dT10:00:00.000Z' % day, 'completedAt': '2026-09-%02dT11:00:00.000Z' % day,
            'startedAt': '2026-09-%02dT10:00:00.000Z' % day, 'routineId': 'r-fab', 'routineName': 'Routine fabriquee',
            'exercises': [{'id': 'sex-%s' % sid, 'exerciseId': exid, 'exerciseName': 'X', 'category': 'Jambes',
                           'restSeconds': 90, 'sets': [{'reps': 10, 'weight': 100, 'done': True}]}]}
def dataset():
    return {'exercises': [ex('ex-x', 'Presse fabriquee'), ex('ex-y', 'Hack squat fabrique'), ex('ex-z', 'Fente fabriquee'),
                          ex('ex-w', 'Leg extension fabrique'), ex('ex-l', 'Squat fabrique lifting', 'Lifting', liftBaseMode='force')],
            'routines': [{'id': 'r-fab', 'name': 'Routine fabriquee', 'weekdays': [], 'updatedAt': '2026-09-01T00:00:00.000Z',
                          'exercises': [{'exerciseId': 'ex-x', 'restSeconds': 90, 'sets': [{'reps': 10, 'weight': 100}, {'reps': 10, 'weight': 100}]}]}],
            'sessions': [done_session('s-1', 1)],
            'settings': {'unit': 'kg', 'restTimerSeconds': 90, 'lastExportAt': None}, 'forceCycles': {}, 'meta': {'schemaVersion': 2}}

def ls(page): return page.evaluate("() => { const o = {}; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); o[k] = localStorage.getItem(k); } return o; }")
def data(page): return {k: v for k, v in ls(page).items() if k in DATA_KEYS}
def jset(page, key, value): page.evaluate("([k, v]) => localStorage.setItem(k, v)", [key, json.dumps(value)])
def exs(page): return {e['id']: e for e in json.loads(ls(page)['ovryk.exercises'])}
def fresh(b, d=None):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', accept_downloads=True)
    page = ctx.new_page(); errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(URL); page.evaluate("() => localStorage.clear()")
    for k, v in (d or dataset()).items(): jset(page, 'ovryk.' + k, v)
    # deux démarrages : la migration existante complète le catalogue au premier, liftBaseMode au second
    page.reload(); page.wait_for_timeout(300); page.reload(); page.wait_for_timeout(300)
    return ctx, page, errors
def fiche(page, name):
    page.click('.nav-btn[data-target="exercices"]'); page.wait_for_timeout(250)
    page.locator('.exercise-row-name', has_text=name).first.click(); page.wait_for_timeout(300)
def equiv_row(page): return page.inner_text('#exercise-detail-equiv-btn') if page.locator('#exercise-detail-equiv-btn').count() and page.is_visible('#exercise-detail-equiv-btn') else ''
def open_equiv(page):
    page.click('#exercise-detail-equiv-btn'); page.wait_for_timeout(250)
def option(page, name): return page.locator('#exercise-equiv-list .equiv-option', has_text=name).first
def search(page, text):
    page.fill('#exercise-equiv-search', text); page.wait_for_timeout(150)

with sync_playwright() as p:
    b = p.chromium.launch()

    # G0 : rien écrit au lancement, à l'ouverture de la fiche ni de l'écran d'équivalent
    d = dataset(); d['exercises'][0]['gymEquivalentId'] = 'ex-y'
    ctx, page, errors = fresh(b, d)
    before = ls(page)
    page.reload(); page.wait_for_timeout(400)
    fiche(page, 'Presse fabriquee'); open_equiv(page); search(page, 'fente')
    page.click('#exercise-equiv-cancel-btn'); page.wait_for_timeout(200)
    check(ls(page) == before and not errors, 'G0 lancement, fiche, écran d\'équivalent puis Fermer : aucune écriture, aucune erreur (%s)' % errors[:1])
    ctx.close()

    # G1 : ligne visible pour un exercice de muscu ("Aucun"), absente pour un mouvement Lifting
    ctx, page, errors = fresh(b)
    fiche(page, 'Presse fabriquee')
    row_x = equiv_row(page)
    fiche(page, 'Squat fabrique lifting')
    row_l = equiv_row(page)
    check('Équivalent en salle indé · Aucun' in row_x and row_l == '', 'G1 fiche : "%s" pour la muscu, aucune ligne pour Lifting' % row_x)
    ctx.close()

    # G2 : choisir un équivalent : rien écrit avant Enregistrer, puis seul ex-x reçoit gymEquivalentId
    ctx, page, errors = fresh(b)
    fiche(page, 'Presse fabriquee'); open_equiv(page)
    names = page.locator('#exercise-equiv-list .equiv-option-name').all_inner_texts()
    check('Presse fabriquee' not in names and 'Squat fabrique lifting' not in names and names[0] == 'Aucun équivalent',
          'G2 liste : "Aucun équivalent" en tête, ni l\'exercice lui-même ni un Lifting (%d choix)' % len(names))
    before = data(page)
    search(page, 'hack'); option(page, 'Hack squat fabrique').click(); page.wait_for_timeout(150)
    check(data(page) == before and option(page, 'Hack squat fabrique').get_attribute('aria-pressed') == 'true', 'G2 choix fait, rien écrit avant Enregistrer')
    page.click('#exercise-equiv-save-btn'); page.wait_for_timeout(300)
    after = exs(page); old = {e['id']: e for e in json.loads(before['ovryk.exercises'])}
    changed = [k for k in after if json.dumps(after[k], sort_keys=True) != json.dumps(old.get(k), sort_keys=True)]
    others_same = all(data(page)[k] == before[k] for k in DATA_KEYS if k != 'ovryk.exercises')
    check(changed == ['ex-x'] and after['ex-x'].get('gymEquivalentId') == 'ex-y' and others_same,
          'G2 Enregistrer : seul ex-x modifié (gymEquivalentId = ex-y), autres clés intactes (%s)' % changed)
    check('Hack squat fabrique' in equiv_row(page) and page.is_hidden('#exercise-equiv-page'), 'G2 fiche : "%s"' % equiv_row(page))
    fiche(page, 'Hack squat fabrique')
    note = page.inner_text('#exercise-detail-equiv-sources') if page.locator('#exercise-detail-equiv-sources').count() else ''
    check('Presse fabriquee' in note, 'G2 fiche de la cible : "%s"' % note)

    # G3 : refus : la cible ne peut plus avoir d'équivalent ; pour un autre exercice, la cible qui a déjà un équivalent est refusée
    open_equiv(page)
    enabled = [o for o in page.locator('#exercise-equiv-list .equiv-option').all() if o.is_enabled()]
    labels = [o.inner_text() for o in enabled]
    msgs = page.locator('#exercise-equiv-list .equiv-option:disabled .equiv-option-sub').all_inner_texts()
    check(len(enabled) == 1 and 'Aucun équivalent' in labels[0] and msgs and 'déjà l’équivalent de « Presse fabriquee »' in msgs[0],
          'G3 cible d\'un autre : seul "Aucun équivalent" permis, raison affichée (%s)' % (msgs[:1]))
    page.click('#exercise-equiv-cancel-btn'); page.wait_for_timeout(150)
    fiche(page, 'Leg extension fabrique'); open_equiv(page)
    search(page, 'presse')
    o = option(page, 'Presse fabriquee')
    check(o.is_disabled() and 'déjà son propre équivalent' in o.inner_text(), 'G3 pas de chaîne : "Presse fabriquee" (qui a un équivalent) refusée comme cible')
    page.click('#exercise-equiv-cancel-btn'); page.wait_for_timeout(150)

    # G4 : retirer l'équivalent (champ mis à null), puis "Aucun" sur un exercice qui n'en a jamais eu : aucune écriture
    fiche(page, 'Presse fabriquee'); open_equiv(page)
    option(page, 'Aucun équivalent').click(); page.click('#exercise-equiv-save-btn'); page.wait_for_timeout(300)
    check(exs(page)['ex-x'].get('gymEquivalentId', 'absent') is None and 'Aucun' in equiv_row(page), 'G4 retrait : gymEquivalentId = null, fiche "Aucun"')
    fiche(page, 'Fente fabriquee'); open_equiv(page); before = ls(page)
    page.click('#exercise-equiv-save-btn'); page.wait_for_timeout(300)
    check(ls(page) == before and 'gymEquivalentId' not in exs(page)['ex-z'], 'G4 "Aucun" sur un exercice sans équivalent : rien écrit, champ toujours absent')
    ctx.close()

    # G5 : équivalent introuvable (fichier restauré où la cible manque) : affiché tel quel, rien écrit
    d = dataset(); d['exercises'][0]['gymEquivalentId'] = 'ex-absent'
    ctx, page, errors = fresh(b, d); before = ls(page)
    fiche(page, 'Presse fabriquee')
    check('Équivalent introuvable' in equiv_row(page) and ls(page) == before, 'G5 cible absente : "%s", rien écrit' % equiv_row(page))
    ctx.close()

    # G6 : l'état change entre le choix et Enregistrer (la cible reçoit un équivalent) : refus, rien écrit
    ctx, page, errors = fresh(b)
    fiche(page, 'Leg extension fabrique'); open_equiv(page)
    search(page, 'hack'); option(page, 'Hack squat fabrique').click()
    e = json.loads(ls(page)['ovryk.exercises'])
    for x in e:
        if x['id'] == 'ex-y': x['gymEquivalentId'] = 'ex-z'
    jset(page, 'ovryk.exercises', e); before = ls(page)
    page.click('#exercise-equiv-save-btn'); page.wait_for_timeout(300)
    msg = page.inner_text('#exercise-equiv-message') if page.is_visible('#exercise-equiv-message') else ''
    check('Rien n’a été enregistré' in msg and ls(page) == before and page.is_visible('#exercise-equiv-page'), 'G6 contrôle refait à l\'enregistrement : "%s"' % msg[:80])
    ctx.close()

    # G7 : aucune séance n'est changée par la livraison 1 : la routine lance toujours l'exercice d'origine, sans salle
    d = dataset(); d['exercises'][0]['gymEquivalentId'] = 'ex-y'
    ctx, page, errors = fresh(b, d)
    page.click('.nav-btn[data-target="seance"]'); page.wait_for_timeout(300)
    page.locator('#seance-routine-list .routine-row-main', has_text='Routine fabriquee').first.click(); page.wait_for_timeout(500)
    live = [s for s in json.loads(ls(page)['ovryk.sessions']) if s['status'] == 'in_progress']
    check(len(live) == 1 and [x['exerciseId'] for x in live[0]['exercises']] == ['ex-x'] and 'gym' not in live[0]
          and all('replacesExerciseId' not in x for x in live[0]['exercises']) and not errors,
          'G7 séance lancée : exercice d\'origine, aucun champ gym ni replacesExerciseId')
    ctx.close()

    # G8 : export avec le champ ; import d'un ancien fichier sans le champ : accepté, restauré, empreinte valide
    d = dataset(); d['exercises'][0]['gymEquivalentId'] = 'ex-y'
    ctx, page, errors = fresh(b, d)
    page.click('.nav-btn[data-target="dashboard"]'); page.wait_for_timeout(150); page.click('#dash-settings-btn'); page.wait_for_timeout(300)
    with page.expect_download() as dl: page.click('#dashboard-export-btn')
    path = F / 'fab-gym-export.json'; dl.value.save_as(str(path)); env = json.loads(path.read_text())
    x_exp = [x for x in env['data']['exercises'] if x['id'] == 'ex-x'][0]
    check(x_exp.get('gymEquivalentId') == 'ex-y' and env['summary'].get('checksum'), 'G8 export : gymEquivalentId présent, empreinte calculée')
    old = dataset(); old['exercises'] = [x for x in old['exercises']]
    old_env = {'app': 'Ovryk', 'exportedAt': '2026-10-01T08:30:00.000Z', 'version': 1, 'data': old}
    imp = F / 'fab-gym-ancien.json'; imp.write_text(json.dumps(old_env))
    page.set_input_files('#dashboard-import-input', str(imp)); page.wait_for_timeout(500)
    page.click('#restore-confirm-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(1500)
    restored = {x['id']: x for x in json.loads(ls(page)['ovryk.exercises'])}
    check('ex-x' in restored and 'gymEquivalentId' not in restored['ex-x'] and not errors, 'G8 ancien fichier sans le champ : restauré, champ absent, aucune erreur (%s)' % errors[:1])
    fiche(page, 'Presse fabriquee')
    check('Aucun' in equiv_row(page), 'G8 après restauration : fiche "%s"' % equiv_row(page))
    env2 = json.loads(path.read_text())
    imp2 = F / 'fab-gym-recent.json'; imp2.write_text(json.dumps(env2))
    page.click('.nav-btn[data-target="dashboard"]'); page.wait_for_timeout(150); page.click('#dash-settings-btn'); page.wait_for_timeout(300)
    page.set_input_files('#dashboard-import-input', str(imp2)); page.wait_for_timeout(500)
    refused = page.is_visible('#restore-confirm-btn') is False
    page.click('#restore-confirm-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(1500)
    check(not refused and {x['id']: x for x in json.loads(ls(page)['ovryk.exercises'])}['ex-x'].get('gymEquivalentId') == 'ex-y',
          'G8 fichier récent (avec le champ et son empreinte) : accepté et restauré')
    ctx.close()

    # G9 : 390 px : écran d'équivalent sans défilement horizontal, choix d'au moins 44 px
    ctx, page, errors = fresh(b)
    fiche(page, 'Presse fabriquee'); open_equiv(page)
    m = page.evaluate("""() => { const page = document.getElementById('exercise-equiv-page'); const opts = Array.from(document.querySelectorAll('#exercise-equiv-list .equiv-option'));
      let over = []; page.querySelectorAll('*').forEach(x => { const r = x.getBoundingClientRect(); if (r.width && r.right > 390.5) over.push(x.id || x.className); });
      return {sw: document.documentElement.scrollWidth, minH: Math.min.apply(null, opts.map(o => o.getBoundingClientRect().height)), over: over.slice(0, 3)}; }""")
    check(m['sw'] <= 390 and m['minH'] >= 44 and not m['over'], 'G9 390 px : largeur %s, hauteur minimale d\'un choix %s px, débordement %s' % (m['sw'], round(m['minH']), m['over']))
    ctx.close()

    b.close()

print('\n%d/%d' % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
