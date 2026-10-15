# Images du manuel « Réception produits »

Emplacements utilisés par le manuel [Réception produits](./reception-produits.md).
Une image « Provisoire » (colonne « État ») est grise (numéro et
description). Remplacez-la par la vraie capture dans
`docs/manuals/images/reception-produits/`, sous **exactement** le même nom.

**Captures de l'application** (recommandé) : déposez la capture brute
(téléphone, 1x) dans `images/reception-produits/raw/`, décrivez ses
pastilles dans `frames.json` (cadre cible en pixels de la capture, texte,
côté), puis :

```bash
uv run python docs/manuals/tools/phone_frame.py docs/manuals/images/reception-produits/frames.json
```

Le script met la capture dans un téléphone, ajoute les pastilles numérotées
et retire la bande du bas où se trouve le badge « N » de Next.js en
développement (mieux : capturer avec `devIndicators: false`). Images déjà
produites ainsi : 02 à 15, 17, 18, 20, 21 et 22.

**À refaire** (colonne « État ») : les captures 05 à 15, 17, 18, 21 et 22
montrent l'ancienne interface (page d'article en 4 étapes, récapitulatif par
ligne attendue). La réception se fait maintenant produit par produit en
5 étapes (Photos, N° de série, Variante, Mesures, État) ; la colonne
« Contenu attendu » décrit l'écran actuel. Après une nouvelle capture,
mettez à jour `frames.json` (pastilles) et la légende de l'image dans le
manuel, et retirez la mention « Ancienne interface ».

Pour les générer avec une IA d'images : un prompt par image dans
`docs/manuals/images/reception-produits/PROMPTS.md` (style commun inclus).

Conseils : captures sur téléphone (portrait), PNG, largeur ~1080 px ;
entourez en rouge l'élément à toucher ; floutez les noms de clients si besoin.

| Fichier | Titre | Contenu attendu | État |
|---|---|---|---|
| 00-cycle-article.png | Le cycle d'un produit | Schéma : les 5 étapes d'un produit en boucle (photos, n° de série, marque et modèle, mesures, état), puis « Produit complet » → produit suivant. | Provisoire |
| 01-autoriser-camera.png | Autoriser la caméra | Capture de la fenêtre du navigateur « Autoriser l'accès à la caméra ? » avec le bouton « Autoriser » entouré. | Provisoire |
| 02-tuile-reception.png | La tuile Réception produits | Page d'accueil de l'intranet, tuile « 📦 Réception produits » entourée. | À jour |
| 03-accueil-onglets.png | L'accueil et ses trois onglets | Accueil « Réception produits » : barre de recherche en haut, les trois onglets avec leur nombre, et quelques lignes en dessous. | À jour |
| 04-reprise-receptionner.png | Réceptionner une reprise | Onglet « À réceptionner », une ligne de reprise (nom, entreprise, nombre d'unités), bouton « Réceptionner » entouré, et une reprise déjà ouverte avec « Ouvrir ». | À jour |
| 05-demarrer-reception.png | Démarrer la réception | Liste des produits d'une réception qui vient d'être ouverte : « 0/N produit(s) complet(s) », lignes « À recevoir · touchez pour photographier », la première entourée. | À refaire (montre l'encadré « Démarrer la réception », supprimé) |
| 06-camera-article-attendu.png | La caméra et le produit attendu | Écran caméra : nom du produit en haut avec les 5 étapes, consigne, cadre de l'étiquette, pastilles Étiquette / Produit entier / +0, gros déclencheur blanc, « Sans étiquette » et « Importer ». | À refaire (montre la liste des articles et « Imprévu », supprimés) |
| 07-photo-etiquette.png | Photo de l'étiquette | Étiquette bien cadrée dans le cadre (texte net, sans reflet) ; à côté, un exemple raté (flou, reflet) barré d'une croix rouge. | À refaire |
| 08-photo-unite-entiere.png | Photo du produit entier | Appareil entier à l'écran, fond dégagé, consigne « Photographiez le produit entier ». | À refaire |
| 09-photos-facultatives.png | Photos facultatives | Rangée de pastilles avec leurs icônes, « Arrière » sélectionnée, « Branchement » cochée ✓. | À refaire |
| 10-camera-suite.png | Passer à la suite | Bas de l'écran caméra : bouton blanc « Suivant : n° de série → » entouré. | À refaire (montre « Photos seules », supprimé) |
| 11-page-article.png | L'écran d'un produit | Haut de l'écran d'un produit : nom, compteur « 3/5 », les 5 étapes (deux cochées), la troisième en cours. | À refaire (montre « Article précédent / suivant », supprimé) |
| 12-champs-etiquette.png | N° de série | Étape « N° de série » : photo de l'étiquette, champ pré-rempli « Lu sur l'étiquette », ligne « L'IA lit : 221209B038 — Utiliser », bouton « Valider le n° de série ». | À refaire |
| 13-reference-deja-liee.png | Référence déjà reliée | Étape « Marque et modèle » : référence avec le badge « Existe dans Airtable », boutons « Oui, c'est bien ce produit » (entouré) et « Non, ce n'est pas ce produit ». | À refaire |
| 14-suggestions-references.png | Proposé par l'IA | « Proposé par l'IA » avec « Relancer » : trois références « Existe dans Airtable » avec 92 %, 41 %, 12 % sûr, la première choisie, bouton « Choisir cette référence ». | À refaire |
| 15-nouvelle-reference.png | Créer une nouvelle référence | Écran « Nouvelle référence » : Marque, Modèle, Type d'équipement (un badge « nouveau dans Airtable »), « Ajouter une variante », récapitulatif « Sera créé dans Airtable », bouton « Créer dans Airtable ». | À refaire (montre la case « J'ai vérifié… », supprimée) |
| 16-mesures.png | Mesures | Les 4 champs de mesure, deux en violet « connu (Airtable) », bouton « Confirmer les valeurs connues », bouton « Valider les mesures » en bas. | Provisoire |
| 17-etat.png | État | Gros boutons « Aspect (esthétique) » et « Fonctionnement » (« Bon » et « Non testé » par défaut), commentaire atelier, encadré « Pièces incluses ». | À refaire |
| 18-accessoires-pieces.png | Accessoires et pièces incluses | À gauche, la fenêtre « Quel type de produit ? » avec « Un accessoire » entouré ; à droite, l'encadré « Pièces incluses » de l'étape État avec « câble d'alimentation », « spatule ». | À refaire |
| 19-article-termine.png | Produit complet | Écran « Produit complet » : coche verte, les 5 étapes résumées, boutons « Produit suivant : … » et « Retour à la liste ». | Provisoire |
| 20-reprendre.png | Reprendre une réception | Onglet « En cours » : une réception avec « Reçus 5/8 » et « Traités 3/5 », bouton « Reprendre » entouré. | À jour |
| 21-recapitulatif.png | La liste des produits | Liste d'une réception : « x/y produit(s) complet(s) » et %, un produit complet ✓, un « À recevoir », un « Imprévu », un accessoire 🧩, « Dans Airtable » sous un produit, menu ⋮ ouvert. | À refaire (montre l'ancien récapitulatif par ligne attendue) |
| 22-terminer.png | Terminer | Bas de la liste : « Tous les produits sont complets. », bouton « Terminer la réception » entouré, et la fenêtre « Terminer la réception ? ». | À refaire (montre l'encadré « 5. Fin des opérations », supprimé) |
| 23-icones-photos.png | Icônes des types de photo | Planche des 11 icônes de types de photo avec leur nom. | Provisoire |
