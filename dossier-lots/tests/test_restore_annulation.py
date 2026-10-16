"""Restauration locale (lot 16) : bandeau, annulation et rétablissement.
* N1 : restauration interrompue (état mélangé, marque) : bandeau, "Revenir à la
  copie d'avant", état identique octet pour octet à celui d'avant, plus de bandeau.
* N2 : marque vers une copie introuvable : message dans le bandeau, seul "Ignorer" reste.
* N3 : "Ignorer" retire seulement la marque.
* N4 : libellés Annuler / Rétablir sur un parcours réel (import, annulation, rétablissement).
* N5 : échec d'une annulation : le message cite "Rétablir la restauration annulée".
* N6 : restauration pendant une séance en cours : avertissement, puis la séance revient après annulation.
* N7 : séances perdues comptées par identifiant (même nombre, autres séances).
* N8 : 5 copies au plus (la plus ancienne disparaît).
* N9 : abandon à l'écran puis à la deuxième confirmation : rien écrit.
* N10 : ouverture de Réglages sans copie : aucune écriture, aucune base créée.
Données FABRIQUÉES ici. Usage : python3 test_restore_annulation.py <dossier de travail>."""
import json
from playwright.sync_api import sync_playwright
from restore_commun import *

F = workdir()
PHONE = dataset('tel', 3)
INCOMING = dataset('imp', 2, 20)
FILE = write_file(F, 'import.json', envelope(INCOMING))
QUOTA = """(rules) => { const orig = Storage.prototype.setItem; const used = {};
  Storage.prototype.setItem = function (k, v) {
    for (const r of rules) {
      if (r.key === k && (r.value == null || r.value === v) && (r.times == null || (used[k] || 0) < r.times)) {
        used[k] = (used[k] || 0) + 1; const e = new Error('QuotaExceededError simulé'); e.name = 'QuotaExceededError'; throw e; } }
    return orig.call(this, k, v); }; }"""
def txt(page, sel): return (page.text_content(sel) or '').strip() if page.locator(sel).count() else ''
def undo_label(page): return txt(page, '#restore-undo-label') if page.is_visible('#restore-undo-btn') else ''
def sessions_of(page): return json.loads(data(page)['ovryk.sessions'])
def do_import(page, path=FILE):
    """import réussi, puis un second démarrage : la migration existante complète liftBaseMode au deuxième
    démarrage d'un état neuf (écriture préexistante, LOT-16 point 6) ; l'état est stable ensuite."""
    settings(page); import_file(page, path); confirm_restore(page); wait_reload(page)
    page.reload(); page.wait_for_timeout(400)

with sync_playwright() as p:
    b = p.chromium.launch()
    control_fixtures(b, F)

    # N1 : restauration interrompue puis retour complet depuis le bandeau
    ctx, page, errors = fresh(b, PHONE)
    settings(page); before = data(page)
    import_file(page, FILE)
    page.evaluate(QUOTA, [{'key': 'ovryk.sessions'}, {'key': 'ovryk.routines', 'value': before['ovryk.routines']}])
    confirm_restore(page)
    mixed = data(page) != before and jget(page, MARK) is not None
    page.reload(); page.wait_for_timeout(500); home(page)
    banner = page.is_visible('#restore-interrupted-banner') and page.is_visible('#restore-interrupted-back-btn')
    if not (mixed and banner):
        # sans marque ni bandeau, aucun retour possible : échec explicite plutôt qu'un clic qui attendrait 30 s
        check(False, 'N1 restauration interrompue : état mélangé %s, marque %s, bandeau %s (attendus tous les trois)' % (data(page) != before, jget(page, MARK) is not None, banner))
    else:
        page.click('#restore-interrupted-back-btn'); page.wait_for_timeout(600)
        title = txt(page, '#restore-title'); btn = txt(page, '#restore-confirm-btn')
        confirm_restore(page); wait_reload(page); home(page)
        check(title == 'Annuler la restauration' and btn == 'Revenir à cette copie' and data(page) == before
              and MARK not in ls(page) and not page.is_visible('#restore-interrupted-banner') and not errors,
              'N1 bandeau : écran "%s", retour complet, état identique octet pour octet à celui d\'avant, marque retirée, plus de bandeau' % title)
        page.reload(); page.wait_for_timeout(500); home(page)
        check(not page.is_visible('#restore-interrupted-banner'), 'N1 au rechargement suivant : aucun bandeau')
    ctx.close()

    # N2 : marque vers une copie qui n'existe pas
    ctx, page, errors = fresh(b, PHONE)
    jset(page, MARK, {'pointId': 999, 'startedAt': '2026-10-12T10:00:00.000Z', 'mode': 'file'})
    page.reload(); page.wait_for_timeout(500); home(page); before = ls(page); dbs0 = dbs(page)
    page.click('#restore-interrupted-back-btn'); page.wait_for_timeout(600)
    check(page.is_visible('#restore-interrupted-msg') and 'introuvable ou abîmée' in txt(page, '#restore-interrupted-msg')
          and not page.is_visible('#restore-interrupted-back-btn') and page.is_visible('#restore-interrupted-dismiss-btn')
          and not restore_open(page) and ls(page) == before and dbs(page) == dbs0 and not errors,
          'N2 copie introuvable : message dans le bandeau, bouton masqué, seul "Ignorer" reste, rien écrit, aucune base créée')
    # N3 : Ignorer
    page.click('#restore-interrupted-dismiss-btn'); page.wait_for_timeout(200)
    modal = txt(page, '#confirm-modal-message')
    page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    after = ls(page)
    check('Ignorer ce message' in modal and MARK not in after and {k: v for k, v in after.items()} == {k: v for k, v in before.items() if k != MARK}
          and not page.is_visible('#restore-interrupted-banner') and not errors,
          'N3 "Ignorer" : seule la marque est retirée, données identiques, bandeau masqué')
    ctx.close()

    # N4 : libellés Annuler / Rétablir sur un parcours réel
    ctx, page, errors = fresh(b, PHONE)
    settings(page); state_p = data(page)
    do_import(page); state_a = data(page)
    settings(page); l1 = undo_label(page)
    page.click('#restore-undo-btn'); page.wait_for_timeout(600)
    t1, b1 = txt(page, '#restore-title'), txt(page, '#restore-confirm-btn')
    confirm_restore(page); wait_reload(page)
    back_p = data(page) == state_p
    settings(page); l2 = undo_label(page)
    page.click('#restore-undo-btn'); page.wait_for_timeout(600)
    t2, b2, body2 = txt(page, '#restore-title'), txt(page, '#restore-confirm-btn'), txt(page, '#restore-body')
    confirm_restore(page); wait_reload(page)
    back_a = data(page) == state_a
    settings(page); l3 = undo_label(page)
    check(l1 == 'Annuler la dernière restauration' and t1 == 'Annuler la restauration' and b1 == 'Revenir à cette copie' and back_p,
          'N4 après import : ligne "%s", écran "%s" / "%s", retour à l\'état d\'avant' % (l1, t1, b1))
    check(l2 == 'Rétablir la restauration annulée' and t2 == 'Rétablir la restauration' and b2 == 'Rétablir la restauration'
          and 'Tu as annulé une restauration' in body2 and back_a,
          'N4 après annulation : ligne "%s", écran "%s" / "%s", rétablissement de l\'état restauré' % (l2, t2, b2))
    check(l3 == 'Annuler la dernière restauration' and not errors, 'N4 après rétablissement : ligne "%s"' % l3)
    ctx.close()

    # N5 : échec d'une annulation (retour arrière en échec) : le message cite le libellé de la copie faite à ce moment
    ctx, page, errors = fresh(b, PHONE)
    settings(page); state_p = data(page)
    do_import(page); state_a = data(page)
    settings(page); page.click('#restore-undo-btn'); page.wait_for_timeout(600)
    page.evaluate(QUOTA, [{'key': 'ovryk.exercises', 'value': state_p['ovryk.exercises']}, {'key': 'ovryk.routines', 'value': state_a['ovryk.routines']}])
    confirm_restore(page)
    m = io(page); mark = jget(page, MARK)
    check(m == 'Restauration interrompue : utilise « Rétablir la restauration annulée » dans Réglages pour revenir à la copie d’avant.'
          and mark and mark.get('mode') == 'undo' and not errors,
          'N5 échec d\'une annulation : "%s", marque gardée (mode %s)' % (m[:80], (mark or {}).get('mode')))
    ctx.close()

    # N6 : restauration pendant une séance en cours, puis annulation : la séance revient en cours, à l'identique
    with_live = dataset('tel', 2); with_live['sessions'].append(live_session('s-live'))
    ctx, page, errors = fresh(b, with_live)
    settings(page); live0 = [s for s in sessions_of(page) if s['id'] == 's-live'][0]
    import_file(page, FILE)
    warn = 'Une séance est en cours sur ce téléphone et n’est pas dans la sauvegarde : elle sera remplacée.' in txt(page, '#restore-body')
    confirm_restore(page); wait_reload(page)
    gone = all(s['status'] != 'in_progress' for s in sessions_of(page))
    settings(page); page.click('#restore-undo-btn'); page.wait_for_timeout(600)
    confirm_restore(page); wait_reload(page)
    live1 = [s for s in sessions_of(page) if s['id'] == 's-live']
    page.click('.nav-btn[data-target="seance"]'); page.wait_for_timeout(400)
    check(warn and gone and live1 == [live0] and page.is_visible('#seance-active-view') and not errors,
          'N6 séance en cours : avertissement, remplacée par la restauration, revenue à l\'identique (en cours) après annulation')
    ctx.close()

    # N7 : séances perdues comptées par identifiant (3 séances de chaque côté, aucune en commun) ; témoin : fichier qui les contient toutes
    ctx, page, errors = fresh(b, PHONE)
    settings(page); before = ls(page); dbs0 = dbs(page)
    import_file(page, write_file(F, 'memes-nombre.json', envelope(dataset('autre', 3, 10))))
    body = txt(page, '#restore-body')
    page.click('#restore-confirm-btn'); page.wait_for_timeout(200); modal = txt(page, '#confirm-modal-message')
    page.click('#confirm-modal-cancel'); page.wait_for_timeout(200); page.click('#restore-cancel-btn'); page.wait_for_timeout(200)
    superset = dataset('tel', 3); superset['sessions'].append(done_session('s-plus', 25))
    import_file(page, write_file(F, 'surensemble.json', envelope(superset)))
    body_ok = txt(page, '#restore-body')
    page.click('#restore-confirm-btn'); page.wait_for_timeout(200); modal_ok = txt(page, '#confirm-modal-message')
    page.click('#confirm-modal-cancel'); page.wait_for_timeout(200); page.click('#restore-cancel-btn'); page.wait_for_timeout(200)
    check('Attention : 3 séances terminées de ce téléphone ne sont pas dans la sauvegarde' in body
          and modal.startswith('Dernière confirmation : 3 séances terminées de ce téléphone ne sont pas dans la sauvegarde'),
          'N7 même nombre de séances mais autres identifiants : 3 séances perdues annoncées à l\'écran et à la deuxième confirmation')
    check('Attention' not in body_ok and modal_ok.startswith('Dernière confirmation. ') and ls(page) == before and dbs(page) == dbs0 and not errors,
          'N7 témoin : fichier qui contient toutes les séances, aucun avertissement ; abandons sans rien écrire')
    ctx.close()

    # N8 : 5 copies au plus
    ctx, page, errors = fresh(b, PHONE)
    olds = [point(raw_of(dataset('old%d' % i, 1)), '2026-10-0%dT10:00:00.000Z' % (i + 1)) for i in range(5)]
    ids = put_points(page, olds)
    settings(page); before = data(page)
    do_import(page); page.wait_for_timeout(500)
    pts = get_points(page); kept = sorted(x['id'] for x in pts)
    newest = max(pts, key=lambda x: x['id']) if pts else {}
    check(len(pts) == 5 and min(ids) not in kept and newest.get('reason') == 'avant restauration'
          and all((newest['raw'].get(k)) == before.get(k) for k in DATA_KEYS) and not errors,
          'N8 5 copies au plus : %d copies gardées (%s), la plus ancienne (%s) supprimée, la nouvelle = état d\'avant' % (len(pts), kept, min(ids)))
    ctx.close()

    # N9 : abandon à l'écran, puis à la deuxième confirmation : rien écrit, aucune base créée
    ctx, page, errors = fresh(b, PHONE)
    settings(page); before = ls(page); dbs0 = dbs(page)
    import_file(page, FILE); page.click('#restore-cancel-btn'); page.wait_for_timeout(200)
    first = not restore_open(page) and ls(page) == before and dbs(page) == dbs0
    import_file(page, FILE); page.click('#restore-confirm-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-cancel'); page.wait_for_timeout(300)
    check(first and restore_open(page) and not page.is_disabled('#restore-confirm-btn') and ls(page) == before and dbs(page) == dbs0 and not errors,
          'N9 abandon à l\'écran puis à la deuxième confirmation : rien écrit, aucune base de copies créée')
    ctx.close()

    # N10 : ouverture de Réglages sans copie : aucune écriture, aucune base créée
    ctx, page, errors = fresh(b, PHONE)
    home(page); before = ls(page); dbs0 = dbs(page)
    settings(page); page.wait_for_timeout(300)
    check(ls(page) == before and dbs(page) == dbs0 == [] and not page.is_visible('#restore-undo-btn') and not page.net and not errors,
          'N10 Réglages sans copie : aucune écriture, aucune base créée, pas de ligne d\'annulation, aucun appel réseau')
    ctx.close()

    b.close()
done()
