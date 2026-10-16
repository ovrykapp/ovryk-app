"""Restauration locale (lot 16) : refus à l'import, sans rien écrire.
* Les 17 variantes de getBackupCrashError (14 qui feraient planter le
  démarrage, 3 sans identifiant), chacune avec une empreinte VALIDE pour que
  ce soit bien cette garde qui refuse.
* Les refus de format (vide, tronqué, autre app, versions, empreinte, listes).
* Les fichiers acceptés (témoins) : export de l'app, ancien format brut,
  enveloppe sans meta ni summary, quatre cas limites produits par l'app.
* Constat NON BLOQUANT : chaque variante injectée directement plante-t-elle
  le démarrage ? (cessera après le mini-lot des gardes de lecture.)
Données FABRIQUÉES ici. Usage : python3 test_restore_refus.py <dossier de travail>,
site servi sur OVRYK_URL (par défaut http://127.0.0.1:8765/index.html)."""
import copy, json
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
from restore_commun import *

F = workdir()
STARTS = '. Il empêcherait l’app de démarrer.'
NO_ID = '. Une sauvegarde faite par Ovryk en a toujours un.'

def base():
    d = dataset('imp', 2, 20)
    d['exercises'].append(dict(ex('ex-fab-l', 'Arraché fabriqué', 'Lifting'), liftBaseMode='force'))
    d['forceCycles'] = {'ex-fab-l': dict(CYCLE)}
    return d
DAY = '20 septembre 2026'   # date de la première séance de base(), telle que formatRestoreDay l'affiche

def v(fn):
    d = base(); fn(d); return d
VARIANTS = [
    ('exercice du catalogue vide', lambda d: d['exercises'].__setitem__(0, None), 'exercice n° 1 du catalogue vide' + STARTS),
    ('exercice sans identifiant', lambda d: d['exercises'][0].pop('id'), 'exercice n° 1 du catalogue sans identifiant' + NO_ID),
    ('routine vide', lambda d: d['routines'].__setitem__(0, None), 'routine n° 1 vide' + STARTS),
    ('routine sans identifiant', lambda d: d['routines'][0].pop('id'), 'routine n° 1 sans identifiant' + NO_ID),
    ('routine sans liste d\'exercices', lambda d: d['routines'][0].pop('exercises'), 'routine « Routine fabriquée imp » sans liste d’exercices' + STARTS),
    ('exercice de routine vide', lambda d: d['routines'][0]['exercises'].__setitem__(0, None), 'routine « Routine fabriquée imp », exercice n° 1 sans séries' + STARTS),
    ('exercice de routine sans séries', lambda d: d['routines'][0]['exercises'][0].pop('sets'), 'routine « Routine fabriquée imp », exercice n° 1 sans séries' + STARTS),
    ('séance vide', lambda d: d['sessions'].__setitem__(0, None), 'séance n° 1 vide' + STARTS),
    ('séance sans identifiant', lambda d: d['sessions'][0].pop('id'), 'séance n° 1 sans identifiant' + NO_ID),
    ('séance sans date valide', lambda d: d['sessions'][0].__setitem__('date', 'pas une date'), 'séance n° 1 sans date valide' + STARTS),
    ('séance sans liste d\'exercices', lambda d: d['sessions'][0].pop('exercises'), 'séance du ' + DAY + ' sans liste d’exercices' + STARTS),
    ('exercice de séance vide', lambda d: d['sessions'][0]['exercises'].__setitem__(0, None), 'séance du ' + DAY + ', exercice n° 1 vide ou sans séries' + STARTS),
    ('exercice de séance sans séries', lambda d: d['sessions'][0]['exercises'][0].pop('sets'), 'séance du ' + DAY + ', exercice n° 1 vide ou sans séries' + STARTS),
    ('série vide', lambda d: d['sessions'][0]['exercises'][0]['sets'].__setitem__(0, None), 'séance du ' + DAY + ', exercice n° 1, série n° 1 vide' + STARTS),
    ('cycle qui n\'est pas un objet', lambda d: d['forceCycles'].__setitem__('ex-fab-l', 5), 'cycle de force « ex-fab-l » vide ou inconnu' + STARTS),
    ('cycle vide', lambda d: d['forceCycles'].__setitem__('ex-fab-l', {}), 'cycle de force « ex-fab-l » vide ou inconnu' + STARTS),
    ('cycle d\'un type inconnu', lambda d: d['forceCycles']['ex-fab-l'].__setitem__('cycle_actif', '99'), 'cycle de force « ex-fab-l » vide ou inconnu' + STARTS),
]
assert len(VARIANTS) == 17

def refused(page, path, expect, label, before, dbs0, errors):
    import_file(page, path)
    msg = io(page)
    ok = msg == 'Import refusé : ' + expect and not restore_open(page) and ls(page) == before and dbs(page) == dbs0 and not errors
    check(ok, '%s : refusé, rien écrit, aucune base de copies (%s)' % (label, msg if not ok else expect[:70]))
    return ok

def accepted(page, path, label, before, dbs0, errors, extra=''):
    import_file(page, path)
    opened = restore_open(page)
    title = page.text_content('#restore-title') if opened else ''
    if opened: page.click('#restore-cancel-btn'); page.wait_for_timeout(200)
    ok = opened and title == 'Restaurer une sauvegarde' and not restore_open(page) and ls(page) == before and dbs(page) == dbs0 and not errors
    check(ok, '%s : accepté, écran de comparaison ouvert puis fermé sans rien écrire%s (%s)' % (label, extra, io(page) if not opened else title))

with sync_playwright() as p:
    b = p.chromium.launch()
    control_fixtures(b, F)

    # contexte unique pour les refus : un refus n'écrit rien, l'état de départ est revérifié à chaque fichier
    ctx, page, errors = fresh(b, dataset('tel', 3))
    settings(page); before = ls(page); dbs0 = dbs(page)

    # ---------- les 17 variantes, empreinte valide ----------
    n_ok = 0
    for i, (label, fn, expect) in enumerate(VARIANTS, 1):
        d = v(fn)
        env = envelope(d)
        path = write_file(F, 'variante-%02d.json' % i, env)
        n_ok += refused(page, path, 'fichier abîmé : ' + expect + ' Rien n’a été importé.', 'V%02d %s' % (i, label), before, dbs0, errors)
    check(n_ok == 17, 'V 17 variantes refusées sur 17 (%d)' % n_ok)

    # ---------- refus de format ----------
    good = envelope(base())
    tampered = copy.deepcopy(good); tampered['data']['exercises'][0]['name'] = 'Mouvement modifié après export'
    newer = base(); newer['meta']['schemaVersion'] = 3
    v2 = copy.deepcopy(good); v2['version'] = 2
    other = copy.deepcopy(good); other['app'] = 'Autre appli'
    no_sessions = base(); no_sessions.pop('sessions')
    bad_settings = base(); bad_settings['settings'] = ['kg']
    bad_cycles = base(); bad_cycles['forceCycles'] = ['ex-fab-l']
    bad_meta = base(); bad_meta['meta'] = 'deux'
    empty_lists = base(); empty_lists.update({'exercises': [], 'routines': [], 'sessions': []})
    text_good = json.dumps(good)
    FORMATS = [
        ('fichier vide (0 octet)', b'', 'ce fichier est vide.'),
        ('fichier fait d\'espaces', '  \n\t ', 'ce fichier est vide.'),
        ('JSON tronqué à la moitié', text_good[:len(text_good) // 2], 'fichier illisible (ce n’est pas du JSON).'),
        ('JSON qui n\'est pas un objet', '[1, 2, 3]', 'ce fichier n’est pas une sauvegarde Ovryk.'),
        ('JSON null', 'null', 'ce fichier n’est pas une sauvegarde Ovryk.'),
        ('autre application', other, 'ce fichier vient d’une autre application.'),
        ('version d\'enveloppe 2', v2, 'version de sauvegarde inconnue (2). Mets l’app à jour avant de restaurer.'),
        ('objet sans données', {'app': 'Ovryk', 'note': 'rien'}, 'ce fichier n’a pas le format d’une sauvegarde Ovryk.'),
        ('schemaVersion 3 (app plus récente)', envelope(newer), 'sauvegarde faite par une version plus récente de l’app. Mets l’app à jour avant de restaurer.'),
        ('empreinte différente (nom modifié après export)', tampered, 'fichier abîmé ou modifié (empreinte différente). Rien n’a été importé.'),
        ('liste des séances absente', envelope(no_sessions), 'fichier invalide : la liste des séances est absente ou invalide.'),
        ('réglages qui ne sont pas un objet', envelope(bad_settings), 'fichier invalide : réglages invalides.'),
        ('cycles qui ne sont pas un objet', envelope(bad_cycles), 'fichier invalide : cycles de force invalides.'),
        ('meta qui n\'est pas un objet', envelope(bad_meta), 'fichier invalide : version de schéma invalide.'),
        ('trois listes vides', envelope(empty_lists), 'ce fichier est vide, il ne contient aucune donnée.'),
    ]
    for i, (label, content, expect) in enumerate(FORMATS, 1):
        path = write_file(F, 'format-%02d.json' % i, content)
        refused(page, path, expect, 'R%02d %s' % (i, label), before, dbs0, errors)

    # ---------- témoins acceptés ----------
    app_env = json.loads((F / 'controle-empreinte.json').read_text(encoding='utf-8'))
    accepted(page, write_file(F, 'ok-export-app.json', app_env), 'A1 export produit par l\'app', before, dbs0, errors)
    accepted(page, write_file(F, 'ok-brut.json', {k: v_ for k, v_ in base().items() if k in ('exercises', 'routines', 'sessions')}),
             'A2 ancien format brut (listes à la racine)', before, dbs0, errors)
    no_meta = base(); no_meta.pop('meta')
    accepted(page, write_file(F, 'ok-sans-meta.json', {'app': 'Ovryk', 'exportedAt': '2026-10-01T08:30:00.000Z', 'version': 1, 'data': no_meta}),
             'A3 enveloppe sans meta ni summary (modèle de l\'ancien export)', before, dbs0, errors)
    edge = base()
    edge['sessions'].append(live_session('s-live'))
    edge['routines'].append({'id': 'r-vide', 'name': 'Routine en création', 'weekdays': [], 'updatedAt': '2026-09-01T00:00:00.000Z', 'exercises': []})
    edge['exercises'].append(ex('ex-perso', 'Exercice perso jamais fait'))
    edge['forceCycles']['ex-fab-l']['en_attente_de_validation'] = True
    accepted(page, write_file(F, 'ok-cas-limites.json', envelope(edge)),
             'A4 séance en cours, routine sans exercice, exercice perso sans historique, cycle en attente de validation', before, dbs0, errors)
    check(not page.net, 'aucun appel réseau (%s)' % page.net[:2])
    ctx.close()

    # ---------- constat non bloquant : la variante injectée directement plante-t-elle le démarrage ? ----------
    # séances datées d'aujourd'hui : l'Accueil ne lit les séries que pour la semaine en cours (sessionVolume) ;
    # une séance ancienne ne ferait rien planter et le constat serait trompeur (V13 avant cette correction).
    TODAY = datetime.now(timezone.utc).strftime('%Y-%m-%dT08:00:00.000Z')
    def this_week(d):
        for s in d['sessions']:
            if isinstance(s, dict) and s.get('date') != 'pas une date':
                s['date'] = s['startedAt'] = s['completedAt'] = TODAY
        return d
    crashes = []
    for i, (label, fn, expect) in enumerate(VARIANTS, 1):
        c, pg, errs = fresh(b, this_week(v(fn)))
        crashes.append(bool(errs))
        constat('V%02d %s injectée directement : %s' % (i, label, ('plante au démarrage (' + errs[0][:60] + ')') if errs else 'démarre sans erreur'))
        c.close()
    constat('%d variantes sur 17 plantent le démarrage aujourd\'hui, séances datées de la semaine en cours (les 3 "sans identifiant" ne plantent pas, par construction ; le refus à l\'import, lui, est vérifié plus haut)' % sum(crashes))

    b.close()
done()
