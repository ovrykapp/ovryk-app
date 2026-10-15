"""Lot 18 : choix de la salle (Indé / On Air) et équivalents d'exercices.
Livraison 1 : champ exercise.gymEquivalentId et écran de la fiche exercice,
sans aucun changement des séances.
Données FABRIQUÉES ici : aucun vrai export, aucun appel réseau.
Usage : python3 test_gym.py <dossier de travail>, site servi sur http://127.0.0.1:8765."""
import sys, json, re, subprocess
from datetime import datetime, timezone, timedelta
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
    # livraison 2a : la séance porte désormais sa salle (On Air par défaut, sans séance précédente), sans remplacement
    check(len(live) == 1 and [x['exerciseId'] for x in live[0]['exercises']] == ['ex-x'] and live[0].get('gym') == 'onair'
          and all('replacesExerciseId' not in x for x in live[0]['exercises']) and not errors,
          'G7 séance lancée (On Air par défaut) : exercice d\'origine, salle "onair", aucun replacesExerciseId')
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

    # ================= Livraison 2a : salle, remplacement à la construction, salle enregistrée et affichée =================
    def rset(w, actual=None, done=False, lo=8, hi=10):
        return {'repType': 'range', 'repsMin': lo, 'repsMax': hi, 'weightKg': w, 'repsActual': actual, 'done': done}
    def sess2(sid, date, gym, items, routine='r-salle'):
        d0 = date + 'T10:00:00.000Z'
        s = {'id': sid, 'status': 'completed', 'date': d0, 'startedAt': d0, 'completedAt': date + 'T11:00:00.000Z', 'durationSeconds': 3600,
             'routineId': routine, 'routineName': 'Routine salle', 'notes': '', 'exercises': []}
        if gym: s['gym'] = gym
        for i, it in enumerate(items):
            exid, name, sets = it[0], it[1], it[2]
            sex = {'id': 'sex-%s-%d' % (sid, i), 'exerciseId': exid, 'exerciseName': name, 'category': 'Jambes', 'restSeconds': 90, 'sets': sets, 'groupId': None, 'groupType': None}
            if len(it) > 3 and it[3]: sex['replacesExerciseId'] = it[3]
            s['exercises'].append(sex)
        return s
    def salle_dataset(sessions=None, weekdays=None, extra_rex=None):
        d = dataset()
        d['exercises'][0]['gymEquivalentId'] = 'ex-y'
        rex = [{'exerciseId': 'ex-x', 'restSeconds': 90, 'sets': [rset(100), rset(100), rset(100)]},
               {'exerciseId': 'ex-z', 'restSeconds': 60, 'sets': [rset(40), rset(40)]}]
        if extra_rex: rex += extra_rex
        d['routines'] = [{'id': 'r-salle', 'name': 'Routine salle', 'weekdays': weekdays or [], 'updatedAt': '2026-06-01T00:00:00.000Z', 'exercises': rex}]
        d['sessions'] = sessions or []
        return d
    def seance(page):
        page.click('.nav-btn[data-target="seance"]'); page.wait_for_timeout(300)
    def live(page):
        l = [x for x in json.loads(ls(page)['ovryk.sessions']) if x['status'] == 'in_progress']
        return l[0] if l else None
    def launch_start(page):
        seance(page); page.locator('#seance-routine-list .routine-row-main', has_text='Routine salle').first.click(); page.wait_for_timeout(600)
    def pill(page): return page.locator('#seance-gym-wrap .gym-switch')
    SHOTS = F

    # G10 : pilule de l'écran de départ : On Air par défaut, ARIA, 44 px, aucune écriture à la bascule, styles demandés
    ctx, page, errors = fresh(b, salle_dataset())
    seance(page)
    pl = pill(page)
    check(pl.get_attribute('role') == 'switch' and pl.get_attribute('aria-label') == 'Salle' and pl.get_attribute('aria-checked') == 'true' and pl.get_attribute('data-gym') == 'onair',
          'G10 pilule : role=switch, aria-label "Salle", On Air par défaut (aucune séance avec salle)')
    page.screenshot(path=str(SHOTS / 'depart-onair.png'))
    before = ls(page)
    pl.click(); page.wait_for_timeout(350)
    pl = pill(page)
    meta = page.locator('#seance-routine-list .routine-row-meta').first.inner_text()
    check(pl.get_attribute('aria-checked') == 'false' and pl.get_attribute('data-gym') == 'inde' and ls(page) == before and '1 remplacé en indé' in meta,
          'G10 bascule en Indé : aucune écriture, ligne de routine "%s"' % meta)
    page.screenshot(path=str(SHOTS / 'depart-inde.png'))
    st = page.evaluate("""() => { const b = document.querySelector('#seance-gym-wrap .gym-switch'); const t = b.querySelector('.gym-switch-thumb');
      const act = b.querySelector('.gym-switch-option[data-for="' + b.dataset.gym + '"]'); const ina = b.querySelector('.gym-switch-option:not([data-for="' + b.dataset.gym + '"])');
      const r = b.getBoundingClientRect(); const cs = getComputedStyle(b), ts = getComputedStyle(t);
      return {h: r.height, right: r.right, sw: document.documentElement.scrollWidth, bg: cs.backgroundColor, border: cs.borderTopColor, bw: cs.borderTopWidth,
              thumb: ts.backgroundColor, act: getComputedStyle(act).color, ina: getComputedStyle(ina).color,
              shadow: [cs.boxShadow, ts.boxShadow], img: [cs.backgroundImage, ts.backgroundImage],
              fits: Array.from(b.querySelectorAll('.gym-switch-option')).every(o => o.scrollWidth <= o.clientWidth)}; }""")
    check(st['h'] >= 44 and st['right'] <= 390 and st['sw'] <= 390 and st['fits'], 'G10 390 px : hauteur %s px, bord droit %s, noms lisibles %s' % (round(st['h']), round(st['right']), st['fits']))
    check(st['bg'] == 'rgb(17, 17, 16)' and st['border'] == 'rgb(58, 58, 53)' and st['bw'] == '1px' and st['thumb'] == 'rgb(255, 106, 43)'
          and st['act'] == 'rgb(17, 17, 16)' and st['shadow'] == ['none', 'none'] and st['img'] == ['none', 'none'],
          'G10 couleurs : fond Graphite, bordure --neutral-400, pastille Rouille, nom actif Graphite (%s), inactif %s, sans ombre ni dégradé' % (st['act'], st['ina']))

    # G11 : lancement en Indé depuis l'écran de départ : remplacement, salle enregistrée, en-tête et carte
    pill(page).click() if pill(page).get_attribute('data-gym') != 'inde' else None
    page.locator('#seance-routine-list .routine-row-main', has_text='Routine salle').first.click(); page.wait_for_timeout(600)
    lv = live(page)
    exs_ = lv['exercises'] if lv else []
    check(lv and lv.get('gym') == 'inde' and [x['exerciseId'] for x in exs_] == ['ex-y', 'ex-z'] and exs_[0].get('replacesExerciseId') == 'ex-x'
          and exs_[0]['exerciseName'] == 'Hack squat fabrique' and 'replacesExerciseId' not in exs_[1],
          'G11 Indé : ex-x remplacé par ex-y (replacesExerciseId ex-x), ex-z inchangé, salle "inde" enregistrée')
    # livraison 2b : sans historique de l'équivalent dans la routine, charges vides (avant : celles de l'exercice d'origine)
    check(len(exs_[0]['sets']) == 3 and all(x['weightKg'] is None for x in exs_[0]['sets']) and exs_[0]['restSeconds'] == 90
          and all(x['repsMin'] == 8 and x['repsMax'] == 10 for x in exs_[0]['sets']),
          'G11 sans historique de l\'équivalent : structure du créneau (3 séries, plage 8-10, repos 90 s), charges vides')
    head = page.inner_text('#seance-gym-label') if page.is_visible('#seance-gym-label') else ''
    card = page.locator('.live-card').first.inner_text()
    check(head == 'Salle : Indé' and 'Remplace Presse fabriquee (salle indé)' in card, 'G11 en-tête "%s", carte "remplace"' % head)
    ctx.close()

    # G12 : lancement en On Air : aucun remplacement, salle "onair"
    ctx, page, errors = fresh(b, salle_dataset())
    launch_start(page); lv = live(page)
    check(lv and lv.get('gym') == 'onair' and [x['exerciseId'] for x in lv['exercises']] == ['ex-x', 'ex-z'] and all('replacesExerciseId' not in x for x in lv['exercises']),
          'G12 On Air : aucun remplacement, salle "onair" enregistrée')
    ctx.close()

    # G13 : dernière salle déduite (aucune clé) ; lancements depuis le Programme et l'Accueil : dernière salle enregistrée et affichée
    today = datetime.now().isoweekday()
    hist = [sess2('s-old', '2026-09-01', 'onair', [('ex-x', 'Presse fabriquee', [rset(100, 10, True)])]),
            sess2('s-last', '2026-09-08', 'inde', [('ex-y', 'Hack squat fabrique', [rset(50, 8, True)], 'ex-x')])]
    ctx, page, errors = fresh(b, salle_dataset(hist, weekdays=[today]))
    keys0 = set(ls(page))
    seance(page)
    check(pill(page).get_attribute('data-gym') == 'inde', 'G13 écran de départ : dernière salle utilisée (Indé) présélectionnée')
    page.click('.nav-btn[data-target="routine"]'); page.wait_for_timeout(400)
    page.locator('.routine-row-start:visible', has_text='Démarrer').first.click(); page.wait_for_timeout(700)
    lv = live(page)
    head = page.inner_text('#seance-gym-label') if page.is_visible('#seance-gym-label') else ''
    check(lv and lv.get('gym') == 'inde' and lv['exercises'][0]['exerciseId'] == 'ex-y' and head == 'Salle : Indé' and set(ls(page)) == keys0,
          'G13 Programme "Démarrer" : salle "inde" enregistrée, remplacement fait, en-tête "%s", aucune nouvelle clé' % head)
    ctx.close()
    ctx, page, errors = fresh(b, salle_dataset(hist, weekdays=[today]))
    page.click('.nav-btn[data-target="dashboard"]'); page.wait_for_timeout(400)
    starts = page.locator('#dash-session-cta')
    if starts.count() and starts.is_visible() and 'commencer' in starts.inner_text().lower():   # capitales (CSS)
        starts.click(); page.wait_for_timeout(700)
        lv = live(page); head = page.inner_text('#seance-gym-label') if page.is_visible('#seance-gym-label') else ''
        check(lv and lv.get('gym') == 'inde' and lv['exercises'][0]['exerciseId'] == 'ex-y' and head == 'Salle : Indé', 'G13 Accueil "Commencer la séance" : salle "inde" enregistrée, remplacement fait, en-tête "%s"' % head)
    else:
        check(False, 'G13 Accueil : bouton "Commencer la séance" introuvable')
    ctx.close()

    # G14 : continuité dans les deux sens : On Air reprend la dernière séance avec X (pas la séance indé), Indé reprend la dernière avec Y
    hist = [sess2('s-a', '2026-08-01', 'onair', [('ex-x', 'Presse fabriquee', [rset(100, 10, True), rset(100, 10, True), rset(100, 10, True)])]),
            sess2('s-b', '2026-08-08', 'inde', [('ex-y', 'Hack squat fabrique', [rset(50, 8, True), rset(50, 8, True)], 'ex-x')])]
    ctx, page, errors = fresh(b, salle_dataset(hist))
    seance(page)
    if pill(page).get_attribute('data-gym') != 'onair': pill(page).click(); page.wait_for_timeout(200)
    page.locator('#seance-routine-list .routine-row-main', has_text='Routine salle').first.click(); page.wait_for_timeout(600)
    x = live(page)['exercises'][0]
    check(x['exerciseId'] == 'ex-x' and len(x['sets']) == 3 and all(abs(st_['weightKg'] - 102.5) < 0.01 for st_ in x['sets']),
          'G14 On Air après une séance indé : X reprend sa dernière séance (100 kg, haut de plage atteint, 102,5 kg) (%s)' % [st_['weightKg'] for st_ in x['sets']])
    ctx.close()
    ctx, page, errors = fresh(b, salle_dataset(hist))
    seance(page)
    if pill(page).get_attribute('data-gym') != 'inde': pill(page).click(); page.wait_for_timeout(200)
    page.locator('#seance-routine-list .routine-row-main', has_text='Routine salle').first.click(); page.wait_for_timeout(600)
    y = live(page)['exercises'][0]
    check(y['exerciseId'] == 'ex-y' and len(y['sets']) == 2 and all(st_['weightKg'] == 50 and st_.get('targetReps') == 9 for st_ in y['sets']),
          'G14 Indé : Y reprend sa dernière séance (2 séries, 50 kg, cible 9 reps) (%s)' % [(st_['weightKg'], st_.get('targetReps')) for st_ in y['sets']])
    ctx.close()

    # G15 : mouvement Lifting jamais remplacé, même avec un champ forcé dans les données
    d = salle_dataset(extra_rex=[{'exerciseId': 'ex-l', 'restSeconds': 120, 'sets': [{'reps': 5, 'weightKg': 80}]}])
    d['exercises'][4]['gymEquivalentId'] = 'ex-z'
    ctx, page, errors = fresh(b, d)
    seance(page)
    if pill(page).get_attribute('data-gym') != 'inde': pill(page).click(); page.wait_for_timeout(200)
    page.locator('#seance-routine-list .routine-row-main', has_text='Routine salle').first.click(); page.wait_for_timeout(600)
    ids = [x['exerciseId'] for x in live(page)['exercises']]
    check(ids == ['ex-y', 'ex-z', 'ex-l'] and not errors, 'G15 Indé : Lifting gardé tel quel (%s)' % ids)
    ctx.close()

    # G16 : allègement automatique (lot 13) sur une carte remplacée, puis séries remises à la séance suivante
    d = salle_dataset()
    d['exercises'].append(ex('ex-c', 'Arrache fabrique', 'Lifting', liftBaseMode='force'))
    d['forceCycles'] = {'ex-c': {'cycle_actif': '6', 'semaine_actuelle': 4, 'one_rm_actuel': 100, 'historique_1rm': [], 'historique_cycles': [], 'prochain_cycle': None,
                                 'en_attente_de_validation': False, 'semaines_modifiees': {}, 'test_report_used': False, 'decalage_semaines': 0}}
    d['settings']['deloadMuscuMode'] = 'auto'
    ctx, page, errors = fresh(b, d)
    seance(page)
    if pill(page).get_attribute('data-gym') != 'inde': pill(page).click(); page.wait_for_timeout(200)
    page.locator('#seance-routine-list .routine-row-main', has_text='Routine salle').first.click(); page.wait_for_timeout(600)
    y = live(page)['exercises'][0]
    check(y['exerciseId'] == 'ex-y' and y.get('deload') is True and len(y['sets']) == 2 and len(y.get('deloadRemovedSets') or []) == 1,
          'G16 semaine allégée : la carte remplacée est allégée comme les autres (3 séries vers 2, 1 retirée)')
    ctx.close()
    hist = [sess2('s-dl', '2026-09-08', 'inde', [('ex-y', 'Hack squat fabrique', [rset(50, 10, True), rset(50, 10, True)], 'ex-x')])]
    hist[0]['exercises'][0].update({'deload': True, 'deloadRemovedSets': [rset(50)], 'deloadSource': {'exerciseId': 'ex-c', 'cycleId': '6', 'weekNumber': 4}})
    ctx, page, errors = fresh(b, salle_dataset(hist))
    seance(page)
    if pill(page).get_attribute('data-gym') != 'inde': pill(page).click(); page.wait_for_timeout(200)
    page.locator('#seance-routine-list .routine-row-main', has_text='Routine salle').first.click(); page.wait_for_timeout(600)
    y = live(page)['exercises'][0]
    check(len(y['sets']) == 3 and all(st_['weightKg'] == 50 for st_ in y['sets']) and not y.get('deload'),
          'G16 séance suivante en Indé : séries retirées remises (3), charge figée (50 kg), pas de progression sur une séance allégée')
    ctx.close()

    # G17 : retour en Indé après une absence (1 séance indé, 3 séances On Air sur plusieurs semaines) : ce que prend la carte Y
    def observe(label, hist_):
        c, pg, err = fresh(b, salle_dataset(hist_))
        seance(pg)
        if pill(pg).get_attribute('data-gym') != 'inde': pill(pg).click(); pg.wait_for_timeout(200)
        pg.locator('#seance-routine-list .routine-row-main', has_text='Routine salle').first.click(); pg.wait_for_timeout(700)
        yy = live(pg)['exercises'][0]
        body = pg.locator('.live-card').first.inner_text()
        sugg = 'Deux dernières séances sous la plage' in body
        pg.click('#seance-cancel-btn'); pg.wait_for_timeout(200); pg.click('#confirm-modal-confirm'); pg.wait_for_timeout(400)
        fiche(pg, 'Hack squat fabrique')
        stag = 'stagnation' in pg.inner_text('#exercise-detail-meta').lower()   # affiché en capitales (CSS)
        fiche(pg, 'Presse fabriquee')
        stag_x = 'stagnation' in pg.inner_text('#exercise-detail-meta').lower()
        print('OBSERVATION G17 %s : Y charges %s, cibles %s, plage %s-%s, suggestion de baisse %s, stagnation Y %s, stagnation X %s' % (
            label, [z['weightKg'] for z in yy['sets']], [z.get('targetReps') for z in yy['sets']], yy['sets'][0].get('repsMin'), yy['sets'][0].get('repsMax'), sugg, stag, stag_x))
        c.close()
        return yy, sugg, stag
    onair3 = [sess2('s-o%d' % i, dt, 'onair', [('ex-x', 'Presse fabriquee', [rset(100 + 2.5 * i, 9, True)] * 3)]) for i, dt in enumerate(['2026-07-29', '2026-08-19', '2026-09-09'])]
    one_y = [sess2('s-y1', '2026-07-01', 'inde', [('ex-y', 'Hack squat fabrique', [rset(60, 9, True), rset(60, 9, True), rset(60, 8, True)], 'ex-x')])]
    yy, sugg, stag = observe('1 séance Y (9, 9, 8 reps à 60 kg) le 1er juillet', one_y + onair3)
    check(yy['exerciseId'] == 'ex-y' and len(yy['sets']) == 3 and all(z['weightKg'] == 60 for z in yy['sets']) and all(z.get('targetReps') == 9 for z in yy['sets']) and not sugg and not stag,
          'G17 absence de 10 semaines : Y repart de sa dernière séance (60 kg, cible 9), aucune suggestion ni stagnation')
    below = [sess2('s-y%d' % i, dt, 'inde', [('ex-y', 'Hack squat fabrique', [rset(60, 7, True)] * 3, 'ex-x')]) for i, dt in enumerate(['2026-06-17', '2026-06-24', '2026-07-01'])]
    yy, sugg, stag = observe('3 séances Y sous la plage (7 reps à 60 kg) fin juin', below + onair3)
    check(sugg and stag and all(z['weightKg'] == 60 for z in yy['sets']),
          'G17 absence avec 3 anciennes séances Y sous la plage : suggestion de baisse ET stagnation affichées malgré 10 semaines d\'écart (aucune prise en compte du temps)')

    # G18 : historique : salle dans la liste et le détail, "remplace X" sur l'exercice remplacé
    hist = [sess2('s-h', '2026-09-08', 'inde', [('ex-y', 'Hack squat fabrique', [rset(50, 8, True)], 'ex-x'), ('ex-z', 'Fente fabriquee', [rset(40, 8, True)])])]
    ctx, page, errors = fresh(b, salle_dataset(hist))
    page.click('.nav-btn[data-target="progression"]'); page.wait_for_timeout(300); page.click('#history-open-btn'); page.wait_for_timeout(400)
    row = page.locator('#history-list .history-row').first.inner_text()
    page.locator('#history-list .history-row').first.click(); page.wait_for_timeout(400)
    sub = page.inner_text('#history-detail-date'); body = page.inner_text('#history-detail-body')
    check('Indé' in row and 'Salle : Indé' in sub and 'Remplace Presse fabriquee (salle indé)' in body and body.count('Remplace') == 1 and not errors,
          'G18 historique : liste "%s", détail "%s", une seule mention "remplace"' % (row.replace('\n', ' ')[:60], sub))
    ctx.close()
    ctx, page, errors = fresh(b, salle_dataset([sess2('s-anc', '2026-09-01', None, [('ex-x', 'Presse fabriquee', [rset(100, 8, True)])])]))
    page.click('.nav-btn[data-target="progression"]'); page.wait_for_timeout(300); page.click('#history-open-btn'); page.wait_for_timeout(400)
    page.locator('#history-list .history-row').first.click(); page.wait_for_timeout(400)
    check('Salle' not in page.inner_text('#history-detail-date') and 'Remplace' not in page.inner_text('#history-detail-body'), 'G18 séance d\'avant le lot (sans salle) : rien d\'affiché')
    ctx.close()

    # ================= Livraison 2b : doublon, statistiques, charges vides, prévisionnel =================
    def cur_kg(page): return page.locator('.live-card.is-open .muscu-set-row.is-current input').first
    def cur_circle(page): return page.locator('.live-card.is-open .muscu-set-row.is-current .live-set-col-check button').first
    def launch_gym(page, gym_):
        seance(page)
        if pill(page).get_attribute('data-gym') != gym_: pill(page).click(); page.wait_for_timeout(200)
        page.locator('#seance-routine-list .routine-row-main', has_text='Routine salle').first.click(); page.wait_for_timeout(700)

    # G19 : charges vides pour un équivalent sans historique dans la routine ; une série se valide avec un poids saisi ; Z non concerné inchangé
    hist = [sess2('s-z', '2026-09-01', 'onair', [('ex-x', 'Presse fabriquee', [rset(100, 9, True)] * 3), ('ex-z', 'Fente fabriquee', [rset(42.5, 10, True), rset(42.5, 10, True)])])]
    ctx, page, errors = fresh(b, salle_dataset(hist))
    launch_gym(page, 'inde')
    lv = live(page); y, z = lv['exercises'][0], lv['exercises'][1]
    check(y['exerciseId'] == 'ex-y' and all(st_['weightKg'] is None for st_ in y['sets']) and len(y['sets']) == 3,
          'G19 équivalent sans historique : 3 séries, charges vides (jamais les 100 kg de la presse)')
    check(z['exerciseId'] == 'ex-z' and [st_['weightKg'] for st_ in z['sets']] == [45, 45] and 'replacesExerciseId' not in z,
          'G19 exercice non concerné : reprise habituelle de la dernière séance (42,5 kg haut de plage, 45 kg) (%s)' % [st_['weightKg'] for st_ in z['sets']])
    cur_kg(page).fill('55'); cur_kg(page).press('Tab'); page.wait_for_timeout(150)
    cur_circle(page).click(); page.wait_for_timeout(400)
    y = live(page)['exercises'][0]
    check(y['sets'][0]['done'] is True and y['sets'][0]['weightKg'] == 55 and not errors, 'G19 série validée avec un poids saisi à la main (55 kg)')
    ctx.close()

    # G20 : prévisionnel de la charge de la semaine (lot 13) : en Indé, la carte remplacée est prévue à la place de l'exercice d'origine
    today = datetime.now().isoweekday()
    # l'écran n'affiche que des nombres de séries : la carte remplacée a 2 séries (son historique), l'exercice d'origine 3 (sa ligne de routine)
    for gym_, expected in [('inde', 4), ('onair', 5)]:
        hist = [sess2('s-w1', '2026-09-01', 'inde', [('ex-y', 'Hack squat fabrique', [rset(50, 10, True)] * 2, 'ex-x')])]
        if gym_ == 'onair': hist.append(sess2('s-w2', '2026-09-08', 'onair', [('ex-w', 'Leg extension fabrique', [rset(30, 10, True)])], routine='r-autre'))
        ctx, page, errors = fresh(b, salle_dataset(hist, weekdays=[today]))
        page.click('.nav-btn[data-target="routine"]'); page.wait_for_timeout(400)
        sub = page.inner_text('#programme-week-load-sub')
        check(('%d séries' % expected) in sub and not errors,
              'G20 charge de la semaine, dernière salle %s : "%s" (attendu %d : %s)' % (gym_, sub, expected, 'Y 2 + Z 2' if gym_ == 'inde' else 'X 3 + Z 2'))
        ctx.close()

    # G21 : doublon X vers Y alors que Y est aussi dans la routine
    dup_rex = [{'exerciseId': 'ex-y', 'restSeconds': 75, 'sets': [rset(70), rset(70)]}]
    def dup_session(sid, date, w_rep, w_norm, reps_rep=10, reps_norm=8, gym='inde'):
        return sess2(sid, date, gym, [('ex-y', 'Hack squat fabrique', [rset(w_rep, reps_rep, True)] * 3, 'ex-x'),
                                       ('ex-z', 'Fente fabriquee', [rset(40, 8, True)] * 2),
                                       ('ex-y', 'Hack squat fabrique', [rset(w_norm, reps_norm, True)] * 2)])
    hist = [dup_session('s-d1', '2026-09-01', 50, 70), dup_session('s-d2', '2026-09-08', 52.5, 70)]
    ctx, page, errors = fresh(b, salle_dataset(hist, extra_rex=dup_rex))
    launch_gym(page, 'inde')
    lv = live(page); cards = lv['exercises']
    c_rep, c_norm = cards[0], cards[2]
    check([c['exerciseId'] for c in cards] == ['ex-y', 'ex-z', 'ex-y'] and c_rep.get('replacesExerciseId') == 'ex-x' and 'replacesExerciseId' not in c_norm and c_rep['id'] != c_norm['id'],
          'G21 deux cartes Y distinctes : la première remplace X, la seconde est la carte normale')
    check(len(c_rep['sets']) == 3 and all(abs(st_['weightKg'] - 55) < 0.01 for st_ in c_rep['sets']) and len(c_norm['sets']) == 2
          and all(st_['weightKg'] == 70 and st_.get('targetReps') == 9 for st_ in c_norm['sets']),
          'G21 progression par carte sur deux séances : remplacée 50 puis 52,5 vers 55 kg ; normale 70 kg cible 9 (%s / %s)' % (
              [st_['weightKg'] for st_ in c_rep['sets']], [(st_['weightKg'], st_.get('targetReps')) for st_ in c_norm['sets']]))
    prev_rep = page.locator('.live-card.is-open .muscu-set-row .live-set-col-prev').first.inner_text()
    page.locator('.live-card-header').nth(2).click(); page.wait_for_timeout(300)
    prev_norm = page.locator('.live-card.is-open .muscu-set-row .live-set-col-prev').first.inner_text()
    check('52.5' in prev_rep and '70' in prev_norm and '52.5' not in prev_norm, 'G21 comparateur "Précédent" par carte : remplacée "%s", normale "%s"' % (prev_rep, prev_norm))
    cur_kg(page).fill('72'); cur_kg(page).press('Tab'); page.wait_for_timeout(100); cur_circle(page).click(); page.wait_for_timeout(300)
    page.locator('.live-card-header').nth(0).click(); page.wait_for_timeout(300)
    cur_kg(page).fill('56'); cur_kg(page).press('Tab'); page.wait_for_timeout(100); cur_circle(page).click(); page.wait_for_timeout(300)
    page.click('#seance-finish-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(800)
    done_s = [x for x in json.loads(ls(page)['ovryk.sessions']) if x['id'] == lv['id']][0]
    ys = [x for x in done_s['exercises'] if x['exerciseId'] == 'ex-y']
    check(done_s['status'] == 'completed' and len(ys) == 2 and ys[0].get('replacesExerciseId') == 'ex-x' and ys[0]['sets'][0]['weightKg'] == 56
          and ys[1]['sets'][0]['weightKg'] == 72 and 'replacesExerciseId' not in ys[1] and ys[0]['id'] != ys[1]['id'],
          'G21 séance enregistrée : deux cartes Y gardées séparément (56 kg remplacée, 72 kg normale), aucune n\'écrase l\'autre')
    fiche(page, 'Hack squat fabrique')
    hist_rows = page.locator('#exercise-detail-history .history-row').count()
    check(hist_rows == 3, 'G21 fiche de Y : %d lignes d\'historique pour 3 séances avec doublon (une par séance)' % hist_rows)
    # compteur de séances (countSessionsForExercise) : vérifié par G22 sur les mêmes règles (séance avec carte remplacée comptée une fois)
    ctx.close()
    hist = [dup_session('s-e1', '2026-09-01', 50, 70, reps_rep=10, reps_norm=6), dup_session('s-e2', '2026-09-08', 52.5, 70, reps_rep=10, reps_norm=6)]
    ctx, page, errors = fresh(b, salle_dataset(hist, extra_rex=dup_rex))
    launch_gym(page, 'inde')
    txt_rep = page.locator('.live-card.is-open').first.inner_text()
    page.locator('.live-card-header').nth(2).click(); page.wait_for_timeout(300)
    txt_norm = page.locator('.live-card.is-open').first.inner_text()
    sug = 'Deux dernières séances sous la plage'
    check(sug in txt_norm and sug not in txt_rep, 'G21 suggestion de baisse par carte : normale oui, remplacée non')
    ctx.close()
    hist = [sess2('s-r0', '2026-08-25', 'onair', [('ex-y', 'Hack squat fabrique', [rset(50, 8, True)])]), dup_session('s-r1', '2026-09-08', 60, 70)]
    ctx, page, errors = fresh(b, salle_dataset(hist, extra_rex=dup_rex))
    page.click('.nav-btn[data-target="progression"]'); page.wait_for_timeout(300); page.click('#history-open-btn'); page.wait_for_timeout(400)
    page.locator('#history-list .history-row').first.click(); page.wait_for_timeout(400)
    tiles = ' '.join(page.locator('#history-detail-body .history-tile').all_inner_texts()).lower().replace('\n', ' ')
    check('record 1' in tiles, 'G21 détail : "%s" (Y en doublon bat son record : compté une fois)' % tiles)
    ctx.close()

    # G22 : strictement identique sans carte remplacée. Fonctions extraites de c81f6fe (avant la 2b) et de la version actuelle, mêmes séances.
    ROOT = Path(__file__).resolve().parents[2]
    def extract(src, name):
        m = re.search(r'\n  function ' + name + r'\(', src)
        if not m: return ''
        i = src.index('{', m.end()); depth = 0
        for j in range(i, len(src)):
            if src[j] == '{': depth += 1
            elif src[j] == '}':
                depth -= 1
                if depth == 0: return src[m.start():j + 1]
        return ''
    NAMES = ['findExerciseInSession', 'findSexForSlot', 'getMuscuSetReps', 'computeSuccessfulReps', 'computeWeightFromPercent', 'epley1RM',
             'resolveDoneSets', 'mergeSessionRecords', 'getExerciseSessionRecords', 'countSessionsForExercise', 'getLastLoggedSex', 'hasBelowRangeSet', 'checkDeloadSuggestion']
    def harness(html):
        src = html[html.index('<script>'):]
        return '\n'.join(extract(src, n) for n in NAMES)
    try:
        old_html = subprocess.run(['git', '-C', str(ROOT), 'show', 'c81f6fe:index.html'], capture_output=True, text=True, check=True).stdout
        new_html = (ROOT / 'index.html').read_text()
        ok_git = True
    except Exception:
        ok_git = False; old_html = new_html = ''
    def lx(sid, date, items, status='completed'):
        s_ = sess2(sid, date, None, items); s_['status'] = status; return s_
    plain = [lx('p1', '2026-08-01', [('ex-a', 'A', [rset(50, 8, True), rset(52.5, 7, True)]), ('ex-b', 'B', [rset(30, 10, True)])]),
             lx('p2', '2026-08-08', [('ex-a', 'A', [rset(55, 6, True)]), ('ex-a', 'A', [rset(60, 5, True), {'reps': 5, 'weightKg': 62.5, 'done': True, 'rpe': 8}])]),
             lx('p3', '2026-08-15', [('ex-a', 'A', [rset(55, 6, True)] * 2), ('ex-b', 'B', [rset(32.5, 10, True)])]),
             lx('p4', '2026-08-22', [('ex-a', 'A', [rset(57.5, 9, False)])], status='in_progress'),
             lx('p5', '2026-08-29', [('ex-l', 'L', [{'reps': 3, 'percent1rm': 80, 'done': True}])])]
    plain[4]['exercises'][0]['category'] = 'Lifting'; plain[4]['exercises'][0]['oneRepMaxSnapshot'] = 100
    plain[2]['exercises'][0]['deload'] = True
    JS_TAIL = "\nvar out = {};\n['ex-a', 'ex-b', 'ex-l'].forEach(function (id) {\n  out[id] = { recAll: getExerciseSessionRecords(id), recDone: getExerciseSessionRecords(id, true), count: countSessionsForExercise(id), last: getLastLoggedSex(id), deload: checkDeloadSuggestion(id) };\n});\nconsole.log(JSON.stringify(out));\n"
    def run_js(code, sessions):
        js = ('var activeSession = null;\nvar OvrykDB = { getSessions: function () { return %s; } };\n' % json.dumps(sessions)) + code + JS_TAIL
        f = SP / 'harness.js'; f.write_text(js)
        r = subprocess.run(['node', str(f)], capture_output=True, text=True)
        return json.loads(r.stdout) if r.returncode == 0 else {'erreur': r.stderr[:300]}
    if ok_git:
        o, n = run_js(harness(old_html), plain), run_js(harness(new_html), plain)
        check('erreur' not in o and 'erreur' not in n and o == n,
              'G22 séances sans carte remplacée (dont le même exercice deux fois dans une séance) : enregistrements, compteur, comparateur et décharge identiques avant et après (%s)' % (o.get('erreur') or n.get('erreur') or 'ok'))
        mixed = plain + [lx('p6', '2026-09-05', [('ex-a', 'A', [rset(70, 8, True)], 'ex-x'), ('ex-a', 'A', [rset(65, 9, True)])])]
        o2, n2 = run_js(harness(old_html), mixed), run_js(harness(new_html), mixed)
        ok2 = ('erreur' not in o2 and 'erreur' not in n2 and len(n2['ex-a']['recAll']) == len(o2['ex-a']['recAll']) - 1
               and n2['ex-a']['count'] == o2['ex-a']['count'] - 1 and n2['ex-a']['recAll'][:-1] == o2['ex-a']['recAll'][:-2]
               and n2['ex-a']['recAll'][-1]['maxWeight'] == 70 and len(n2['ex-a']['recAll'][-1]['sets']) == 2)
        check(ok2, 'G22 seule la séance avec une carte remplacée est fusionnée (un enregistrement et une séance de moins qu\'avant, les autres identiques)')
    else:
        check(False, 'G22 git indisponible : comparaison avec c81f6fe impossible')

    b.close()

print('\n%d/%d' % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
