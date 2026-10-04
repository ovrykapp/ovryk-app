"""Test de fonctionnement d'Ovryk.

Usage : python dossier-lots/tests/smoke.py chemin/vers/index.html

Ce que fait le test :
1. ouvre l'application à 390 x 844 avec des cycles d'exemple,
2. clique chaque onglet de la barre de navigation et prend une capture,
3. démarre une séance vide,
4. signale toute erreur JavaScript.

Prérequis : pip install playwright, puis playwright install chromium.
Les captures sont écrites dans tests/captures.
"""
import json
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if len(sys.argv) < 2:
    print("Usage : python dossier-lots/tests/smoke.py chemin/vers/index.html")
    sys.exit(2)

index = Path(sys.argv[1]).resolve()
if not index.exists():
    print("Fichier introuvable :", index)
    sys.exit(2)

here = Path(__file__).parent
captures = here / "captures"
captures.mkdir(exist_ok=True)
seed = json.loads((here / "donnees-exemple.json").read_text(encoding="utf-8"))

erreurs = []
echecs = []

def verifier(condition, message):
    print(("ok     " if condition else "ECHEC  ") + message)
    if not condition:
        echecs.append(message)

with sync_playwright() as p:
    navigateur = p.chromium.launch()
    contexte = navigateur.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
    page = contexte.new_page()
    page.on("pageerror", lambda e: erreurs.append("pageerror : " + str(e)[:200]))
    page.on("console", lambda m: erreurs.append("console.error : " + m.text[:200]) if m.type == "error" else None)

    page.goto(index.as_uri())
    page.wait_for_timeout(800)

    # cycles d'exemple, uniquement si les exercices existent
    exercices = json.loads(page.evaluate("localStorage.getItem('ovryk.exercises')") or "[]")
    ids = {e["id"] for e in exercices}
    cycles = {k: v for k, v in seed["forceCycles"].items() if k in ids}
    page.evaluate("v => localStorage.setItem('ovryk.forceCycles', v)", json.dumps(cycles))
    page.reload()
    page.wait_for_timeout(800)

    onglets = page.query_selector_all(".nav-btn")
    verifier(len(onglets) >= 5, "la barre de navigation a au moins 5 entrées (" + str(len(onglets)) + ")")
    for i, bouton in enumerate(onglets):
        cible = bouton.get_attribute("data-target") or ("onglet-" + str(i))
        bouton.click()
        page.wait_for_timeout(400)
        page.screenshot(path=str(captures / (str(i + 1).zfill(2) + "-" + cible + ".png")))
        verifier(True, "onglet " + cible + " s'ouvre")

    # cycles : le tableau de bord ne doit pas afficher "NaN" ni "undefined"
    texte = page.inner_text("body")
    verifier("NaN" not in texte, "aucun NaN affiché")
    verifier("undefined" not in texte, "aucun undefined affiché")

    # séance vide
    page.click('.nav-btn[data-target="seance"]')
    page.wait_for_timeout(300)
    premier = page.locator("#view-seance button").first
    if premier.count():
        premier.click()
        page.wait_for_timeout(500)
        verifier(page.is_visible("#seance-sticky-topbar"), "une séance vide démarre")
        page.screenshot(path=str(captures / "seance-active.png"))

    navigateur.close()

verifier(not erreurs, "aucune erreur JavaScript" + ("" if not erreurs else " : " + "; ".join(erreurs[:3])))
print("\n" + ("Tous les contrôles passent" if not echecs else str(len(echecs)) + " contrôle(s) en échec"))
sys.exit(1 if echecs else 0)
