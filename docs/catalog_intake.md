# Catalog intake: receiving batches to Airtable

The Airtable side of the product intake workflow run by `app.rewake.fr`.
Operations register arriving products in the app (receiving batches, product
groups); the app pushes each group to Airtable as a **draft** once it has the
minimum fields, then a reviewer **validates** it. The app owns the workflow
state; the API only writes Airtable. Code: `api/services/catalog_sync.py`,
`api/services/catalog_lookup.py`, `api/domain/intake.py`,
`api/routes/internal/catalog/` (how the tables fit together:
[Catalog model](catalog_model.md)).

All routes are under `/internal/catalog`, with `APP_TOKEN` + `app.rewake.fr`
origin (like other internal routes).

## Endpoints

| Route | Does |
|---|---|
| `GET /options` | Brands, equipment types (with family), specification keys (with their `kind`), expected specs per family, Unit condition choices (`Etat esthétique`, `État fonctionnel`). Cached 10 min; `?refresh=true` reloads. |
| `POST /match` | Existing Models matching brand + model, with their Variations, through the catalog search below (Airtable formula lookup if the index is unavailable). A suggestion: a human picks. |
| `GET /airtable-links` | `base_id` and the table ids of Model, Variation and Units (`tables.model`, `.variation`, `.unit`), so the app can open a record at `https://airtable.com/{base}/{table}/{record}` (schema cached). |
| `POST /search` | Catalog search for the app: `results` for `q` (every word must match, partial words, any order, most relevant first; `limit` 10, max 30) and, separately, `suggestions` (default 3, max 10) from the item's `identity` (brand, model, serial, product_hint, label_text). 503 when the catalog index is unavailable. |
| `POST /units/sync` | Create or complete the Unit of one received item, as soon as operations finish it (see "Units of received items" below). |
| `POST /units/{id}/photos` | Add one of the operations' photos to the Unit's `Photos interne` (`image_b64`, `content_type` JPEG/PNG/WebP, `filename` `rw-<photo>-<kind>.<ext>`; 5 MB max); idempotent by file name → `attachment_id`. |
| `POST /units/{id}/photos/remove` | Remove these attachments (`attachment_ids`, 100 max), keep every other one → `removed`. |
| `POST /units/{id}/remove` | Delete a Unit the app created. **409 `unit_locked`** once engaged commercially; already gone: 200. |
| `POST /units/{id}/restore` | Put a pre-created reprise Unit's `fields` (snapshot) back; `restored: false` if it no longer exists. |
| `POST /groups/push` | Create or update a group: Model → Variation(s) → Specification(s) → Unit(s). |
| `POST /groups/validate` | `Statut validation Variation = Validé` on the group's `variation_ids`; `conversions` turn an existing default Variation into a variant (axis spec created, `is_variant = Oui`). **409 `shopify_confirmation_required`** when converting on a Model on Shopify without `confirm_shopify`. |
| `POST /groups/unvalidate` | Back to `À valider`. **409 `on_shopify`** if the Model has a `ShopifyID` or an `Annonces Shopify` record. |
| `POST /groups/cancel` | Delete what the group created (the Model only if `model_created`), give pre-created reprise Units their snapshot back (`restore_units`) and remove its accessory links (`compat_links`). **409 `on_shopify`** / **`unit_locked`**. |
| `POST /relationships/accessory` | Add an accessory Model to a host's `Compatibilité` row (`Machine fille`), creating the row if needed, and tick the accessory's `is_accessory`; idempotent. **409 `self_link`** for a Model as its own accessory. |
| `POST /relationships/accessory/remove` | Remove it again (`removed`). |
| `GET /reprises?q=` | `Opération reprise` records to receive: `Statut logistique = Appareils reçus` (set by the operations team when the equipment arrives) and `Statut opérationnel` not `Inventaire terminé`, newest first (100 max); `q` filters on the name and the seller company. |
| `GET /reprises/{id}` | The operation, its pre-created Units (each with the matched equipment row of its proposition) and unmatched equipment. |
| `GET /units/{id}` | A Unit's catalog fields, with the `snapshot` to restore if the item is removed. |
| `POST /units/photos` | `Photos client` (attachments on the Unit) of several Units, `{ids}` (200 max) → `{photos: {id: [{url, thumbnail, name}]}}`, images only, one Airtable call per 50 ids. Links expire after a few hours: the app caches them briefly, never stores them. |
| `GET /variations/{id}` | A Variation's name, `model_id`, `is_variant` and status (Référence variant checks), its Model's brand, reference and type (`brand`, `modele`, `type`: the item's known identity) and known `dimensions` (to pre-fill measurements). |
| `POST /reprises/{id}/received` | Operation `Statut logistique = Appareils reçus` (+ `Date de réception` if empty); returns the previous values. |
| `POST /reprises/{id}/received/undo` | Put the previous values back (409 `operation_changed` if the status moved meanwhile). |
| `POST /ocr` | Queue a label photo (`image_b64`, `content_type`; 8 MB max) for OCR; returns `job_id`. |
| `GET /ocr/{job_id}` | `queued` / `running` / `done` (+ `result`: `lines`, `fields`) / `failed` (+ `error`). |
| `POST /suggest-reference` | Référence variant of a received item (`brand`, `model`, `serial`, `product_hint`, `label_text`, `photos_text`, up to 4 `images`): existing Variations first (catalog index ranking, then the AI decides within the shortlist, with confidences), else a new reference mapped to the closest existing brands / models / types (a brand not in Airtable is flagged `new`). Heuristic ranking alone when the AI is off or unavailable (`ai_error`). The AI also reads the serial number (`read.serial`). Without a confident match, a second pass with `photos_text` (OCR of the other photos) when the `ocr_fallback` setting is on (`fallback_used`). 503 when the catalog is unavailable. See "Reference suggestion" below. |
| `POST /brands`, `POST /types` | Create a brand / equipment type the operator confirmed as new (idempotent by normalized name: an existing one comes back with `created: false`; a type's optional `famille` must be an existing family name, else 400). |
| `POST /spec-types` | Create a specification key (variant axis) the operator confirmed as new, with its `kind` (`Numérique` default, `Boolean`, `Text`); idempotent by normalized name. |
| `POST /research` | Queue the AI research of one product identity (`brand`, `model`, `product_hint`, `serial_example`, `label_text`; 422 without `model`, `product_hint` or `label_text`). Refused by the AI settings: **503 `not_configured`** (no AI provider has a key), **409 `disabled`**, **429 `daily_limit`** / **`budget`**. |
| `GET /research/{job_id}` | Same states as OCR; `result` is the proposal below. |
| `GET /review-queue` | Models to verify for the site, most urgent first (see "Commercial review" below); `?refresh=true` rebuilds now. `{models, age_seconds}`. |
| `POST /models/{id}/verify` | `Vérification pour site` checked, its Variations `Statut verification = Vérifié` (and `Validé` when still `À valider`: `validated_variations`). **409 `shopify_decision_required`** while `to_sell_on_shopify` is empty. |
| `POST /models/{id}/unverify` | Back to review: unchecked, Variations `Non vérifié` (a `Validé` status stays). |
| `GET /models/{id}/sheet` | A Model's full sheet for the commercial review (`?variation_id=` adds that Variation's status, unit count and specifications, the variant's own first; `?all_variations=true` adds `variation_list`: every Variation with its statuses, specifications and Units in stock with their `Photos interne`): identity, editable `fields`, `photos` (Photo neuve), `documents` (Documentation, Manuel Operateur, Manuel de service), `verified`, Shopify / accessory / compatibility flags. Attachment links expire: never stored. |
| `PATCH /models/{id}` | Correct the Model: `{changes, expected}` with keys `short_description`, `long_description`, `longueur_mm`, `hauteur_mm`, `profondeur_mm`, `poids_kg`, `prix_neuf_ht`, `dimension_exacte`, `poids_estime`, `notice_introuvable`, `to_sell_on_shopify` (`Oui` / `Non`). **409 `changed_in_airtable`** when Airtable no longer holds `expected` (nothing written); 422 for a bad value. |
| `POST /models/{id}/pdf` | The sales team's PDF of the model (`pdf_b64`, `filename`, `attach`, default true; 10 MB max, 422 if not a PDF): added to `Documentation` and read by the AI → the proposed sheet (see "Commercial review"). Synchronous (1-2 min). AI refusals as for `/research` (503 / 409 / 429); **502** when no AI model answered. |
| `POST /models/{id}/variants` | Create a proposed variant: `{axis, specs, convert_variation_id?}` (each `{spec_type_id, valeur, unite}`) → `{variation_id, created}`. **409 `on_shopify`** / **`already_variant`** when converting. |
| `POST /variations/{id}/specs` | Add a specification (`spec_type_id`, `valeur`, `unite`) to a Variation. |
| `PATCH /specs/{id}`, `DELETE /specs/{id}` | Change a specification's `valeur` / `unite` (value required, 200 characters max; 422 otherwise), or remove it (**409 `variant_axis`** for the spec that tells a variant apart). |
| `POST /models/{id}/documents` | Add a PDF by URL (`field`, `url`, optional `filename`) to `documentation`, `manuel_operateur` or `manuel_service` (others kept, same file name not added twice; a document in the first two clears « Notice Introuvable »). The link is checked first: 422 unless it is a reachable PDF on a public host. |
| `POST /describe` | AI rewrite of a product's descriptions (`name`, `brand`, `model`, `type`, `famille`, current texts, `specs`, optional `instruction`; 422 without `name` or `model`) → `short_description`, `long_description`, `issues` (e.g. the current text describes another product), `ai_call_id`, `ai_model`. A proposal: nothing written. AI refusals and 502 as for `/models/{id}/pdf`. |
| `POST /documents/search` | Queue the AI web search of a model's PDF documents (same identity; AI refusals as for `/research`); `GET /documents/search/{job_id}` → `documents` (`url`, `title`, `kind`, `language`, `covers`, `filename`, `size`), each checked to be a reachable PDF (`rejected` counts the others), and `notes`. |

Refusals are `409` with `detail = {"code", "message", ...}`; the app shows
the message.

## Push

Every entity in the request has a `ref`, a stable app-side id (`model`,
`variation:12`, `spec:40`, `unit:7`). The response maps each ref to its
Airtable record id (`ids`) and returns the fields written per record
(`written`), which the app sends back as `baseline` on the next push.

- **Created records**: Variations start as `À valider`. A variant Variation
  needs an `axis` spec: it is created with both `Variation associée` and
  `Spec_variant`, which makes it the Variation's `Variant_name`
  (`Variant_value` is a lookup of its `valeur`).
- **Selected records** (`created_by_group: false`): an existing Model or
  Variation is linked to, never edited.
- **Refusals** (409): `incomplete_model` (a created Model needs name, brand
  and type), `missing_model_id` / `missing_variation_id` (a selected record
  without its id), `missing_variant_axis`, `unknown_variation` (a Unit
  pointing to a Variation absent from the group).
- **No duplicates on retry**: each created record id is stored in Redis
  (`api:catalog:refs:<idempotency_key>`, 90 days) as soon as Airtable
  returns it. The `idempotency_key` must be stable per product group. A push
  that fails midway answers `502` with the `ids` created so far; sending the
  same push again resumes.
- **Conflicts**: for a record with a `baseline`, the current Airtable values
  are compared first. A field changed in Airtable since the last push (and
  not to the value the app wants) makes the record a conflict: it is not
  written, and the response has `status: "conflict"` with the differences.
- **Removed records** the group created earlier and no longer has:
  `removed_unit_ids` (refused if the Unit is engaged commercially: status
  Vendu/Commandé/Réservé/En enchères, or linked to a Vente, Devis or Vente
  aux enchères), `removed_spec_ids`, `removed_variation_ids` (refused,
  `variation_has_units`, if the Variation still has Units after this push
  re-linked them).
- **Restored Units** (`restored_units`): pre-created reprise Units given
  their snapshot back.

Airtable calls are retried on 429/5xx (1, 2, 4, 8 s).

## Units of received items (`CatalogSync.sync_unit`, `api/services/unit_photos.py`)

The app writes an item's Unit as soon as operations finish it, with no
commercial step (also for a new reference: the Unit links to its `À valider`
Variation). `POST /units/sync` writes `Référence variant`, `Numéro de série`,
`Etat esthétique`, `État fonctionnel`, `Commentaire atelier (état &
accessoires)` (written empty when cleared) and `Modules/Accessoires/Consommables`
(`host_variation_id`):

- with `airtable_id` (a pre-created reprise Unit, or one written before) it
  **completes** that record; `baseline` gives conflict detection as for a
  push (`status: "conflict"`, nothing written);
- without, it **creates** the Unit, remembered under `idempotency_key`
  (`app-unit:<item>`, Redis) so a retry never creates a second one (a
  remembered Unit deleted since is created again). Only at creation:
  `Opération reprise` (`creation.operation_id`) and, for an item of the
  reprise proposal (`creation.equipment_id`), that equipment row's
  `Prix de rachat` and `Photos` (as `Photos client`, read at that moment:
  attachment links expire).

The operations' photos go to `Photos interne`, one upload each through
Airtable's content API (`content.airtable.com/.../uploadAttachment`, base64,
5 MB max), named `rw-<photo id>-<kind>.<ext>`: a retry finds the attachment by
that name instead of adding it twice. Removing photos keeps every attachment
added by people. A removed item's Unit is deleted (`/units/{id}/remove`,
refused once engaged commercially) or, for a pre-created reprise Unit, given
its snapshot back (`/units/{id}/restore`) and the app's photos removed.

## Reprises (`api/services/catalog_reprise.py`)

An accepted reprise's Units already exist (`Opération reprise.Équipement
rachetés`), usually without a Variation. A receiving batch seeded from the
operation **completes** them (`POST /units/sync` with the pre-created Unit's
id). Such a Unit is never deleted: removing the item gives it back the
snapshot taken when it was received.

Equipment rows (`Équipements liés aux propositions de reprises`) of the
linked `Propositions de reprises` record have no link to the
Units: they are matched by normalized serial number (exact first, then one
containing the other, 5+ characters), one to one. When exactly one Unit and
one row are left and one of them has no serial, they are the same item.

The Unit's `Statut logistique reprise` is a lookup of the operation's
`Statut logistique`, so the received status is set on the operation.

## Not written by the API

- Variation `Short description`/`Long description`, `Variant_value`,
  `ShopifyID`, `Status Shopify`: lookups. Descriptions go on the Model.
- `Statut commercial`, `Prix de vente HT`: entered by people, never
  inferred. `Prix de rachat` is only copied from the reprise equipment row,
  `Prix neuf HT` only written by an explicit correction (`PATCH /models/{id}`).
- Shopify: drafts (`À valider`) are kept off Shopify by the existing filter;
  nothing here touches Shopify.

## Label OCR (`api/services/label_ocr.py`)

The app sends each receiving photo right after it is stored (every kind: the
label's fields are used now, the other photos' text feeds the reference
suggestion's fallback pass); capture never waits. `run_label_ocr` (Celery) posts the image to the `ocr` sidecar
(`ocr/`: RapidOCR, i.e. PaddleOCR models on ONNX Runtime, CPU, about 1 s per
label), then extracts candidates from the text lines in reading order:

- **serial**, from the surest to the least sure:
  1. value after `SN:` (the usual form), `S/N`, `Serial No.` (also as the OCR
     misreads it: `Serlal`, `Seria1`), `N° de série`, `Serien-Nr.`,
     `Ser.-Nr.`... (same line or the line below, or glued to the previous
     value: `ECN:390-1544SN:ICV18230008`), containing at least one digit;
  2. a line starting with `N:` (a cut `S/N:`), at half confidence;
  3. a word that only *looks like* a serial label (approximate match with
     `serial`, `seriennummer`, `numéro de série`..., e.g. `SeralHo.:`), at
     0.8 x confidence, flagged ``guess``;
  4. no label at all: the token shaped most like a serial (digits, letters
     and digits mixed, 8-14 characters), skipping ratings (`220V-240V`),
     dates, file names, addresses and model / part / contact lines, at 0.3 x
     confidence, flagged ``guess``;
- **model**: value after `Model` / `Model No.`, `Type`, `Device`, `Réf.`;
  only without one of these, `Cat. No.`, `P/N`, `Part No.`, `Art.-Nr.`;
- **brand**: the longest Airtable `Marque` name found as a word.

Each comes with the OCR confidence and the line it was read from; `fields`
also holds the whole `text` in reading order. Nothing is written to Airtable.
The task retries (3 times) when the sidecar is unreachable or slow. The sidecar is internal (`OCR_URL`, default
`http://ocr:8000`); CI builds and pushes it as `ghcr.io/<repo>-ocr` with the
same tags as the API image.

## AI product research (`api/services/product_research.py`)

Started by the app when operations mark a reception done: one job per
distinct product identity (brand + model read on the labels, else the reprise
equipment row or the devis line). Celery task `run_product_research`. Two
calls through the AI service, each on the feature's chain of AI models
(default: Claude Opus 5.5, then Sonnet 5.5, then OpenRouter once configured):

1. **research**: web search with adaptive thinking and high effort (Claude:
   server-side `web_search` + `web_fetch`, `pause_turn` resumed up to 4
   times; OpenRouter: the `web` plugin); the model writes notes with a source
   URL per fact and lists PDF datasheets/manuals;
2. **extraction**: notes -> strict JSON schema: French short and long
   descriptions, specifications **using existing `Specification type` names
   only** (anything else goes to `unmapped_facts`, enforced again in code),
   dimensions (mm) and weight (kg), documents, sources (plus the web
   results seen), confidence and `missing` fields.

The result also carries the research `notes`, `ai_call_id` (the extraction,
for feedback), `ai_call_ids` and `ai_models`.

A proposal only: nothing is written to Airtable here; the commercial team
creates the product from it in the app and reviews every value. Web content is
treated as data, never as instructions. The job fails when the whole chain is
unavailable (every AI model skipped or failed).

## Central AI service (`api/services/ai/`)

Every AI call of the API goes through `AIService.run(feature, request)`: one
provider-neutral request (`AIRequest`: system prompt, text, image and PDF
parts, optional JSON schema, web search, thinking, effort) tried on the feature's
**chain of AI models**, in order, until one answers.

- **Providers** (`providers/`): `anthropic` (Anthropic SDK, Messages API) and
  `openrouter` (chat completions, `https://openrouter.ai/api/v1`). Keys come
  from the environment only (`ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN`,
  `OPENROUTER_API_KEY`). Each provider translates the request (images, PDF,
  JSON schema, web search, effort) and maps its errors to one code:
  `rate_limited`, `no_credit`, `overloaded`, `timeout`, `connection`,
  `bad_request`, `refused`, `invalid_response`, `truncated`, `error`.
- **AI models** (`ModelProfile`, editable in the app's `/settings/ia`): an id,
  a label, a provider and its model id (e.g. `claude-opus-5-5`,
  `openai/gpt-5.2`), an optional manual price (USD per million tokens, input
  and output; overrides the list price in Anthropic cost estimates; 0 and 0 =
  **free**), on/off, **directives** appended to every request it
  serves, effort and max output tokens overrides, capabilities (reads images,
  web search, structured JSON) and its own limits (calls per day, monthly
  budget). Several AI models may share a provider model with different
  directives. Defaults: `claude-opus`, `claude-sonnet` (both with web
  search), `claude-haiku`, and `openrouter` (disabled until a model id is
  set).
- **Chains:** each feature lists AI model ids in priority order. An AI model
  is **skipped** when it is disabled, its provider is disabled or has no key,
  it lacks a capability the feature requires (`product_research` and
  `document_search`: web + JSON; `reference_suggestion`,
  `description_writing` and `pdf_extraction`: JSON; images are dropped for
  models without vision), or one of its limits is reached (model or provider daily calls /
  monthly budget, global budget). Free AI models skip every budget check, and
  a feature stays available past the global budget while its chain holds an
  enabled free model. It **fails over** to the next on any provider error, an
  invalid JSON answer or a JSON answer cut by the token limit (`truncated`) —
  without retrying it, except after a **rate limit**
  (429): the AI model then cools down (`general.retry_after_seconds`, 30 s, or
  its own `retry_after_seconds`) while the next usable model is tried at once;
  when only cooling models are left, the service waits for the first one and
  tries it again, up to `general.rate_limit_retries` new tries per model and
  `general.max_wait_seconds` of waiting per request (≤ 240 s, under the app's
  HTTP timeout). Cooldowns carry over between requests and processes (read
  from the call log). When nothing answers, `AIUnavailable` lists every
  attempt and its reason (synchronous routes answer 502; an async job
  fails; the reference suggestion falls back to its heuristic ranking).
- **Limits and budgets** (provider, AI model, feature, global): empty
  (``None``) = no limit, ``0`` = a real zero (no calls / nothing to spend).
  Settings version 2 used ``0`` for "no limit" and are migrated to ``None``.
- **Feature settings:** on/off, chain, daily call limit, image analysis and
  max images (reference suggestion: also `suggestions` and `ocr_fallback`),
  plus a global monthly budget (default 100 USD); these are checked before
  the chain (`AIBlocked`: 503 `not_configured`, 409 `disabled`, 429
  `daily_limit` / `budget`) and blocked attempts are recorded as `blocked`.
  Default daily limits: `product_research` 50, `reference_suggestion` 300
  (2 images), `description_writing` 200, `document_search` and
  `pdf_extraction` 100. Settings v1 (one model per feature) are migrated on
  read.
- **Recorded per attempt** (SQLite `AI_DB_PATH`, default
  `/home/rewake/DB/ai.sqlite`): feature, provider, AI model, served model,
  tokens (input, output, cache read/write), web searches, images, cost
  (Anthropic: estimated at list prices; OpenRouter: the `usage.cost` it
  bills), duration, status, error code, request id and subject. Limit skips
  are recorded as `blocked`; configuration skips are not.
- **Feedback:** results the app shows are reported back as `accepted` /
  `edited` / `rejected`, giving each feature's acceptance rate.
- **Errors:** stored as `code: message`; OpenRouter errors carry the
  upstream provider and its own reason (`metadata.raw`, also for errors
  returned with HTTP 200), invalid JSON keeps the start of the answer. A
  failed or limit-skipped attempt points to the call that answered instead
  (`fallback_call_id`).
- **Test:** `POST /internal/ai/models/test` (an AI model, saved or not) sends
  a tiny real request — "pong", a red test image if it reads images, a JSON
  schema if structured — and returns the answer, checks, served model,
  duration, cost and the catalog entry (or close ids). Recorded as feature
  `model_test` (`model_test.py`).
- **Routes** (`/internal/ai/*`): `GET/PUT /settings` (GET adds which
  providers have a key, each feature's label and requirements, and the price
  `catalog` in USD per million tokens: Anthropic list prices, OpenRouter's
  public `/api/v1/models` cached 6 h — `pricing.py`; PUT
  validates ids and chains and rejects unknown fields, 422), `GET /usage?days=` (per feature, per
  provider + AI model, per day), `GET /calls?limit=&feature=`,
  `POST /feedback` (`call_id`, `outcome`, optional `detail`),
  `POST /models/test`.
- **Token limit and reasoning:** a reasoning model spends hidden reasoning
  tokens within its output limit. On OpenRouter the limit sent is twice the
  answer's (`max_tokens`), with reasoning capped at the answer's size
  (`reasoning.max_tokens`) unless the AI model sets an effort or the request
  asks for thinking (then `reasoning.effort`); a JSON answer
  still cut (`finish_reason: length`, or Claude's `max_tokens`) is reported as
  `truncated`, with the reasoning tokens spent.
- **Claude specifics:** Opus/Sonnet 5.5 get adaptive thinking (when the
  feature asks for it), an explicit effort and the server-side refusal
  fallback (`fallbacks: "default"`); other Claude models (Haiku 4.5) get none
  of these and have no web search. Web turns and turns over 16,000 output
  tokens are streamed.

The features are `product_research` (web + JSON), `reference_suggestion`
(JSON), `description_writing` (JSON), `document_search` (web + JSON) and
`pdf_extraction` (JSON; the PDF is sent as a document: Claude reads it
natively, OpenRouter as a `file` part). `reference_suggestion`'s
system prompt holds the full brand, type and key lists and is cached
(`cache_control` on Claude; OpenRouter models cache per their provider), so
repeated suggestions mostly pay cache reads.

## Commercial review (`api/services/review_queue.py`, `api/services/model_sheet.py`, `api/services/product_assist.py`)

Units reach Airtable without the commercial team (see "Units of received
items" above); what they review is the **Model**, for the site.

**The queue** (`GET /review-queue`): every Model whose `Vérification pour
site` is unchecked and that has Units `A vendre` or `Non traité`, or a
Variation still `À valider` (a new reference created by operations). Order:
Models with Units `A vendre` first, those meant for the site
(`to_sell_on_shopify` not `Non`) before the others, by number of Units on
sale; then by Units `Non traité`; newest stock first among equals. Each entry
has its counts (`a_vendre`, `non_traite`, `non_teste`), `is_new`, `to_sell`,
`on_shopify`, `is_accessory`, and what its sheet lacks (`missing`: `description`, `photos`, `dimensions`,
`poids`, `shopify`). Reading it pages through the stock (~15 s): it is cached
in the process and rebuilt in the background after 5 minutes; a verified
Model leaves it at once, an unverified one comes back at the next rebuild.

**Verifying** (`POST /models/{id}/verify`) needs the Shopify decision
(`to_sell_on_shopify`, editable through `PATCH /models/{id}`), then checks
`Vérification pour site` and sets every Variation `Statut verification =
Vérifié`; a Variation still `À valider` becomes `Validé`.

The sheet (`GET /models/{id}/sheet?all_variations=true`) shows everything to
check. Corrections are explicit (`PATCH /models/{id}`) and optimistic: the app
sends the values it showed, and a field changed in Airtable meanwhile refuses
the whole edit rather than overwriting it. Specifications are edited per
Variation (`/variations/{id}/specs`, `/specs/{id}`).

AI help, proposals only:

- **The product's PDF** (`POST /models/{id}/pdf`, `pdf_extraction`): the
  sales team uploads the PDF they prepared for this model (10 MB max). It is
  added to the Model's `Documentation` (Airtable's content API, 5 MB max;
  `attached.reason`: `already_there` / `too_large` / `error` otherwise,
  `not_asked` with `attach: false`), then
  the AI reads it with the list of Airtable specification keys and returns
  the sheet in the web research's shape (`source: "pdf"`): descriptions,
  dimensions, weight, new price, specifications (Airtable spelling when the
  key exists), `variants` (axis key, value, unit, their own specifications),
  `unmapped_facts`, `issues` and `confidence` (`identified` is false when
  there are issues). Only what the PDF states; nothing is written
  besides the attachment. A proposed variant is created on request with
  `POST /models/{id}/variants` (`CatalogSync.add_variant`): a new Variation
  `À valider` with its axis and specifications (idempotent per Model, axis
  key and value: push key `app-variant:<model>:<key>:<value>`), or, with
  `convert_variation_id`, the Model's default Variation turned into that
  variant (refused on Shopify: `on_shopify`; already a variant:
  `already_variant`).
- **Descriptions** (`description_writing`): French, factual, short (one
  sentence) and long (2-4 paragraphs), from the identity, the specifications
  and the current texts; a current text about another product is not reused
  and is reported in `issues`.
- **PDF documents** (`document_search`, Celery task `run_document_search`):
  one web call with structured output (at most 6 documents, kinds `manual`,
  `service_manual`, `datasheet`, `brochure`, `other`, plus `notes` for the
  sales team); every link is then fetched (first bytes only, up to 5
  redirects followed by hand) and kept only if it is a PDF on a
  public host (no private, loopback or link-local address, at any hop). The
  same check runs again before a link is attached to the Model; Airtable then
  downloads the file from the URL.

## Reference suggestion (`api/services/reference_suggestion.py`)

Called by the app for one received item (`POST /suggest-reference`): which
**existing** Variation it is, else what new reference to create. Never raises
for AI reasons: without AI (disabled, limit, unavailable) the heuristic
ranking alone is returned with ``ai_error``.

1. The catalog index ranks every Variation against what is known of the item
   (brand, model, serial, seller's product name — for an accessory, also what
   it was found in — label text) and keeps a shortlist of 12.
2. The AI (feature ``reference_suggestion``, its chain of AI models; photos if
   the settings allow: `use_images`, up to `max_images`) returns ``matches`` among the numbered candidates with
   a confidence and a reason, the new-reference fields (brand as in the brand
   list, model reference, type from the type list, variant axis from the
   specification keys) and the **serial number** read on the label or photos
   (labels usually print it ``SN:``).
3. **Fallback pass:** when no candidate reaches 0.6 and ``photos_text`` (OCR
   of the item's other photos) is given, a second call adds that text
   (``ocr_fallback``, on by default); what only the first pass read is kept.
4. Result: ``match`` (``existing`` from 0.6), ``variations`` (the AI's
   matches; the heuristic ranking only when no AI answered; ``suggestions``
   items), ``new_reference`` (closest
   existing brands, models and types with confidences; ``brand_proposal``
   flagged ``new`` when not in Airtable — created only once the operator
   confirms, through ``POST /brands``), ``read.serial``, ``fallback_used``,
   ``rationale``, ``ai_call_id`` for feedback, ``ai_model``,
   ``images_used``.

The app keeps the result, so reloading never pays twice.

**Catalog search** (`CatalogIndex.search_models`): each searched word is
matched against the Model's brand, reference, equipment type, Variation
names and variant values — whole word 1, start of a word 0.85, inside a word 0.7, across
separators 0.65 (`ub90060` in `UB90.060.089`), close spelling 0.5. Every word
must match (with 3+ words, all but one, ranked lower); an exact or contained
reference adds to the score, popularity breaks ties. "2424", "Rotor" and
"rotor 2424" all find Rotor 2424. `suggest_models` turns the item ranking
below into up to 3 Models with their best Variation.

**Catalog index** (`api/services/catalog_index.py`): brands, types, Models
(with dimensions) and Variations (with unit counts) loaded from Airtable and
reloaded in the background when used after 15 minutes (invalidated after
pushes and brand / type / spec-type creations). It scores every Variation against the item — brand 0.35, model
reference 0.45, type 0.08, variant value on the label 0.05, popularity 0.07 —
and the top 12 go to the AI as numbered candidates; invented candidate
numbers are dropped. This replaces an MCP lookup: the full Variation list is
too large for a prompt, the shortlist is not. The number of proposals per
list is `reference_suggestion.suggestions` (1-5, default 3).
