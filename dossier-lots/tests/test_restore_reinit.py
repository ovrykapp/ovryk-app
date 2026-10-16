"""Restauration locale (lot 16) : "Réinitialiser l'app".
* T1 : supprime la base de copies, les données, la marque et les copies
  quotidiennes (préfixe exact "ovryk.backup.", dont "ovryk.backup.forceCycles.") ;
  les clés leurres restent ; les copies du jour recréées ne contiennent rien de l'ancien état.
* T2 et T3 : base de copies bloquée par un second onglet qui la garde ouverte :
  suspension à 5 s (horloge figée), puis "Annuler" (rien supprimé) ou
  "Réinitialiser quand même" (données effacées, copies gardées).
Données FABRIQUÉES ici. Usage : python3 test_restore_reinit.py <dossier de travail>."""
import json
from playwright.sync_api import sync_playwright
from restore_commun import *

F = workdir()
PHONE = dataset('ancien', 3)
OLD_DAILY = {'ovryk.backup.2026-10-01': json.dumps({'routines': PHONE['routines'], 'exercises': PHONE['exercises']}),
             'ovryk.backup.forceCycles.2026-10-01': json.dumps({'ex-fab-l': CYCLE})}
DECOYS = {'ovryk.autre': 'garde-moi', 'ovrykbackup.x': 'garde-moi aussi', 'ovryk.backupX': 'pas le préfixe exact'}
LATER = 'pourront être effacées plus tard'

def prepare(page):
    put_points(page, [point(raw_of(dataset('c%d' % i, 1)), '2026-10-0%dT10:00:00.000Z' % (i + 1)) for i in range(3)])
    for k, v in list(OLD_DAILY.items()) + list(DECOYS.items()): rawset(page, k, v)
    jset(page, MARK, {'pointId': 1, 'startedAt': '2026-10-12T10:00:00.000Z', 'mode': 'file'})
def no_old_state(store):
    """aucune trace de l'ancien état (routine, exercice, séances "ancien") dans les clés ovryk.*"""
    return not any('ancien' in (v or '') for k, v in store.items() if k.startswith('ovryk.') and k not in DECOYS)
def ask_reset(page):
    settings(page); page.click('#reset-app-btn'); page.wait_for_timeout(200)
    m = (page.text_content('#confirm-modal-message') or '')
    page.click('#confirm-modal-confirm')
    return m
HOLD = """() => new Promise((ok) => { const r = indexedDB.open('ovryk-restore'); r.onsuccess = () => { window.__db = r.result; ok(true); }; })"""
COUNT_HELD = """() => new Promise((ok) => { const g = window.__db.transaction('points', 'readonly').objectStore('points').count(); g.onsuccess = () => ok(g.result); })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    control_fixtures(b, F)

    # T1 : réinitialisation complète
    ctx, page, errors = fresh(b, PHONE)
    prepare(page); n0 = count_points(page); st0 = ls(page)
    m = ask_reset(page); wait_reload(page, 800)
    st = ls(page)
    today = [k for k in st if k.startswith('ovryk.backup.')]
    check(n0 == 3 and 'copies de sécurité de ce téléphone seront supprimées' in m and 'ovryk-restore' not in dbs(page),
          'T1 confirmation annoncée ("copies de sécurité"), base de copies supprimée (3 copies avant)')
    check(MARK not in st and all(k not in st for k in OLD_DAILY) and no_old_state(st) and not errors,
          'T1 marque, copies quotidiennes anciennes et données supprimées ; aucune trace de l\'ancien état dans ovryk.* (copies du jour recréées : %s)' % today)
    check(all(st.get(k) == v for k, v in DECOYS.items()), 'T1 préfixe exact : ovryk.autre, ovrykbackup.x et ovryk.backupX intactes')
    ctx.close()

    # T2 : base bloquée par un second onglet, puis "Annuler"
    for choice in ('annuler', 'quand même'):
        ctx, page, errors = fresh(b, PHONE, clock=True)
        prepare(page); st0 = ls(page)
        other = ctx.new_page(); other.goto(URL); other.wait_for_timeout(300); other.evaluate(HOLD)
        page.clock.pause_at(page.evaluate("() => Date.now()"))
        ask_reset(page); page.wait_for_timeout(300)
        page.clock.run_for(4900); page.wait_for_timeout(200)
        early = ls(page) == st0 and not page.is_visible('#confirm-modal-overlay')
        page.clock.run_for(200); page.wait_for_timeout(300)
        modal = page.text_content('#confirm-modal-message') or ''; status = io(page)
        suspended = ('n’ont pas pu être effacées (pas de réponse)' in modal and 'Réinitialiser quand même' in (page.text_content('#confirm-modal-confirm') or '')
                     and LATER in modal and status.startswith('Réinitialisation suspendue') and ls(page) == st0)
        if not page.is_visible('#confirm-modal-overlay'):
            # aucune suspension proposée (réinitialisation partie sans attendre la base) : échec explicite
            check(False, 'T2/T3 (%s) base bloquée : aucune suspension à 5 s (rien avant 5 s %s ; état %s)' % (choice, early, 'inchangé' if ls(page) == st0 else 'effacé'))
            ctx.close(); continue
        if choice == 'annuler':
            page.click('#confirm-modal-cancel'); page.wait_for_timeout(300)
            check(early and suspended, 'T2 base bloquée : rien avant 5 s, puis suspension "pas de réponse", choix proposé, rien supprimé')
            check(ls(page) == st0 and other.evaluate(COUNT_HELD) == 3 and io(page).startswith('Réinitialisation annulée : rien n’a été supprimé.') and LATER in io(page) and not errors,
                  'T2 "Annuler" : données, marque, copies quotidiennes et 3 copies intactes ; message honnête sur l\'effacement plus tard')
        else:
            page.click('#confirm-modal-confirm'); wait_reload(page, 800)
            st = ls(page)
            check(suspended and MARK not in st and all(k not in st for k in OLD_DAILY) and no_old_state(st) and all(st.get(k) == v for k, v in DECOYS.items())
                  and other.evaluate(COUNT_HELD) == 3 and not errors,
                  'T3 "Réinitialiser quand même" : données, marque et copies quotidiennes effacées, leurres intacts, les 3 copies restent')
        check(not page.net, 'aucun appel réseau (%s)' % choice)
        ctx.close()

    b.close()
done()
