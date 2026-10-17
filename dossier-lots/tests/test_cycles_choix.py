"""Cycles liés au programme, livraison 3b : "Choisir le mouvement" sur l'écran
de fin de cycle. Liste = même pool que le tirage de la 3a, triée par nom,
1RM de l'exercice affiché ; cycle toujours tiré au sort ; même confirmation
et même écriture que la 3a ; pool vide expliqué (accords) ; 1RM modifié ou
mouvement devenu inéligible pendant que la liste est ouverte ; double tap ;
Annuler sans écriture ; affichage à 390 px sans débordement.
Données FABRIQUÉES ici : aucun vrai export, aucun appel réseau.
Usage : python3 test_cycles_choix.py <dossier de travail> [url], site servi sur http://127.0.0.1:8765."""
import sys, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright
SP = Path(sys.argv[1]); URL = sys.argv[2] if len(sys.argv) > 2 else 'http://127.0.0.1:8765/index.html'
SP.mkdir(parents=True, exist_ok=True)
res = []
def check(c, m): res.append(bool(c)); print(('ok     ' if c else 'ECHEC  ') + m)
DATA_KEYS = ['ovryk.exercises', 'ovryk.routines', 'ovryk.sessions', 'ovryk.settings', 'ovryk.forceCycles', 'ovryk.meta']
FAIL = "Le changement de mouvement a échoué (stockage plein ou indisponible). "
KEPT = FAIL + "Tes routines et tes cycles sont restés comme avant."
ONERM = " Seul le 1RM validé de Deadlift fab (110 kg) a été enregistré sur l'exercice."
STALE = "Le tirage n'est plus à jour : rien n'a changé. Tire à nouveau un mouvement."
GONE = "Ce mouvement n'est plus disponible : la liste a été mise à jour."
TAIL = " Le 1RM se saisit dans Exercices."
MSG_RE = re.compile(r"^Remplacer Deadlift fab par (.+?) dans (.+) \? (.+?), cycle (\d+), semaine 1, 1RM ([\d,]+) kg\.$")
LETTERS = {'13': 'A', '14': 'B', '15': 'C', '16': 'D', '17': 'E'}

# ---------- fixtures fabriquées ----------
def ex(eid, name, orm=None, cat='Lifting', start=None):
    d = {'id': eid, 'name': name, 'category': cat, 'equipment': 'Barre', 'unit': 'kg', 'isCustom': True, 'oneRepMax': orm}
    if cat == 'Lifting': d['liftBaseMode'] = 'force'
    if start: d['forceCycleStartDate'] = start
    return d
def active(eid, orm, cyc='D', week=2):
    return {'exercise_id': eid, 'cycle_actif': cyc, 'one_rm_actuel': orm, 'semaine_actuelle': week,
            'historique_1rm': [{'date': '2026-08-01T10:00:00.000Z', 'valeur': orm}], 'historique_cycles': [], 'prochain_cycle': None,
            'en_attente_de_validation': False, 'semaines_modifiees': {}, 'test_report_used': False, 'decalage_semaines': 0}
def pending(eid, start, after, cyc='C', nxt='D'):
    return {'exercise_id': eid, 'cycle_actif': cyc, 'one_rm_actuel': after, 'semaine_actuelle': 6,
            'historique_1rm': [{'date': '2026-08-01T10:00:00.000Z', 'valeur': start}, {'date': '2026-09-12T10:00:00.000Z', 'valeur': after}],
            'historique_cycles': [{'cycle': cyc, 'debut': '2026-08-01T10:00:00.000Z', 'fin': '2026-09-12T10:00:00.000Z', 'seances': 6,
                                   'seances_prevues': 6, 'reussite_pct': 90, 'one_rm_avant': start, 'one_rm_apres': after}],
            'prochain_cycle': nxt, 'en_attente_de_validation': True, 'semaines_modifiees': {}, 'test_report_used': False, 'decalage_semaines': 0}
def rex(eid, sets=1, weight=40, rest=120, **extra):
    d = {'exerciseId': eid, 'restSeconds': rest, 'sets': [{'reps': 5, 'weight': weight, 'weightKg': weight} for _ in range(sets)]}
    d.update(extra); return d
def routine(rid, name, rexes):
    return {'id': rid, 'name': name, 'weekdays': [], 'updatedAt': '2026-09-01T00:00:00.000Z', 'createdAt': '2026-09-01T00:00:00.000Z',
            'exercises': [r if isinstance(r, dict) else rex(r) for r in rexes]}
def dataset(exercises, routines, cycles):
    st = {'unit': 'kg', 'restTimerSeconds': 90, 'lastExportAt': None}
    return {'exercises': exercises, 'routines': routines, 'sessions': [], 'settings': st, 'forceCycles': cycles, 'meta': {'schemaVersion': 2}}

def ls(page): return page.evaluate("() => { const o = {}; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); o[k] = localStorage.getItem(k); } return o; }")
def data(page): return {k: v for k, v in ls(page).items() if k in DATA_KEYS}
def cycles(page): return json.loads(ls(page)['ovryk.forceCycles'])
def routines(page): return json.loads(ls(page)['ovryk.routines'])
def exs(page): return {e['id']: e for e in json.loads(ls(page)['ovryk.exercises'])}
def fresh(b, d):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    page = ctx.new_page(); errors = []; page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(URL); page.evaluate("() => localStorage.clear()")
    for k, v in d.items(): page.evaluate("([k, v]) => localStorage.setItem(k, v)", ['ovryk.' + k, json.dumps(v)])
    page.reload(); page.wait_for_timeout(300); page.reload(); page.wait_for_timeout(300)
    return ctx, page, errors
def neutralize_library(page):
    """fixture C11 : les 19 mouvements Lifting de la bibliothèque par défaut (sans 1RM, fusionnés à chaque démarrage) passent
    dans une autre catégorie, pour compter les motifs du pool vide sur les seuls exercices fabriqués ici"""
    page.evaluate("""() => { const l = JSON.parse(localStorage.getItem('ovryk.exercises'));
      l.forEach(e => { if (!e.isCustom && e.category === 'Lifting') e.category = 'Divers'; }); localStorage.setItem('ovryk.exercises', JSON.stringify(l)); }""")
    page.reload(); page.wait_for_timeout(300)
def nav(page, target): page.click('.nav-btn[data-target="%s"]' % target); page.wait_for_timeout(300)
def open_end(page):
    nav(page, 'exercices')
    page.locator('.exercise-row', has_text='Deadlift fab').first.locator('.cycle-active-badge').click(); page.wait_for_timeout(300)
def modal(page):
    return {'visible': page.is_visible('#confirm-modal-overlay'), 'message': page.inner_text('#confirm-modal-message'),
            'confirm': page.text_content('#confirm-modal-confirm'), 'cancel_visible': page.is_visible('#confirm-modal-cancel')}
def toggle_list(page): page.click('#cycle-end-choose-move-btn'); page.wait_for_timeout(200)
def rows(page): return page.locator('#cycle-end-move-list .picker-row')
def row_names(page): return page.locator('#cycle-end-move-list .picker-row .picker-row-name').all_inner_texts()
def row_metas(page): return page.locator('#cycle-end-move-list .picker-row .picker-row-meta').all_text_contents()
def pick(page, name):
    page.locator('#cycle-end-move-list .picker-row', has_text=name).first.click(); page.wait_for_timeout(200); return modal(page)
def cancel(page): page.click('#confirm-modal-cancel'); page.wait_for_timeout(200)
def confirm(page): page.click('#confirm-modal-confirm'); page.wait_for_timeout(400)
def set_orm(page, eid, value):
    page.evaluate("""([eid, v]) => { const l = JSON.parse(localStorage.getItem('ovryk.exercises'));
      l.forEach(e => { if (e.id === eid) e.oneRepMax = v; }); localStorage.setItem('ovryk.exercises', JSON.stringify(l)); }""", [eid, value])
def no_overflow(page):
    return page.evaluate("""() => { const l = document.getElementById('cycle-end-move-list');
      const all = [document.documentElement, document.getElementById('cycle-end-body'), l].concat(Array.from(l.children));
      return all.every(el => el.scrollWidth <= el.clientWidth + 1) && Array.from(l.children).every(el => el.getBoundingClientRect().right <= 391); }""")
def break_key(key, after=0):
    return """() => { const orig = Storage.prototype.setItem; let n = 0; Storage.prototype.setItem = function (k, v) {
  if (k === '%s' && ++n > %d) throw new DOMException('quota', 'QuotaExceededError'); return orig.call(this, k, v); }; }""" % (key, after)

DL, PC, BS, NO, FU, MU, OA, ZS, AR, EP, FS = 'ex-dl', 'ex-pc', 'ex-bs', 'ex-no', 'ex-fu', 'ex-mu', 'ex-oa', 'ex-zs', 'ex-ar', 'ex-ep', 'ex-fs'
EXPECTED = ['Arraché fab', 'Épaulé fab', 'Power Clean fab', 'Zercher fab']
def full_pool():
    """Deadlift terminé dans deux routines. Éligibles : Arraché, Épaulé, Power Clean (sans cycle) et Zercher (en attente hors
    programme, ancienne entrée à 180, exercice à 190). Exclus : Back Squat (actif), Sans 1RM, Futur (date future), Presse (muscu),
    Orphelin actif (cycle en cours hors programme), Front Squat (en attente dans le programme), Deadlift (terminé).
    Exercices volontairement dans le désordre."""
    exercises = [ex(ZS, 'Zercher fab', 190), ex(DL, 'Deadlift fab', 100), ex(PC, 'Power Clean fab', 70), ex(BS, 'Back Squat fab', 120),
                 ex(EP, 'Épaulé fab', 85), ex(NO, 'Sans 1RM fab', None), ex(FU, 'Futur fab', 90, start='2099-01-01'),
                 ex(MU, 'Presse fab', 150, 'Jambes'), ex(OA, 'Orphelin actif fab', 60), ex(AR, 'Arraché fab', 62.5), ex(FS, 'Front Squat fab', 100)]
    rts = [routine('r-a', 'Force fab', [rex(BS), rex(DL, 3, 80, 180, groupId='g1', groupType='superset', grip='pronation'), rex(MU), rex(FS)]),
           routine('r-b', 'Force fab (indé)', [rex(DL, 2, 60, 150), rex(BS)])]
    cyc = {DL: pending(DL, 100, 110), BS: active(BS, 120), OA: active(OA, 60, 'B', 3), ZS: pending(ZS, 170, 180, 'A', 'B'),
           FS: pending(FS, 90, 100, 'B', 'D')}
    return dataset(exercises, rts, cyc)

with sync_playwright() as p:
    b = p.chromium.launch()

    # C0 à C3 : bouton, liste = pool de la 3a triée par nom, 1RM de l'exercice, ordre stable, 390 px, aucune écriture
    ctx, page, errors = fresh(b, full_pool())
    before = ls(page)
    open_end(page)
    body = page.text_content('#cycle-end-body')
    check(all(t in body for t in ['Relancer', 'Garder ce cycle', 'Choisir moi même', 'Lancer ce cycle', 'CHANGER DE MOUVEMENT'])
          and page.text_content('#cycle-end-swap-btn') == 'Tirer un autre mouvement'
          and page.text_content('#cycle-end-choose-move-btn') == 'Choisir le mouvement'
          and page.is_hidden('#cycle-end-move-list') and ls(page) == before,
          'C0 écran de fin : commandes existantes inchangées, "Choisir le mouvement" présent, liste fermée, aucune écriture')
    toggle_list(page)
    names, metas = row_names(page), row_metas(page)
    check(names == EXPECTED, 'C1 liste = pool de la 3a, triée par nom (accents compris) : %s' % names)
    check(metas == ['1RM 62,5 kg', '1RM 85 kg', '1RM 70 kg', '1RM 190 kg'],
          'C1 1RM de l\'exercice sur chaque ligne (Zercher 190, jamais 180 de l\'ancienne entrée) : %s' % metas)
    check(ls(page) == before and not errors, 'C1 ouverture de la liste : aucune écriture')
    orders = []
    for _ in range(3):
        toggle_list(page); toggle_list(page); orders.append(row_names(page))
    check(all(o == EXPECTED for o in orders) and page.is_visible('#cycle-end-move-list'), 'C2 ordre stable sur trois réouvertures')
    check(no_overflow(page), 'C3 liste à 390 px : aucun débordement horizontal')
    toggle_list(page)
    check(page.is_hidden('#cycle-end-move-list') and ls(page) == before, 'C3 fermeture de la liste : aucune écriture')

    # C4 : Zercher choisi : confirmation de la 3a, 1RM 190, cycle jamais celui qui vient de finir (C = 15), Annuler sans écriture
    toggle_list(page)
    m = pick(page, 'Zercher fab'); g = MSG_RE.match(m['message'])
    check(g and g.group(1) == 'Zercher fab' and g.group(2) == '« Force fab » et « Force fab (indé) »' and g.group(5) == '190'
          and m['confirm'] == 'Confirmer' and m['cancel_visible'],
          'C4 confirmation de la 3a, 1RM de l\'exercice (190) : %s' % m['message'])
    drawn = set()
    for _ in range(30):
        cancel(page); m = pick(page, 'Zercher fab'); g = MSG_RE.match(m['message']); drawn.add(g.group(4) if g else None)
    check(None not in drawn and '15' not in drawn and len(drawn) > 1, 'C4 30 tirages du cycle : jamais le cycle 15 qui vient de finir (%s)' % sorted(drawn))
    cancel(page)
    check(ls(page) == before and not errors, 'C4 Annuler : aucune écriture')

    # C5 : confirmation : même résultat que la 3a (entrée reprise, point de départ à 190, routines remplacées)
    m = pick(page, 'Zercher fab'); g = MSG_RE.match(m['message']); cyc = LETTERS.get(g.group(4), g.group(4))
    old = {'c': json.loads(before['ovryk.forceCycles']), 'r': json.loads(before['ovryk.routines'])}
    confirm(page)
    c, r = cycles(page), routines(page)
    z = c[ZS]
    check(z['one_rm_actuel'] == 190 and z['historique_1rm'][:-1] == old['c'][ZS]['historique_1rm'] and z['historique_1rm'][-1]['valeur'] == 190
          and z['historique_cycles'] == old['c'][ZS]['historique_cycles'] and z['cycle_actif'] == cyc and cyc != 'C'
          and z['semaine_actuelle'] == 1 and not z['en_attente_de_validation'] and z['prochain_cycle'] is None,
          'C5 entrée de Zercher reprise à 190, cycle %s semaine 1, historiques conservés' % g.group(4))
    a = r[0]['exercises'][1]
    check([x['exerciseId'] for x in r[0]['exercises']] == [BS, ZS, MU, FS] and [x['exerciseId'] for x in r[1]['exercises']] == [ZS, BS]
          and a['grip'] is None and a['groupId'] == 'g1' and len(a['sets']) == 3 and a['restSeconds'] == 180
          and r[0]['updatedAt'] == old['r'][0]['updatedAt'] and c[DL] == old['c'][DL] | {} and c[DL]['en_attente_de_validation']
          and exs(page)[DL]['oneRepMax'] == 110 and page.is_hidden('#cycle-end-page') and not errors,
          'C5 routines remplacées (créneau conservé, prise remise à null, updatedAt intact), entrée de Deadlift en place, 1RM validé recopié (%s)' % errors[:1])
    ctx.close()

    # C6 : 1RM modifié pendant que la liste est ouverte, puis pendant que la confirmation est ouverte
    ctx, page, errors = fresh(b, full_pool())
    open_end(page); toggle_list(page)
    set_orm(page, PC, 75); before = ls(page)
    m = pick(page, 'Power Clean fab'); g = MSG_RE.match(m['message'])
    check(g and g.group(1) == 'Power Clean fab' and g.group(5) == '75', 'C6 1RM changé liste ouverte : la confirmation relit 75 : %s' % m['message'])
    set_orm(page, PC, 80); before = ls(page)
    confirm(page); m = modal(page)
    check(m['message'] == STALE and ls(page) == before and not errors, 'C6 1RM changé confirmation ouverte : "plus à jour", rien n\'est écrit')
    confirm(page)
    ctx.close()

    # C7 : mouvement devenu inéligible avant l'appui (1RM vidé, puis cycle lancé ailleurs) : message, liste mise à jour, rien n'est écrit
    ctx, page, errors = fresh(b, full_pool())
    open_end(page); toggle_list(page)
    set_orm(page, PC, None); before = ls(page)
    m = pick(page, 'Power Clean fab')
    check(m['message'] == GONE and m['confirm'] == 'Compris' and not m['cancel_visible'], 'C7 1RM vidé : "%s"' % m['message'])
    confirm(page)
    check(row_names(page) == ['Arraché fab', 'Épaulé fab', 'Zercher fab'] and ls(page) == before and not errors,
          'C7 liste mise à jour sans Power Clean, aucune écriture')
    page.evaluate("""() => { const c = JSON.parse(localStorage.getItem('ovryk.forceCycles'));
      c['ex-ep'] = { exercise_id: 'ex-ep', cycle_actif: 'A', one_rm_actuel: 85, semaine_actuelle: 1, historique_1rm: [], historique_cycles: [],
        prochain_cycle: null, en_attente_de_validation: false, semaines_modifiees: {}, test_report_used: false, decalage_semaines: 0 };
      localStorage.setItem('ovryk.forceCycles', JSON.stringify(c)); }""")
    before = ls(page)
    m = pick(page, 'Épaulé fab'); confirm(page)
    check(m['message'] == GONE and row_names(page) == ['Arraché fab', 'Zercher fab'] and ls(page) == before and not errors,
          'C7 cycle lancé ailleurs : refusé, liste mise à jour, aucune écriture')
    ctx.close()

    # C8 : double tap sur une ligne puis sur Confirmer : une seule application
    ctx, page, errors = fresh(b, full_pool())
    old_c = cycles(page)
    open_end(page); toggle_list(page)
    page.evaluate("() => { const r = Array.from(document.querySelectorAll('#cycle-end-move-list .picker-row')).find(x => x.textContent.indexOf('Power Clean fab') === 0); r.click(); r.click(); }")
    page.wait_for_timeout(200)
    check(MSG_RE.match(modal(page)['message']) is not None, 'C8 double tap sur la ligne : une confirmation')
    page.evaluate("() => { const b = document.getElementById('confirm-modal-confirm'); b.click(); b.click(); }"); page.wait_for_timeout(400)
    c, r = cycles(page), routines(page)
    check(set(c) == set(old_c) | {PC} and len(c[PC]['historique_1rm']) == 1 and c[PC]['one_rm_actuel'] == 70
          and [x['exerciseId'] for x in r[0]['exercises']] == [BS, PC, MU, FS] and [x['exerciseId'] for x in r[1]['exercises']] == [PC, BS]
          and not page.is_visible('#confirm-modal-overlay') and not errors,
          'C8 double tap sur Confirmer : une seule application, aucun message d\'erreur (%s)' % errors[:1])
    ctx.close()

    # C9 : échec d'écriture des routines par la liste : même remise en état et même message que la 3a
    ctx, page, errors = fresh(b, full_pool())
    old = data(page)
    open_end(page); toggle_list(page); pick(page, 'Power Clean fab')
    page.evaluate(break_key('ovryk.routines')); confirm(page); m = modal(page)
    after = data(page)
    check(m['message'] == KEPT + ONERM and after['ovryk.forceCycles'] == old['ovryk.forceCycles'] and after['ovryk.routines'] == old['ovryk.routines'] and not errors,
          'C9 échec des routines : cycles remis, routines intactes, message exact : %s' % m['message'])
    ctx.close()

    # C10 : un seul mouvement : une ligne, confirmation, Annuler et retour sans écriture
    d = dataset([ex(DL, 'Deadlift fab', 100), ex(PC, 'Power Clean fab', 70)], [routine('r-a', 'Force fab', [DL])], {DL: pending(DL, 100, 110)})
    ctx, page, errors = fresh(b, d)
    before = ls(page)
    open_end(page); toggle_list(page)
    check(row_names(page) == ['Power Clean fab'] and row_metas(page) == ['1RM 70 kg'], 'C10 un seul mouvement : une ligne')
    m = pick(page, 'Power Clean fab'); g = MSG_RE.match(m['message'])
    check(g and g.group(2) == '« Force fab »' and g.group(4) != '15', 'C10 confirmation : %s' % m['message'])
    cancel(page); page.click('#cycle-end-back-btn'); page.wait_for_timeout(200)
    check(ls(page) == before and not errors, 'C10 Annuler puis retour : aucune écriture')
    ctx.close()

    # C11 : pool vide : message dans la liste (accords), même message pour le tirage, aucune ligne, aucune écriture, 390 px
    ONE_NO = "Aucun mouvement disponible. 1 mouvement Lifting n'a pas de 1RM saisi." + TAIL
    MANY = "Aucun mouvement disponible. 3 mouvements Lifting n'ont pas de 1RM saisi. 2 mouvements Lifting ont déjà un cycle, en cours ou à lancer." + TAIL
    ONE_CY = "Aucun mouvement disponible. 1 mouvement Lifting a déjà un cycle, en cours ou à lancer." + TAIL
    TWO_NO = "Aucun mouvement disponible. 2 mouvements Lifting n'ont pas de 1RM saisi." + TAIL
    NONE = "Aucun autre mouvement Lifting. Crée-en un dans Exercices et saisis son 1RM pour qu'il puisse être tiré ou choisi."
    cases = [
        ('un sans 1RM', [ex(NO, 'Sans 1RM fab', None)], {}, ONE_NO),
        ('trois sans 1RM, deux avec cycle', [ex(NO, 'Sans 1RM fab', None), ex(AR, 'Arraché fab', None), ex(ZS, 'Zercher fab', ''),
                                              ex(BS, 'Back Squat fab', 120), ex(FS, 'Front Squat fab', 100), ex(MU, 'Presse fab', 150, 'Jambes')],
         {BS: active(BS, 120), FS: pending(FS, 90, 100, 'B', 'D')}, MANY),
        ('un avec cycle', [ex(BS, 'Back Squat fab', 120)], {BS: active(BS, 120)}, ONE_CY),
        ('deux sans 1RM dont un avec cycle', [ex(NO, 'Sans 1RM fab', None), ex(ZS, 'Zercher fab', None)], {ZS: pending(ZS, 80, 90, 'A', 'B')}, TWO_NO),
        ('aucun autre Lifting', [ex(MU, 'Presse fab', 150, 'Jambes')], {}, NONE),
    ]
    for label, extra, extra_cyc, expected in cases:
        rex_list = [DL] + [e['id'] for e in extra if e['id'] in (BS, FS)]
        cyc = {DL: pending(DL, 100, 110)}; cyc.update(extra_cyc)
        d = dataset([ex(DL, 'Deadlift fab', 100)] + extra, [routine('r-a', 'Force fab', rex_list)], cyc)
        ctx, page, errors = fresh(b, d); neutralize_library(page)
        before = ls(page)
        open_end(page); toggle_list(page)
        text = page.inner_text('#cycle-end-move-list').strip()
        check(text == expected and rows(page).count() == 0 and page.is_visible('#cycle-end-move-list .cycle-end-move-empty') and no_overflow(page),
              'C11 pool vide (%s) : "%s"' % (label, text))
        page.click('#cycle-end-swap-btn'); page.wait_for_timeout(200); m = modal(page); confirm(page)
        check(m['message'] == expected and m['confirm'] == 'Compris' and ls(page) == before and not errors,
              'C11 pool vide (%s) : même message pour le tirage, aucune écriture' % label)
        ctx.close()

    # C12 : bibliothèque par défaut présente (cas réel) : ses mouvements Lifting sans 1RM sont comptés
    d = dataset([ex(DL, 'Deadlift fab', 100), ex(NO, 'Sans 1RM fab', None)], [routine('r-a', 'Force fab', [DL])], {DL: pending(DL, 100, 110)})
    ctx, page, errors = fresh(b, d)
    lib = sum(1 for e in exs(page).values() if not e['isCustom'] and e['category'] == 'Lifting')
    open_end(page); toggle_list(page)
    text = page.inner_text('#cycle-end-move-list').strip()
    check(lib == 19 and text == "Aucun mouvement disponible. 20 mouvements Lifting n'ont pas de 1RM saisi." + TAIL and no_overflow(page) and not errors,
          'C12 bibliothèque présente (%d mouvements Lifting) : "%s"' % (lib, text))
    ctx.close()

    b.close()

print('\n%d/%d' % (sum(res), len(res)))
sys.exit(0 if all(res) else 1)
