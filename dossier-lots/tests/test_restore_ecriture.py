"""Restauration locale (lot 16) : écriture et copie de sécurité.
* E0 témoin : restauration réussie (données remplacées, une copie identique à l'état d'avant, marque retirée).
* E1 à E3 : écriture partielle (stockage plein simulé pendant le remplacement) :
  retour arrière réussi ; retour arrière en échec sur une clé déjà remplacée
  (marque gardée, message vers la ligne d'annulation) ; échec sur une clé
  jamais modifiée ("rien n'a changé").
* E4 : IndexedDB qui ne répond jamais : abandon à 10 s (horloge simulée),
  puis réponse tardive : copie supprimée, aucune ligne Annuler fantôme.
* E5 : copie relue différente de l'état (une autre fenêtre écrit pendant la copie).
* E6 : copie impossible (ouverture de la base en erreur).
Données FABRIQUÉES ici. Usage : python3 test_restore_ecriture.py <dossier de travail>."""
import json
from playwright.sync_api import sync_playwright
from restore_commun import *

F = workdir()
PHONE = dataset('tel', 3)
INCOMING = dataset('imp', 2, 20)
FILE = write_file(F, 'import.json', envelope(INCOMING))
ROLLBACK_MSG = 'Restauration impossible (stockage plein ?). L’état d’avant a été remis, rien n’a changé.'
INTERRUPTED_MSG = 'Restauration interrompue : utilise « Annuler la dernière restauration » dans Réglages pour revenir à la copie d’avant.'
TIMEOUT_MSG = 'La copie de sécurité n’a pas pu être faite, rien n’a été remplacé. Réessaie plus tard.'

# stockage plein simulé : règles par clé (et par valeur exacte si donnée), "times" = nombre d'échecs
QUOTA = """(rules) => { const orig = Storage.prototype.setItem; const used = {};
  Storage.prototype.setItem = function (k, v) {
    for (const r of rules) {
      if (r.key === k && (r.value == null || r.value === v) && (r.times == null || (used[k] || 0) < r.times)) {
        used[k] = (used[k] || 0) + 1; const e = new Error('QuotaExceededError simulé'); e.name = 'QuotaExceededError'; throw e; } }
    return orig.call(this, k, v); }; }"""
# IndexedDB muette : l'ouverture renvoie une requête qui ne répond jamais ; __release la branche ensuite sur la vraie base
HANG = """() => { const realOpen = IDBFactory.prototype.open; window.__pending = null;
  IDBFactory.prototype.open = function (name, v) {
    if (name === 'ovryk-restore' && !window.__pending) { const f = {}; window.__pending = { f: f, name: name, v: v }; return f; }
    return realOpen.call(this, name, v); };
  window.__release = () => { const p = window.__pending; IDBFactory.prototype.open = realOpen;
    const r = realOpen.call(indexedDB, p.name, p.v);
    r.onupgradeneeded = (e) => { if (p.f.onupgradeneeded) p.f.onupgradeneeded(e); };
    r.onsuccess = () => { p.f.result = r.result; if (p.f.onsuccess) p.f.onsuccess(); };
    r.onerror = (e) => { p.f.error = r.error; if (p.f.onerror) p.f.onerror(e); }; }; }"""

def open_import(b, clock=False):
    ctx, page, errors = fresh(b, PHONE, clock=clock)
    settings(page); before = data(page)
    import_file(page, FILE)
    return ctx, page, errors, before
def raw_equal(raw, d):
    return all((raw.get(k) if raw.get(k) is not None else None) == d.get(k) for k in DATA_KEYS)

with sync_playwright() as p:
    b = p.chromium.launch()
    control_fixtures(b, F)

    # E0 témoin : restauration réussie
    ctx, page, errors, before = open_import(b)
    opened = restore_open(page)
    confirm_restore(page); wait_reload(page)
    after = data(page); pts = get_points(page)
    check(opened and json.loads(after['ovryk.sessions']) == INCOMING['sessions'] and json.loads(after['ovryk.routines']) == INCOMING['routines']
          and MARK not in ls(page) and len(pts) == 1 and raw_equal(pts[0]['raw'], before) and pts[0]['reason'] == 'avant restauration' and not errors,
          'E0 témoin : données remplacées par le fichier, une copie identique à l\'état d\'avant, marque retirée')
    ctx.close()

    # E1 : stockage plein sur les séances, une seule fois : le retour arrière réussit
    ctx, page, errors, before = open_import(b)
    page.evaluate(QUOTA, [{'key': 'ovryk.sessions', 'times': 1}])
    confirm_restore(page)
    check(io(page) == ROLLBACK_MSG and data(page) == before and MARK not in ls(page) and count_points(page) == 0 and not restore_open(page) and not errors,
          'E1 écriture partielle, retour arrière réussi : "%s", état identique octet pour octet, marque retirée, copie de la tentative supprimée' % io(page)[:60])
    ctx.close()

    # E2 : le retour arrière échoue aussi, sur les routines déjà remplacées : état mélangé, marque gardée, renvoi vers la copie
    ctx, page, errors, before = open_import(b)
    page.evaluate(QUOTA, [{'key': 'ovryk.sessions'}, {'key': 'ovryk.routines', 'value': before['ovryk.routines']}])
    confirm_restore(page)
    now = data(page); mark = jget(page, MARK); pts = get_points(page)
    mixed = json.loads(now['ovryk.routines']) == INCOMING['routines'] and now['ovryk.sessions'] == before['ovryk.sessions']
    check(io(page) == INTERRUPTED_MSG and mixed and mark and mark.get('mode') == 'file' and len(pts) == 1 and mark.get('pointId') == pts[0]['id']
          and raw_equal(pts[0]['raw'], before) and not errors,
          'E2 retour arrière en échec : message vers "Annuler la dernière restauration", marque gardée (copie %s), état mélangé constaté, copie = état d\'avant' % (mark or {}).get('pointId'))
    ctx.close()

    # E3 : échec sur les exercices, première clé écrite et la plus grosse (catalogue complet) : jamais modifiée,
    # le retour arrière échoue sur elle en dernier ; l'état est intact : "rien n'a changé", marque retirée
    ctx, page, errors, before = open_import(b)
    order = sorted(DATA_KEYS, key=lambda k: len(before.get(k) or ''))
    page.evaluate(QUOTA, [{'key': 'ovryk.exercises'}])
    confirm_restore(page)
    check(order[-1] == 'ovryk.exercises' and io(page) == ROLLBACK_MSG and data(page) == before and MARK not in ls(page) and count_points(page) == 0 and not errors,
          'E3 échec sur une clé jamais modifiée : "rien n\'a changé", état intact, marque retirée, aucune copie laissée')
    ctx.close()

    # E4 : IndexedDB muette : rien avant 10 s, abandon à 10 s, réponse tardive supprimée
    ctx, page, errors, before = open_import(b, clock=True)
    page.evaluate(HANG)
    page.clock.pause_at(page.evaluate("() => Date.now()"))   # horloge figée : seul run_for la fait avancer
    page.click('#restore-confirm-btn'); page.wait_for_timeout(200); page.click('#confirm-modal-confirm'); page.wait_for_timeout(300)
    page.clock.run_for(9900); page.wait_for_timeout(200)
    locked = page.is_disabled('#restore-confirm-btn') and restore_open(page) and io(page) == '' and data(page) == before and MARK not in ls(page)
    page.clock.run_for(200); page.wait_for_timeout(300)
    after10 = io(page); unlocked = not restore_open(page) and not page.is_disabled('#restore-confirm-btn')
    check(locked, 'E4 IndexedDB muette, à 9,9 s : écran bloqué, aucun message, rien écrit, aucune marque')
    check(after10 == TIMEOUT_MSG and unlocked and data(page) == before and MARK not in ls(page) and not errors,
          'E4 à 10 s : "%s", écran débloqué, données identiques, aucune marque' % after10[:60])
    page.evaluate("() => window.__release()"); page.wait_for_timeout(600); page.clock.run_for(100); page.wait_for_timeout(400)
    settings(page); page.wait_for_timeout(300)
    check(count_points(page) == 0 and not page.is_visible('#restore-undo-btn') and data(page) == before and MARK not in ls(page) and not errors,
          'E4 réponse tardive : copie supprimée dès son arrivée, aucune ligne Annuler fantôme, rien écrit')
    ctx.close()

    # E5 : une autre fenêtre écrit pendant la copie : copie relue différente, rien remplacé, copie supprimée
    ctx, page, errors, before = open_import(b)
    page.evaluate("""() => { const add = IDBObjectStore.prototype.add;
      IDBObjectStore.prototype.add = function (v, k) { const r = add.apply(this, arguments);
        localStorage.setItem('ovryk.settings', JSON.stringify({ unit: 'kg', restTimerSeconds: 120, lastExportAt: null })); return r; }; }""")
    confirm_restore(page)
    now = data(page)
    same_rest = all(now[k] == before[k] for k in DATA_KEYS if k != 'ovryk.settings')
    check(io(page) == 'Restauration annulée : impossible de copier l’état actuel (copie relue différente de l’état actuel). Rien n’a été modifié.'
          and same_rest and json.loads(now['ovryk.settings'])['restTimerSeconds'] == 120 and MARK not in ls(page) and count_points(page) == 0 and not errors,
          'E5 copie relue différente : rien remplacé (seule l\'écriture de l\'autre fenêtre reste), copie supprimée, aucune marque')
    ctx.close()

    # E6 : ouverture de la base en erreur : rien remplacé
    ctx, page, errors, before = open_import(b)
    page.evaluate("""() => { const realOpen = IDBFactory.prototype.open;
      IDBFactory.prototype.open = function (name, v) { if (name === 'ovryk-restore') throw new Error('base indisponible simulée'); return realOpen.call(this, name, v); }; }""")
    confirm_restore(page)
    check(io(page) == 'Restauration annulée : impossible de copier l’état actuel (base indisponible simulée). Rien n’a été modifié.'
          and data(page) == before and MARK not in ls(page) and not errors,
          'E6 copie impossible : "%s", rien remplacé, aucune marque' % io(page)[:70])
    check(not page.net, 'aucun appel réseau')
    ctx.close()

    b.close()
done()
