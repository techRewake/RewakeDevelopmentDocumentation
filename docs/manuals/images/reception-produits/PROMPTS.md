# Prompts pour générer les images du manuel « Réception produits »

Un prompt par image du manuel ([`../../reception-produits.md`](../../reception-produits.md)),
à coller dans un générateur d'images. Chaque image générée remplace l'image
provisoire du même nom dans ce dossier.

## Mode d'emploi

1. Copiez le **style commun** ci-dessous, puis le prompt de l'image, dans le
   même message (le style garde les 24 images cohérentes entre elles).
2. Utilisez le **format** indiqué (portrait 9:16 pour un écran de téléphone,
   paysage 16:9 pour un schéma).
3. Enregistrez en PNG sous le **nom de fichier** indiqué (~1080 px de large).
4. Les générateurs écrivent mal le texte : gardez les quelques mots entre
   guillemets, corrigez-les au besoin dans un éditeur d'image.
5. 📸 = un **vrai capture d'écran** est préférable (l'interface exacte compte) ;
   le prompt sert alors d'alternative illustrée, ou de modèle pour annoter la
   capture (cercle rouge, main, numéros).

## Style commun (à coller avant chaque prompt)

```text
Style: IKEA-style assembly instruction illustration. Clean, uniform black line art
(2 px strokes) on a pure white background, flat, no shading, no gradients, no
photorealism, no 3D. One accent colour only: deep teal #1B5450, used for the
element to tap and for numbered step circles (white numbers in teal circles).
A simple outlined cartoon hand with the index finger pointing where the user must
tap. Friendly, minimal, lots of whitespace, rounded corners on screens and
buttons. Smartphones are drawn as simple rounded rectangles with a thin bezel.
Any text is short, in French, in a clean sans-serif font, and only where quoted
in the prompt. No logos, no brand names, no watermark, no people's faces.
```

Prompt négatif (si l'outil en propose un) :
`photorealistic, 3D render, gradient, shadow, clutter, long text, gibberish text,
watermark, logo, extra fingers, distorted hands, dark background`

---

## Image 0 — `00-cycle-article.png`

Format : paysage 16:9.

```text
A circular process diagram with five stations connected by arrows, going clockwise
and looping back: 1) a camera icon labelled "Photos", 2) a tag icon labelled
"Étiquette", 3) a tape measure icon labelled "Mesures", 4) a clipboard with a
checklist labelled "État", 5) a big teal check mark labelled "Terminé". From
"Terminé" a teal arrow loops back to "Photos" with the label "Article suivant".
In the centre, a simple outlined lab instrument (a benchtop centrifuge). Numbered
teal circles 1 to 5 next to each station.
```

## Image 1 — `01-autoriser-camera.png` 📸

Format : portrait 9:16.

```text
A smartphone screen showing a browser permission pop-up in the upper half: a small
camera icon, the question "Autoriser la caméra ?" and two buttons, "Bloquer"
(outlined) and "Autoriser" (filled teal). A cartoon hand taps "Autoriser". A teal
circle highlights the "Autoriser" button. Behind the pop-up, a faint blank web page.
```

## Image 2 — `02-tuile-reception.png` 📸

Format : portrait 9:16.

```text
A smartphone showing an intranet home page made of a grid of six rounded square
tiles, each with a simple line icon and a short label. One tile has a cardboard box
icon and the label "Réception produits"; it is outlined in teal with a teal circle
around it, and a cartoon hand taps it. The other tiles are plain and unlabelled
(just grey lines).
```

## Image 3 — `03-accueil-onglets.png` 📸

Format : portrait 9:16.

```text
A smartphone screen: at the top a large rounded search bar with a magnifying glass.
Below it a segmented control with three equal tabs: "En cours" (selected, white
with a small teal number badge "2"), "À réceptionner" (badge "5"), "Historique"
(badge "12"). Below, three list rows, each with a small rounded square icon tile
on the left, two grey text lines, and a teal button "Reprendre" on the right.
Numbered teal circles: 1 on the search bar, 2 on the tabs, 3 on a "Reprendre"
button.
```

## Image 4 — `04-reprise-receptionner.png` 📸

Format : portrait 9:16.

```text
A smartphone screen with the tab "À réceptionner" selected. A list of three rows;
each row has an orange-outlined delivery truck icon tile, a title line and a grey
details line ("3 unité(s)"). The first row's button "Réceptionner" is filled teal,
circled in teal, and a cartoon hand taps it. The other rows' buttons are plain.
Only the truck tiles use a light orange tint; everything else follows the style.
```

## Image 5 — `05-demarrer-reception.png` 📸

Format : portrait 9:16.

```text
A smartphone screen with a large rounded card. In the card: a big teal circle with
a white camera icon at the top, with two thin concentric "pulse" rings around it;
the title "Démarrer la réception"; a wide teal button "Commencer le premier article"
with a camera icon. Under the button, a small row of four tiny icons joined by
arrows: camera, tag, tape measure, clipboard. A cartoon hand taps the button.
```

## Image 6 — `06-camera-article-attendu.png` 📸

Format : portrait 9:16.

```text
A smartphone in full-screen camera mode, dark grey viewfinder. Centre: a white
rounded rectangle framing guide with a lab instrument's rating plate inside. Top:
a small pill with the hint "Photographiez l'étiquette". Bottom panel: the expected
item name as one bold white line, a grey line under it, three small chips (a tag
icon, a box icon, "+0"), and a big round white shutter button. Teal numbered
circles: 1 on the item name, 2 on the framing guide, 3 on the shutter.
```

## Image 7 — `07-photo-etiquette.png`

Format : paysage 16:9.

```text
Two side-by-side panels, IKEA do/don't style. Left panel: a phone held straight in
front of a metal rating plate on a lab instrument; the plate fills the phone's
rectangular frame, crisp lines; a large teal check mark below. Right panel: the same
scene but the phone is too far and tilted, with a bright glare spot on the plate and
wavy blur lines; a large black cross below. Small text under the left panel:
"Net, sans reflet".
```

## Image 8 — `08-photo-unite-entiere.png`

Format : paysage 16:9.

```text
A person's hands (outlined, no face) holding a phone at arm's length in front of a
benchtop lab instrument on a clean table. On the phone screen, the whole instrument
fits inside a square framing guide. A dotted teal arrow shows the person stepping
back. Numbered teal circle 1 near the arrow ("reculer"), 2 near the phone screen.
```

## Image 9 — `09-photos-facultatives.png` 📸

Format : portrait 9:16.

```text
A smartphone camera screen, bottom panel shown large. A horizontal row of rounded
chips, each with a tiny line icon: plug "Branchement" (with a small check mark),
square "Face", rotate arrow "Arrière" (selected: white chip with dark text),
open box "Intérieur", lightning "Tension". A cartoon hand taps "Arrière". Above
the chips, the hint pill "Photo facultative : Arrière". Big round shutter below.
```

## Image 10 — `10-camera-suite.png` 📸

Format : portrait 9:16.

```text
The bottom of a smartphone camera screen: two buttons side by side. Left, an
outlined white-text button "Photos seules". Right, a wider filled white button with
dark text "Étiquette, mesures, état →", outlined in teal with a teal circle, and a
cartoon hand tapping it. Above them, three small chips showing thumbnails with
check marks.
```

## Image 11 — `11-page-article.png` 📸

Format : portrait 9:16.

```text
A smartphone page header: a bold item title, a small line "Article 3/12" between a
left arrow and a right arrow. Below, a 2x2 grid of rounded step chips with icons:
camera "Photos" (teal, check mark), tag "Étiquette et référence" (teal, check
mark), tape measure "Mesures" (grey, dashed circle), clipboard "État" (grey, dashed
circle). Teal numbered circle 1 on the done chips, 2 on the to-do chips.
```

## Image 12 — `12-champs-etiquette.png` 📸

Format : portrait 9:16.

```text
Three stacked form fields on a phone screen: "Marque", "Modèle", "N° de série",
each a rounded input with a grey value and a small grey caption under it reading
"Lu sur l'étiquette (95 %)". Under the serial number field, an extra line with a
small sparkle icon in violet: "Lu par l'IA : 221209B038" and a small outlined
button "Utiliser", circled in teal, tapped by a cartoon hand. Beside the phone, a
small drawing of a rating plate with "SN:" highlighted by a teal arrow pointing to
the field.
```

## Image 13 — `13-reference-deja-liee.png` 📸

Format : portrait 9:16.

```text
A rounded card on a phone screen with a soft teal tint and teal border. Small grey
label "Référence variant · déjà liée dans Airtable", a bold product name line, a
grey "marque · modèle" line. On the right, a small ghost button "Autre référence"
and a filled teal button with a check mark "Confirmer", circled in teal and tapped
by a cartoon hand.
```

## Image 14 — `14-suggestions-references.png` 📸

Format : portrait 9:16.

```text
A rounded card with a light violet tint and a violet border, header with a small
violet sparkle icon and the text "Suggestions IA — à vérifier", and a small button
"Relancer l'IA". Inside, three white rows, each with a bold percentage on the left
("92 %", "41 %", "12 %"), a product name line, a grey details line, and a button
"Choisir" on the right; the first "Choisir" is filled teal, circled, and tapped by a
cartoon hand. Only the card uses violet; everything else follows the style.
```

## Image 15 — `15-nouvelle-reference.png` 📸

Format : portrait 9:16.

```text
A phone screen showing a creation form: a row of rounded chips with percentages
("Eppendorf 90 %", "Hettich 40 %"), an input "Modèle", a row of type chips. One chip
has a small orange badge "Nouveau dans Airtable" with a warning triangle. Near the
bottom, a checkbox with the label "J'ai vérifié la marque et la référence du
modèle", circled in teal, tapped by a cartoon hand, and a summary box "Sera créé
dans Airtable". Numbered teal circles: 1 on the chips, 2 on the orange badge, 3 on
the checkbox.
```

## Image 16 — `16-mesures.png`

Format : paysage 16:9.

```text
Left half: a benchtop lab instrument with a tape measure along its length, and
dimension arrows labelled "L", "l", "H". Right half: a phone screen with four
aligned inputs in a row, "Longueur", "Largeur", "Hauteur", "Poids · facultatif";
the first two have dashed teal borders and a small caption "connu (Airtable)".
Below, a small teal button "Confirmer les valeurs connues", tapped by a cartoon
hand. Teal arrows connect each dimension arrow to its input.
```

## Image 17 — `17-etat.png` 📸

Format : portrait 9:16.

```text
A phone screen with two dropdown selects stacked: "État esthétique" showing "Très
bon", "État fonctionnel" showing "100 % fonctionnel", then a multi-line text area
with the placeholder "Commentaire atelier (défauts, accessoires présents…)".
Numbered teal circles 1, 2 and 3 on the three fields. A small magnifying glass over
a scratch on a tiny instrument drawing in the corner.
```

## Image 18 — `18-accessoires-pieces.png`

Format : paysage 16:9.

```text
Two rounded cards side by side. Left card titled "Accessoires" with a box icon:
one row with a check circle, the name "Rotor F-34-6-38", a small chain-link icon and
the text "Compatible (Airtable)", and a full-width button "Ajouter un accessoire"
with a camera icon. Right card titled "Pièces incluses" with a plug icon: two
rounded pills "câble d'alimentation" and "spatule", each with a small "x", and a
full-width button "Ajouter une pièce incluse". Above the cards, a small drawing of
an open centrifuge with a rotor being lifted out, a teal arrow going to the left
card, and a power cable with a teal arrow going to the right card.
```

## Image 19 — `19-article-termine.png` 📸

Format : portrait 9:16.

```text
The bottom bar of a phone screen, sticky: a small outlined button "Réception" with
a list icon, a grey text "4/4 étapes", and a filled teal button with a check mark
"Article terminé → suivant", circled in teal and tapped by a cartoon hand. Above
the bar, a ghosted page with four teal check marks in a row.
```

## Image 20 — `20-reprendre.png` 📸

Format : portrait 9:16.

```text
A phone screen with the tab "En cours" selected. One highlighted row: a teal play
icon tile, a bold reception name, a grey line "Reprise … · activité le 09/10",
then two small stats "Reçus 5/8" and "Traités 3/5" with a thin teal progress bar,
and a large filled teal button "Reprendre" with a play icon, tapped by a cartoon
hand. A small clock icon in the corner suggests "later".
```

## Image 21 — `21-recapitulatif.png` 📸

Format : paysage 16:9.

```text
A wide card titled "Récapitulatif de la réception". A row of small rounded counter
pills at the top. Below, four stacked blocks, each with a coloured status icon on
the left and "reçu/attendu" with a tiny bar on the right: a green check "1/1"
with one nested item row under it (thumbnail, name, step chips); an amber
half-circle "1/2"; a grey dashed circle "0/1"; and a violet sparkle block "Hors
devis +1". Colours: green, amber, grey and violet only on the status icons and
bars; everything else in the common style. Numbered teal circles 1 to 4 on the
four statuses.
```

## Image 22 — `22-terminer.png` 📸

Format : paysage 16:9.

```text
Left: a rounded card "5. Fin des opérations" with a large filled teal button
"Terminer" with a check mark, tapped by a cartoon hand. Right: a confirmation
dialog "Terminer quand même ?" listing two bullet lines in grey ("1 article non
terminé", "1 attendu non reçu") with two buttons "Annuler" and "OK". A teal arrow
goes from the button to the dialog. Then a small arrow to a simple icon of a
document handed to another person's hand (no face), labelled "Commercial".
```

## Image 23 — `23-icones-photos.png`

Format : paysage 16:9.

```text
A clean legend sheet: a grid of eleven rounded square tiles in two rows, each tile
containing one simple monochrome line icon with its French label underneath:
tag "Étiquette", box "Unité entière", plug "Branchement", panel-top "Dessus",
square "Face", panel-left "Côté gauche", panel-right "Côté droit", rotate arrow
"Arrière", open box "Intérieur", lightning bolt "Tension", picture frame "Autre".
All icons in black line art, the tile borders in teal.
```
