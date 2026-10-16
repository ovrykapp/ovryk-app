"""Restauration locale (lot 16) : export, partage et protection du stockage.
* X0 témoin : export téléchargé, lastExportAt noté.
* X1 : pour chacune des 6 clés présente mais illisible : export ET partage refusés,
  rien téléchargé, rien partagé, rien écrit.
* X2 : ligne "Partager" masquée sans partage de fichiers, visible avec.
* X3 : partage réussi : fichier relu (empreinte valide, données = état), lastExportAt
  noté seulement APRÈS le succès (partage en attente : rien noté), puis réimport
  dans un autre téléphone : mêmes données (aller-retour).
* X4, X5 : partage annulé (AbortError) : rien ; partage en erreur : message, rien écrit.
* X6 : protection du stockage : Non activée, appui, Activée ; refus ; API absente.
Partage et navigator.storage SIMULÉS (script injecté) ; données FABRIQUÉES ici.
Usage : python3 test_restore_export.py <dossier de travail>."""
import json
from playwright.sync_api import sync_playwright
from restore_commun import *

F = workdir()
PHONE = dataset('tel', 3)
LABELS = {'ovryk.exercises': 'exercices', 'ovryk.routines': 'routines', 'ovryk.sessions': 'séances',
          'ovryk.settings': 'réglages', 'ovryk.forceCycles': 'cycles de force', 'ovryk.meta': 'version de schéma'}
# partage simulé : mode 'ok', 'abort', 'error' ou 'pending' (résolu par __resolveShare) ; 'none' = pas de partage de fichiers
SHARE = """(() => { window.__share = { mode: 'ok', calls: 0, text: null, resolve: null };
  Object.defineProperty(navigator, 'canShare', { configurable: true, value: (d) => window.__share.mode !== 'none' });
  Object.defineProperty(navigator, 'share', { configurable: true, value: (d) => { window.__share.calls++;
    return d.files[0].text().then((t) => { window.__share.text = t; const m = window.__share.mode;
      if (m === 'abort') { const e = new Error('annulé'); e.name = 'AbortError'; throw e; }
      if (m === 'error') throw new Error('échec simulé');
      if (m === 'pending') return new Promise((ok) => { window.__share.resolve = ok; }); }); } }); })();"""
NO_SHARE = """(() => { Object.defineProperty(navigator, 'canShare', { configurable: true, value: undefined });
  Object.defineProperty(navigator, 'share', { configurable: true, value: undefined }); })();"""
# protection du stockage simulée : réponse de persist() réglable ; 'absent' = API absente
STORAGE = """(() => { const mode = %s; window.__persisted = false; const st = navigator.storage;
  if (mode === 'absent') { Object.defineProperty(st, 'persist', { configurable: true, value: undefined }); return; }
  Object.defineProperty(st, 'persisted', { configurable: true, value: () => Promise.resolve(window.__persisted) });
  Object.defineProperty(st, 'persist', { configurable: true, value: () => { if (mode === 'grant') window.__persisted = true; return Promise.resolve(mode === 'grant'); } }); })();"""
def last_export(page): return (jget(page, 'ovryk.settings') or {}).get('lastExportAt')
def share_state(page): return page.evaluate("() => ({ calls: window.__share.calls, text: window.__share.text })")
def persist_value(page): return (page.text_content('#storage-persist-value') or '').strip()

with sync_playwright() as p:
    b = p.chromium.launch()
    control_fixtures(b, F)

    # X0 témoin et X1 clés illisibles (même contexte : chaque clé est remise après son test)
    ctx, page, errors = fresh(b, PHONE, init_script=SHARE)
    downloads = []; page.on('download', lambda d: downloads.append(d))
    settings(page)
    for key, label in LABELS.items():
        good = ls(page)[key]
        rawset(page, key, '{illisible'); before = ls(page); n_dl = len(downloads)
        page.click('#dashboard-export-btn'); page.wait_for_timeout(500)
        m_exp = io(page)
        page.click('#dashboard-share-btn'); page.wait_for_timeout(500)
        m_sh = io(page)
        expect = 'les ' + label + ' de cet appareil sont illisibles. Rien n’a été exporté.'
        if key == 'ovryk.meta':
            # texte de l'app : "les version de schéma ... sont illisibles" (accord fautif, noté dans PLAN.md) : la faute n'est pas figée ici
            msg_ok = all(m.startswith(pre) and 'version de schéma de cet appareil sont illisibles' in m and m.endswith('Rien n’a été exporté.')
                         for m, pre in ((m_exp, 'Export impossible : '), (m_sh, 'Partage impossible : ')))
        else:
            msg_ok = m_exp == 'Export impossible : ' + expect and m_sh == 'Partage impossible : ' + expect
        check(msg_ok and len(downloads) == n_dl
              and share_state(page)['calls'] == 0 and ls(page) == before and not errors,
              'X1 %s illisibles : export et partage refusés ("%s"), rien téléchargé ni partagé, rien écrit' % (label, expect[:45]))
        rawset(page, key, good)
    before_le = last_export(page); n_dl = len(downloads)
    page.click('#dashboard-export-btn'); page.wait_for_timeout(800)
    check(len(downloads) == n_dl + 1 and io(page) == 'Export téléchargé.' and last_export(page) and last_export(page) != before_le and not errors,
          'X0 témoin, clés saines : export téléchargé, lastExportAt noté')
    ctx.close()

    # X2 : ligne "Partager" selon le navigateur
    ctx, page, errors = fresh(b, PHONE, init_script=NO_SHARE)
    settings(page); hidden = not page.is_visible('#dashboard-share-btn')
    ctx.close()
    ctx, page, errors = fresh(b, PHONE, init_script=SHARE)
    settings(page)
    check(hidden and page.is_visible('#dashboard-share-btn'), 'X2 ligne "Partager" masquée sans partage de fichiers, visible avec')

    # X3 : partage en attente (rien noté), puis réussi (noté), fichier relu et valide
    page.evaluate("() => { window.__share.mode = 'pending'; }")
    state = data(page); le0 = last_export(page)
    page.click('#dashboard-share-btn'); page.wait_for_timeout(600)
    pending_ok = share_state(page)['calls'] == 1 and last_export(page) == le0 and data(page) == state
    page.evaluate("() => window.__share.resolve()"); page.wait_for_timeout(500)
    text = share_state(page)['text']; env = json.loads(text)
    file_ok = (env.get('app') == 'Ovryk' and env['summary']['checksum'] == fnv(js_stringify(env['data']))
               and all(env['data'][k] == json.loads(state['ovryk.' + k]) for k in ('exercises', 'routines', 'sessions', 'forceCycles')))
    check(pending_ok, 'X3 partage en attente : lastExportAt pas encore noté, rien écrit')
    check(file_ok and last_export(page) and last_export(page) != le0 and io(page) == 'Sauvegarde partagée.' and not errors,
          'X3 partage réussi : fichier Ovryk à l\'empreinte valide, données = état du téléphone, lastExportAt noté après le succès')
    shared = write_file(F, 'partage.json', text)
    ctx.close()
    # aller-retour : le fichier partagé, importé dans un autre téléphone, redonne les mêmes données
    ctx, page, errors = fresh(b, dataset('autre', 1))
    settings(page); import_file(page, shared); opened = restore_open(page); confirm_restore(page); wait_reload(page)
    now = data(page)
    check(opened and all(json.loads(now['ovryk.' + k]) == env['data'][k] for k in ('exercises', 'routines', 'sessions', 'forceCycles')) and not errors,
          'X3 aller-retour : le fichier partagé réimporté ailleurs redonne exercices, routines, séances et cycles à l\'identique')
    ctx.close()

    # X4 partage annulé, X5 partage en erreur : rien écrit
    for mode, expect, label in (('abort', None, 'X4 partage annulé (AbortError) : aucun message, rien écrit, lastExportAt inchangé'),
                                ('error', 'Partage impossible : échec simulé.', 'X5 partage en erreur : message, rien écrit, lastExportAt inchangé')):
        ctx, page, errors = fresh(b, PHONE, init_script=SHARE)
        settings(page); page.evaluate("(m) => { window.__share.mode = m; }", mode)
        before = ls(page); io0 = io(page)
        page.click('#dashboard-share-btn'); page.wait_for_timeout(600)
        check(share_state(page)['calls'] == 1 and ls(page) == before and (io(page) == io0 if expect is None else io(page) == expect) and not errors, label)
        ctx.close()

    # X6 : protection du stockage
    ctx, page, errors = fresh(b, PHONE, init_script=STORAGE % "'grant'")
    settings(page); before = ls(page)
    v0, en0 = persist_value(page), page.is_enabled('#storage-persist-btn')
    page.click('#storage-persist-btn'); page.wait_for_timeout(500)
    m = io(page); v1 = persist_value(page)
    check(page.is_visible('#storage-persist-btn') and v0 == 'Non activée' and en0 and m == 'Protection activée : Safari ne supprimera pas ces données de lui-même.'
          and v1 == 'Activée' and page.is_disabled('#storage-persist-btn') and ls(page) == before and not errors,
          'X6 protection : "Non activée", appui, "Activée" et bouton désactivé, aucune écriture')
    ctx.close()
    ctx, page, errors = fresh(b, PHONE, init_script=STORAGE % "'deny'")
    settings(page); before = ls(page)
    page.click('#storage-persist-btn'); page.wait_for_timeout(500)
    check(io(page).startswith('Safari a refusé pour l’instant.') and persist_value(page) == 'Non activée' and page.is_enabled('#storage-persist-btn') and ls(page) == before,
          'X6 refus : message, toujours "Non activée", bouton actif, aucune écriture')
    ctx.close()
    ctx, page, errors = fresh(b, PHONE, init_script=STORAGE % "'absent'")
    settings(page)
    check(not page.is_visible('#storage-persist-btn') and not page.net and not errors, 'X6 API absente : ligne masquée ; aucun appel réseau')
    ctx.close()

    b.close()
done()
