# Authentification

Le système d'authentification de l'API Rewake repose sur des **tokens Bearer** et une vérification optionnelle de l'origine/referer.

---

## Tokens

| Token | Description | Accès |
|-------|-------------|-------|
| `ADMIN_TOKEN` | Token administrateur | **Toutes les routes**, contourne la vérification d'origine |
| `HELLOPRO_TOKEN` | Token dédié HelloPro | Routes `/hellopro/*` uniquement |
| `MACHINIO_TOKEN` | Token dédié Machinio | Routes `/machinio/*` uniquement |
| `APP_TOKEN` | Token dédié à l'app interne | Routes `/internal/*` uniquement |
| `AIRTABLE_AUTOMATION_TOKEN` | Token envoyé par les automatisations Airtable (≠ `AIRTABLE_TOKEN`, que l'API envoie à Airtable) | Routes `/internal/scripts/*` uniquement |

> [!WARNING] 
> Les tokens doivent être définis dans `.env` et **ne jamais être commités**.

---

## Origines autorisées

L'API accepte les requêtes provenant des domaines suivants (quand la vérification de domaine est activée,
via l'en-tête `Origin` **ou** `Referer` ; `ALLOWED_ORIGINS` dans `api/utils/auth.py`) :
- `https://app.rewake.fr`
- `https://sav.rewake.fr`
- `https://info.rewake.fr`

Le CORS (`api/main.py`) n'autorise en revanche que `app.rewake.fr` et `sav.rewake.fr`.

Les routes publiques (`/health/`, `/metrics`, `/invoice/get`, `/pdf/{filename}`,
`/formulaire/photos/*`) ne demandent ni token ni origine (voir [routes](./routes.md)).

---

## Logique de vérification

### Avec `ADMIN_TOKEN`
Accès **automatique** à toutes les routes, **sans vérification d'origine/referer**.

### Règles par route

| Route | Vérification d'origine |
|-------|---------------------|
| `/hellopro/*` | ❌ Non (seulement `HELLOPRO_TOKEN` requis) |
| `/machinio/*` | ❌ Non (seulement `MACHINIO_TOKEN` requis) |
| `/internal/*` | ✅ Oui (`APP_TOKEN` **ET** origine/referer valide) |
| `/internal/scripts/*` | ✅ Oui avec `APP_TOKEN`, ❌ Non avec `AIRTABLE_AUTOMATION_TOKEN` |

> [!IMPORTANT] 
> `ADMIN_TOKEN` contourne toujours la vérification d'origine sur toutes les routes.

Quand l'origine est vérifiée, elle l'est **avant** le token : une requête sans
origine valide reçoit `403 Accès interdit: domaine invalide`, quel que soit le
token ; avec une origine valide mais un mauvais token, `403 Accès interdit: token invalide`.
Si la variable d'environnement d'un token n'est pas définie, seul `ADMIN_TOKEN`
ouvre les routes correspondantes.

---

## Exemples de requêtes

### Token seul (ADMIN_TOKEN)
```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" \
     http://localhost:3002/internal/logs/
# ✅ 200 - Accès autorisé (contourne l'origine)
```

### APP_TOKEN + Origin
```bash
curl -H "Authorization: Bearer APP_TOKEN" \
     -H "Origin: https://app.rewake.fr" \
     http://localhost:3002/internal/logs/
# ✅ 200 - Token valide + origine autorisée
```

### APP_TOKEN sans Origin
```bash
curl -H "Authorization: Bearer APP_TOKEN" \
     http://localhost:3002/internal/logs/
# ❌ 403 - Origin/Referer manquant
```

### HELLOPRO_TOKEN (pas de vérification d'origine)
```bash
curl -H "Authorization: Bearer HELLOPRO_TOKEN" \
     http://localhost:3002/hellopro/csv/
# ✅ 200 - Token valide, l'origine n'est pas vérifiée
```

### Automatisation Airtable (AIRTABLE_AUTOMATION_TOKEN)
Les automatisations Airtable tournent sur les serveurs d'Airtable, sans
`Origin`/`Referer` rewake.fr : ce token n'a donc pas de vérification
d'origine, mais n'ouvre que `/internal/scripts/*`.
```bash
curl -X POST -H "Authorization: Bearer AIRTABLE_AUTOMATION_TOKEN" \
     "http://localhost:3002/internal/scripts/create_product_shopify/run?record_id=recXXX"
# ✅ 200 - {"task_id": ..., "status": "queued", ...}

curl -H "Authorization: Bearer AIRTABLE_AUTOMATION_TOKEN" \
     http://localhost:3002/internal/backups/
# ❌ 403 - hors de /internal/scripts/*
```

### Origin sans Token
```bash
curl -H "Origin: https://app.rewake.fr" \
     http://localhost:3002/internal/logs/
# ❌ 403 - Token manquant
```
