# Routes

Liste complète des endpoints de l'API Rewake avec leurs règles d'accès et exemples de réponses.
La documentation interactive (OpenAPI) est servie par FastAPI sur `/docs` et `/redoc`.

---

## 🔍 Public

### `/health/`
- **Méthode** : `GET`
- **Accès** : Public (pas de token requis)
- **Description** : Vérifie que l'API est opérationnelle
- **Réponse** :
  ```json
  {
    "status": "healthy",
    "message": "API is running"
  }
  ```

### `/metrics`
- **Méthode** : `GET`
- **Accès** : Public (scrapé par Prometheus)
- **Description** : Exposition Prometheus calculée à chaque appel depuis la dernière
  exécution enregistrée de chaque script (voir [architecture](./architecture.rst)) :
  `rewake_api_script_metric{script, metric}`, `rewake_api_script_duration_seconds`,
  `rewake_api_script_last_run_success`, `rewake_api_script_last_run_timestamp_seconds`.

### `/invoice/get`
- **Méthode** : `GET`
- **Accès** : Public (pas de token)
- **Description** : Récupère une facture PDF sauvegardée par `POST /internal/invoice/analysis`
- **Query Params** : `hash` (string, **requis**) - Le hash renvoyé dans `file_location`
- **Réponse** : Fichier PDF (download), `Content-Type: application/pdf`
- **Erreurs** : `422` si aucun dossier ou aucun PDF pour ce hash

### `/pdf/{filename}`
- **Méthode** : `GET`
- **Accès** : Public (pas de token)
- **Description** : Sert un PDF généré par les routes `/internal/pdf/*` (dossier
  `/home/rewake/DB/PDF`) ; c'est l'URL attachée aux records Airtable.
- **Erreurs** : `404` si le fichier n'existe pas

### `/formulaire/photos/{airtable_id}/{filename}`
- **Méthode** : `GET`
- **Accès** : Public (pas de token)
- **Description** : Sert une photo envoyée par `POST /internal/formulaire/photos/upload/{airtable_id}`
- **Erreurs** : `404` si la photo n'existe pas

---

## 📊 HelloPro

### `/hellopro/csv/`
- **Méthode** : `GET`
- **Accès** : `HELLOPRO_TOKEN` (sans vérification d'origine)
- **Description** : Export des données CSV pour HelloPro (format pipe-delimited)
- **Réponse** :
  - Fichier CSV (download)
  - Content-Type: text/csv
  - Delimiter: `|`
  - Nom du fichier: `hellopro_export.csv`

---

## ⚙️ Machinio

### `/machinio/csv/`
- **Méthode** : `GET`
- **Accès** : `MACHINIO_TOKEN` (sans vérification d'origine)
- **Description** : Export des données CSV pour Machinio (format semicolon-delimited)
- **Réponse** :
  - Fichier CSV (download)
  - Content-Type: text/csv
  - Delimiter: `;`
  - Nom du fichier: `machinio_export.csv`

---

## 🔒 Interne

Toutes les routes `/internal/*` exigent `APP_TOKEN` **ET** une origine/referer
autorisée (ou `ADMIN_TOKEN`), sauf `/internal/scripts/*` qui accepte aussi
`AIRTABLE_AUTOMATION_TOKEN` sans origine (voir [authentication](./authentication.md)).

### `/internal/contact/check`
- **Méthode** : `GET`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Recherche les contacts potentiels dans la table "Personne" d'Airtable.
- **Stratégie** :
  - Email fourni → recherche par `Email OR Nom`, puis bonus prénom +3
  - Pas d'email → recherche par `Nom OR Prénom`
- **Scoring** : Email +15, Nom +10, Prénom +3
- **Note** : `best_match` n'est pas inclus dans `potential_contacts`
- **Query Params** (au moins un requis) :
  - `email` (string) : Email du contact
  - `nom` (string) : Nom du contact
  - `prenom` (string) : Prénom du contact
- **Réponse** :
  ```json
  {
    "exists": true,
    "best_match": {
      "id": "recXXX",
      "nom": "Dupont",
      "prenom": "Jean",
      "email": "jean.dupont@example.com",
      "mobile": "+33612345678",
      "poste": "Technicien",
      "entreprise": "Acme Corp",
      "score": 30
    },
    "potential_matching": 2,
    "potential_contacts": [
      {
        "id": "recXXX",
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "jean.dupont@example.com",
        "mobile": "+33612345678",
        "poste": "Technicien",
        "entreprise": "Acme Corp",
        "score": 30
      },
      {
        "id": "recYYY",
        "nom": "Dupont",
        "prenom": "Marie",
        "email": "m.dupont@example.com",
        "mobile": "+33698765432",
        "poste": "Manager",
        "entreprise": "Acme Corp",
        "score": 10
      }
    ]
  }
  ```
- **Erreurs** : `422` si aucun paramètre fourni, `500` si erreur Airtable

### `/internal/contact/update/{id}`
- **Méthode** : `PATCH`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Met à jour les champs fournis d'un record dans la table "Personne" d'Airtable.
- **Path Params** : `id` (string, requis) - L'ID du record Airtable
- **Request Body** (au moins un champ requis) :
  ```json
  {
    "nom": "Dupont",
    "prenom": "Jean",
    "email": "jean.dupont@example.com",
    "mobile": "+33612345678",
    "poste": "Technicien",
    "entreprise": ["recEntreprise1", "recEntreprise2"]
  }
  ```
- **Réponse** :
  ```text
  {
    "id": "recXXX",
    "fields": { ... }
  }
  ```
- **Erreurs** : `404` si contact introuvable, `422` si aucun champ fourni, `500` si erreur Airtable

### `/internal/contact/create`
- **Méthode** : `POST`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Crée un nouveau contact dans la table "Personne" d'Airtable.
- **Request Body** (au moins un champ requis) :
  ```json
  {
    "nom": "Dupont",
    "prenom": "Jean",
    "email": "jean.dupont@example.com",
    "mobile": "+33612345678",
    "poste": "Technicien",
    "entreprise": ["recEntreprise1"]
  }
  ```
- **Réponse** :
  ```text
  {
    "id": "recXXX",
    "fields": { ... }
  }
  ```
- **Erreurs** : `422` si aucun champ fourni, `500` si erreur Airtable

### `/internal/contact/entreprise/all`
- **Méthode** : `GET`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Liste les records de la table "Entreprise", sous forme de dict `{nom: record_id}`.

### `/internal/contact/entreprise/create`
- **Méthode** : `POST`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Crée un record dans la table "Entreprise".
- **Request Body** (au moins un champ requis) : `{"nom": "Acme Corp", "siret": "12345678900011"}`
- **Réponse** : `{"id": "recXXX", "fields": {...}}`
- **Erreurs** : `422` si aucun champ fourni, `500` si erreur Airtable

### `/internal/affaire/user/all`
- **Méthode** : `GET`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Liste les employés Rewake pour alimenter le sélecteur
  "Utilisateur" de l'extension Chrome. La réponse est un dict
  `{nom: record_id}` — `toOptionList()` en fait `{label: nom, value: record_id}`,
  et c'est le `record_id` qui est renvoyé comme `utilisateur_id` à
  `/internal/affaire/create`. L'extension n'affiche que le label.
- **Réponse** :
  ```json
  {
    "Marie-C": "recUzdhKEe8ugB3qJy",
    "Youri Remy": "rec9FPiDjDLS83Ku6"
  }
  ```

### `/internal/affaire/origine/all`
- **Méthode** : `GET`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Liste les valeurs possibles du champ "Origine de l'affaire"
  de la table Airtable "Affaires". C'est un `singleSelect` : il n'a pas de record
  associé, donc la réponse est une liste de strings et la valeur soumise à
  `/internal/affaire/create` est le libellé de l'option.
- **Réponse** :
  ```json
  ["Prospection mail", "Enchère", "Inbound - site web", "HelloPro", "..."]
  ```

### `/internal/affaire/create`
- **Méthode** : `POST`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Crée un record dans la table Airtable "Affaires" puis, si
  une date de relance a été fournie, une activité `relance` dans la table
  "Activité" liée à cette affaire. `Client` pointe sur la table "Personne",
  `Entreprise` sur "Entreprise" et `Propriétaire` sur "Employé Rewake", tous
  trois en lien — d'où l'écriture sous forme de liste de record ids.
- **Request Body** :
  ```json
  {
    "contact_id": "recXXX",
    "entreprise": "Rewake",
    "utilisateur_id": "recYYY",
    "nom": "Remplacement ascenseur",
    "origine": "Enchère",
    "date_relance": "2026-10-01"
  }
  ```
  - `entreprise` est le **nom** de la société (`best_match.entreprise` renvoyé par
    `/internal/contact/check`), pas son record id : la route le résout via la
    table "Entreprise".
  - `origine` est le libellé d'une valeur du `singleSelect`
    "Origine de l'affaire".
  - `date_relance` sort d'un `<input type="date">` (format `YYYY-MM-DD`). La
    table "Affaires" n'a pas de champ de relance : la date sert à créer
    l'activité. **Si elle est vide, l'activité n'est pas créée** — une relance
    sans date n'a rien à faire dans le planning.
- **Activité créée** (table "Activité") :
  ```json
  {
    "Name": "relance",
    "Quand ?": "2026-10-01",
    "Affaire": ["recZZZ"],
    "Propriétaire": ["recYYY"],
    "Entreprise": ["recWWW"]
  }
  ```
  Le champ `Type` est laissé vide.
- **Réponse** :
  ```json
  {
    "id": "recZZZ",
    "fields": {
      "Nom": "Remplacement ascenseur",
      "Origine de l'affaire": "Enchère",
      "Client": ["recXXX"],
      "Entreprise": ["recWWW"],
      "Propriétaire": ["recYYY"]
    }
  }
  ```
- **Erreurs** :
  - `422` si `nom` est vide, si `origine` n'est pas une valeur du `singleSelect`,
    si `entreprise` ne correspond à aucune Entreprise, si `utilisateur_id`
    n'est pas un employé connu, ou si `date_relance` n'est pas en `YYYY-MM-DD`
  - `500` si erreur Airtable. Si l'activité de relance échoue alors que l'affaire
    a bien été créée, **l'affaire est supprimée** avant de renvoyer le `500`, pour
    ne pas laisser de doublon si l'utilisateur réessaie.

### `/internal/backups/`
- **Méthode** : `GET`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Liste des backups (dossier `$VERIFICATION_SHOPIFY_DIR/backups`, hérité de
  l'ancien script `verification_shopify`) avec leurs fichiers et contenu (comparison.txt),
  plus récent d'abord ; `{"backups": []}` si le dossier n'existe pas
- **Réponse** :
  ```json
  {
    "backups": [
      {
        "name": "2024-01-15_12-00-00",
        "path": "<VERIFICATION_SHOPIFY_DIR>/backups/2024-01-15_12-00-00",
        "files": ["comparison.txt", "airtable.json", "shopify.json"],
        "hasComparison": true,
        "content": "Contenu de comparison.txt..."
      }
    ]
  }
  ```

### `/internal/fees/distritec`
- **Méthode** : `POST`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Calcule les frais de transport Distritec
- **Request Body** :
  ```json
  {
    "departureCity": 75,
    "arrivalCity": 13,
    "packages": [
      {
        "id": 1,
        "weight": 10.5,
        "portage": 2,
        "roulage": 0
      }
    ]
  }
  ```
  `departureCity`/`arrivalCity` sont des numéros de département ; `portage` est un
  nombre d'étages, `roulage` une distance en mètres.
- **Réponse** :
  ```text
  {
    "success": true,
    "total": 12345,
    "currency": "EUR",
    "fixedFees": 950,
    "breakdown": [...],
    "warning": "Possible surcharge de 57.11€ (île ou montagne). Total avec surcharge: XXX€"
  }
  ```
- **Erreurs** : `400` si `departureCity` ou `packages` manquant ou paramètre invalide

### `/internal/fees/compute/handling`
- **Méthode** : `POST`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Résumé logistique d'une proposition de reprise (table
  "Propositions de reprises") : équipements, poids/volume totaux, nombre de colis /
  palettes / non conditionnés, code postal.
- **Query Params** : `id` (string, **requis**) - L'ID du record Airtable
- **Erreurs** : `422` si un équipement non conditionné en colis n'a pas de poids ou de
  hauteur, ou si le code postal manque

### `/internal/fees/compute/dock`
- **Méthode** : `POST`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Calcule les frais logistiques « à quai » de la même proposition
  (forfait pour 75/92/93/94/95 et 77/78/91, sinon tarif du
  département, table "Grille tarifaire Granger") et les écrit dans `Frais logistique - À quai`.
- **Query Params** : `id` (string, **requis**)
- **Réponse** : `{"success": true}`
- **Erreurs** : `422` (données manquantes, département de montagne ou sans grille,
  équipement hors norme)

### `/internal/logs/`
- **Méthode** : `GET`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Récupère le contenu d'un fichier de log
- **Query Params** : `log` (nom du fichier, défaut: api.log) : un fichier du
  dossier des logs seulement ; un chemin qui en sort (`../.env`, chemin
  absolu) est refusé (400)
- **Réponse** (fichier absent : `content` vide) :
  ```json
  {
    "content": "Contenu du log...",
    "logName": "api.log"
  }
  ```

### `/internal/scripts/`
- **Méthode** : `GET`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide, ou `AIRTABLE_AUTOMATION_TOKEN`
  (vrai pour toutes les routes `/internal/scripts/*`)
- **Description** : Liste les scripts enregistrés (voir `api/scripts/registry.py`
  et [docs/architecture.rst](./architecture.rst))
- **Réponse** :
  ```text
  { "scripts": ["update_product", "create_product_shopify", "shopify_catalog_reconciliation", "airtable_catalog_stats"] }
  ```

### `/internal/scripts/{name}/run`
- **Méthode** : `POST`
- **Description** : Met en file d'attente (Celery) une exécution du script `name`.
  Query params : `record_id` (ID d'un **Model**) requis pour `create_product_shopify` ;
  pour `update_product`, exactement un de `record_id` (ID d'une Variation) ou
  `model_id` (ID d'un Model). Ignorés par les autres scripts.
- **Réponse** :
  ```text
  { "task_id": "...", "status": "queued", "script": "update_product" }
  ```
- **Erreurs** : `404` si `name` inconnu, `400` si `record_id` manque pour
  `create_product_shopify` ou si `update_product` ne reçoit pas exactement un de
  `record_id`/`model_id`

### `/internal/scripts/status/{task_id}`
- **Méthode** : `GET`
- **Description** : État d'une tâche mise en file par `POST /internal/scripts/{name}/run`
  (`PENDING`/`STARTED`/`RETRY`/`SUCCESS`/`FAILURE`) ; une fois terminée, `result`
  (succès) ou `error` (échec)
- **Réponse** :
  ```text
  {
    "task_id": "...",
    "status": "SUCCESS",
    "result": { "status": "success", "details": {...}, "metrics": {...}, "duration_seconds": 1.2, "finished_at": "..." }
  }
  ```

### `/internal/scripts/{name}/runs`
- **Méthode** : `GET`
- **Description** : Historique des exécutions de `name`, plus récentes d'abord (Redis,
  1000 dernières conservées par script)
- **Query Params** : `limit` (int, défaut 20, max 100), `offset` (int, défaut 0)
- **Réponse** :
  ```text
  { "script": "shopify_catalog_reconciliation", "runs": [ { "status": "success", "...": "..." } ], "total": 245 }
  ```
- **Erreurs** : `404` si `name` inconnu

### `/internal/scripts/{name}/current`
- **Méthode** : `GET`
- **Description** : Étapes en cours des exécutions de `name` (une par `record_id` en
  parallèle), pour suivre une exécution en direct ; vide si rien ne tourne
- **Réponse** : `{ "script": "create_product_shopify", "stages": [ ... ] }`
- **Erreurs** : `404` si `name` inconnu

### `/internal/invoice/analysis`
- **Méthode** : `POST`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Analyse une facture PDF et extrait les informations selon la source ;
  le PDF est sauvegardé et récupérable via `GET /invoice/get?hash=...`
- **Request** :
  - `file` : fichier PDF (multipart) - **requis**
  - `source` (query param) - **requis** - `surplus` ou `equipnet`
- **Réponse** :
  ```text
  {
    "file_info": {
      "filename": "nom_du_fichier.pdf",
      "content_type": "application/pdf",
      "size": 1024,
      "source": "surplus"
    },
    "file_location": "hash_du_fichier",
    "equipements": [...]
  }
  ```
- **Erreurs** : `400` si le fichier n'est pas un PDF ou si `source` manque

### `/internal/airtable/location/get/{record_id}`
- **Méthode** : `GET`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Récupère les informations de localisation d'une unité spécifique dans l'entrepôt
- **Path Params** : `record_id` (string, requis) - L'ID du record Airtable de l'unité
- **Réponse** :
  ```json
  {
    "name": "Nom de l'unité",
    "serialNumber": "Numéro de série",
    "imageUrls": ["https://url1.jpg", "https://url2.jpg"],
    "currentLocation": "Emplacement actuel",
    "possibleLocations": ["Emplacement 1", "Emplacement 2", "Emplacement 3"]
  }
  ```

### `/internal/airtable/location/update/{record_id}`
- **Méthode** : `POST`
- **Accès** : `APP_TOKEN` **ET** origine/referer valide
- **Description** : Mets à jour l'emplacement d'une unité spécifique dans l'entrepôt sur Airtable
- **Path Params** : `record_id` (string, requis) - L'ID du record Airtable de l'unité
- **Request Body** :
  ```json
  {
    "location": "Nouvel emplacement"
  }
  ```
- **Réponse** :
  ```json
  {
    "success": true,
    "message": "Location updated from 'Ancien emplacement' to 'Nouvel emplacement'"
  }
  ```

### Référentiels Airtable (`/internal/airtable/*`, `/internal/model/*`, `/internal/cache/*`)

Les routes `.../all` renvoient un dict `{nom: record_id}` (mis en cache) ; les
routes `create` renvoient `{"id": "recXXX", "fields": {...}}`, `422` si le nom est
vide, `500` si erreur Airtable.

| Route | Description |
|---|---|
| `GET /internal/airtable/brand/all` | Marques (table "Marque") |
| `POST /internal/airtable/brand/create?name=` | Crée une marque (vide le cache des marques) |
| `GET /internal/model/airtable/type/all` | Types d'équipement |
| `POST /internal/model/airtable/type/create?name=&categorieId=&familleId=` | Crée un type d'équipement |
| `GET /internal/model/airtable/famille/all` | Familles |
| `GET /internal/model/airtable/categorie/all` | Catégories |
| `POST /internal/model/create` | Crée un Model (`brandId`, `typeId`, `name`, `longueur`, `hauteur`, `profondeur` en mm) et sa Variation par défaut (`is_variant = Non`) |
| `POST /internal/cache/refresh` | Vide les caches Airtable (schéma, models, marques) → `{"success": true, "message": ...}` |

### Formulaires client (`/internal/formulaire/*`)

Formulaires remplis par le client (proposition de reprise, formulaire logistique
entreprise). `id` (query param, **requis**) est l'ID du record Airtable.

| Route | Description |
|---|---|
| `GET /internal/formulaire/reprise/get/proposition` | Proposition de reprise (table "Propositions de reprises") avec ses équipements dépliés |
| `PATCH /internal/formulaire/reprise/update/proposition` | Met à jour la proposition et ses équipements depuis le formulaire (corps JSON) ; `403` si `Modifiable par le client` est décoché |
| `PATCH /internal/formulaire/reprise/finish/proposition` | `Statut = Formulaire rempli`, plus modifiable par le client, puis notifie le responsable (webhook n8n) |
| `POST /internal/formulaire/photos/upload/{airtable_id}` | Upload multipart (`files`) des photos → `{"photos": [{filename, url}]}`, servies par `GET /formulaire/photos/...` |
| `GET /internal/formulaire/entreprise/get` | Champs du formulaire logistique (table "Formulaire logistique entreprise") |
| `PATCH /internal/formulaire/entreprise/update` | Met à jour ce formulaire ; `403` si `Modifiable par l'entreprise` est décoché |
| `PATCH /internal/formulaire/entreprise/finish` | `Statut = Terminé`, plus modifiable par l'entreprise |

Erreurs : `404` si le record n'existe pas, `500` si erreur Airtable.

### Génération de PDF (`/internal/pdf/*`)

Chaque route génère un PDF (WeasyPrint) dans `/home/rewake/DB/PDF`, servi par
`GET /pdf/{filename}`, et l'attache au record Airtable.

| Route | Description |
|---|---|
| `POST /internal/pdf/proposition_de_rachat/create?id=` | Proposition de rachat d'une proposition de reprise : crée un record dans la table "Propositions de rachat" → `record_id`, `file_number` |
| `POST /internal/pdf/bon_de_commande/create?proposition_id=&operation_id=` | Bon de commande attaché à l'"Opération reprise", brouillon Gmail dans la boîte du responsable, et une Unit par équipement à racheter → `file_number`, `units_created` |
| `POST /internal/pdf/logistique/fiche/create?id=` | Fiche logistique attachée à la proposition de reprise → `file_number` |
| `POST /internal/pdf/rapport_intervention?id=` | Rapport d'intervention ajouté au record "SAV" |

### Catalogue (`/internal/catalog/*`)

Routes du flux de réception et de la revue commerciale de `app.rewake.fr`. Le
détail (corps, réponses, codes `409`) est dans
[catalog_intake](./catalog_intake.md#endpoints).

| Route | Description |
|---|---|
| `GET /internal/catalog/options` | Marques, types, clés de spécification, états d'Unit (cache 10 min, `?refresh=true`) |
| `GET /internal/catalog/airtable-links` | `base_id` et IDs des tables Model / Variation / Units |
| `POST /internal/catalog/match` | Models existants correspondant à marque + modèle |
| `POST /internal/catalog/search` | Recherche catalogue (`q`) et suggestions depuis l'identité d'un article |
| `POST /internal/catalog/units/sync` | Crée ou complète l'Unit d'un article reçu |
| `POST /internal/catalog/units/photos` | `Photos client` de plusieurs Units |
| `GET /internal/catalog/units/{unit_id}` | Champs catalogue d'une Unit (+ `snapshot`) |
| `POST /internal/catalog/units/{unit_id}/photos` | Ajoute une photo à `Photos interne` |
| `POST /internal/catalog/units/{unit_id}/photos/remove` | Retire des pièces jointes |
| `POST /internal/catalog/units/{unit_id}/remove` | Supprime une Unit créée par l'app |
| `POST /internal/catalog/units/{unit_id}/restore` | Restaure une Unit de reprise |
| `POST /internal/catalog/groups/push` | Crée / met à jour un groupe (Model → Variations → Specs → Units) |
| `POST /internal/catalog/groups/validate` | Valide les Variations du groupe |
| `POST /internal/catalog/groups/unvalidate` | Les repasse `À valider` |
| `POST /internal/catalog/groups/cancel` | Supprime ce que le groupe a créé |
| `POST /internal/catalog/relationships/accessory` | Lie un accessoire à un Model hôte |
| `POST /internal/catalog/relationships/accessory/remove` | Retire ce lien |
| `GET /internal/catalog/reprises` | Opérations de reprise à réceptionner (`?q=`) |
| `GET /internal/catalog/reprises/{operation_id}` | Une opération, ses Units pré-créées et équipements |
| `POST /internal/catalog/reprises/{operation_id}/received` | Marque l'opération `Appareils reçus` |
| `POST /internal/catalog/reprises/{operation_id}/received/undo` | Annule ce marquage |
| `GET /internal/catalog/variations/{variation_id}` | Nom, Model, statut et identité d'une Variation |
| `POST /internal/catalog/ocr` | Met en file l'OCR d'une photo d'étiquette → `job_id` |
| `GET /internal/catalog/ocr/{job_id}` | État / résultat de l'OCR |
| `POST /internal/catalog/suggest-reference` | Suggestion de Référence variant (Variations existantes d'abord, IA) |
| `POST /internal/catalog/brands`, `POST /internal/catalog/types`, `POST /internal/catalog/spec-types` | Crée une marque / un type / une clé de spécification confirmée comme nouvelle |
| `POST /internal/catalog/research` | Met en file la recherche IA d'un produit → `job_id` |
| `GET /internal/catalog/research/{job_id}` | État / résultat de la recherche |
| `GET /internal/catalog/review-queue` | Models à vérifier pour le site, plus urgents d'abord |
| `GET /internal/catalog/models/{model_id}/sheet` | Fiche complète d'un Model pour la revue commerciale |
| `PATCH /internal/catalog/models/{model_id}` | Corrige le Model (`changes` / `expected`) |
| `POST /internal/catalog/models/{model_id}/verify` | Coche `Vérification pour site`, Variations `Vérifié` |
| `POST /internal/catalog/models/{model_id}/unverify` | Remet le Model en revue |
| `POST /internal/catalog/models/{model_id}/pdf` | PDF commercial du Model, lu par l'IA → fiche proposée |
| `POST /internal/catalog/models/{model_id}/documents` | Ajoute un PDF par URL (documentation, manuels) |
| `POST /internal/catalog/models/{model_id}/variants` | Crée une variante proposée |
| `POST /internal/catalog/variations/{variation_id}/specs` | Ajoute une spécification à une Variation |
| `PATCH /internal/catalog/specs/{spec_id}`, `DELETE /internal/catalog/specs/{spec_id}` | Modifie / supprime une spécification |
| `POST /internal/catalog/describe` | Réécriture IA des descriptions (proposition, rien n'est écrit) |
| `POST /internal/catalog/documents/search` | Met en file la recherche web IA des PDF d'un modèle → `job_id` |
| `GET /internal/catalog/documents/search/{job_id}` | État / documents trouvés |

### IA (`/internal/ai/*`)

Réglages et suivi du service IA central (`api/services/ai/`, voir
[catalog_intake](./catalog_intake.md)).

| Route | Description |
|---|---|
| `GET /internal/ai/settings` | Réglages, fournisseurs configurés, fonctions et catalogue de prix |
| `PUT /internal/ai/settings` | Modifie les réglages (`422` si champ inconnu ou ID invalide) |
| `POST /internal/ai/models/test` | Petite requête réelle avec un modèle IA |
| `GET /internal/ai/usage?days=` | Consommation par fonction, fournisseur et jour (défaut 30, max 365) |
| `GET /internal/ai/calls?limit=&feature=` | Derniers appels IA (défaut 50, max 500) |
| `POST /internal/ai/feedback` | Retour sur un résultat (`call_id`, `outcome`, `detail`) ; `404` si appel inconnu |

---

## Résumé des règles

| Route | Token requis | Origin/Referer requis |
|-------|--------------|---------------------|
| `/health/`, `/metrics` | ❌ Non | ❌ Non |
| `/invoice/get`, `/pdf/{filename}`, `/formulaire/photos/*` | ❌ Non | ❌ Non |
| `/hellopro/*` | ✅ Oui (`HELLOPRO_TOKEN`) | ❌ Non |
| `/machinio/*` | ✅ Oui (`MACHINIO_TOKEN`) | ❌ Non |
| `/internal/*` | ✅ Oui (`APP_TOKEN`) | ✅ Oui |
| `/internal/scripts/*` | ✅ Oui (`APP_TOKEN` ou `AIRTABLE_AUTOMATION_TOKEN`) | ✅ Oui avec `APP_TOKEN`, ❌ Non avec `AIRTABLE_AUTOMATION_TOKEN` |

`ADMIN_TOKEN` donne accès à toutes les routes protégées, sans vérification d'origine.
