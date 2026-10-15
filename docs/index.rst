Rewake API
==========

The back-end API for Rewake -- internal tooling (used by the
``app.rewake.fr`` intranet app) and external integrations (HelloPro,
Machinio), served at `api.rewake.fr <https://api.rewake.fr>`_.

This documentation set is new (see :doc:`development` for why and what's
still missing); the API and its endpoints existed and were in production
well before it.

.. raw:: html

   <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin:28px 0 36px">
     <a href="https://app.rewake.fr" target="_blank" rel="noopener noreferrer" style="display:flex;flex-direction:column;justify-content:space-between;min-height:150px;padding:22px;border-radius:16px;background:linear-gradient(135deg,#152d4a,#2874a6);color:#fff;text-decoration:none;box-shadow:0 8px 22px #18334a30">
       <img src="https://app.rewake.fr/favicon.ico" alt="" width="36" height="36" style="object-fit:contain"/><span><strong style="font-size:20px">App</strong><br/><span style="opacity:.85">Open the Rewake team app</span></span>
     </a>
     <a href="https://admin.shopify.com/store/rewakedev" target="_blank" rel="noopener noreferrer" style="display:flex;flex-direction:column;justify-content:space-between;min-height:150px;padding:22px;border-radius:16px;background:linear-gradient(135deg,#164b38,#36a675);color:#fff;text-decoration:none;box-shadow:0 8px 22px #18334a30">
       <img src="https://cdn.simpleicons.org/shopify/ffffff" alt="" width="36" height="36" style="object-fit:contain"/><span><strong style="font-size:20px">Shopify Dev</strong><br/><span style="opacity:.85">Manage the development store</span></span>
     </a>
     <a href="https://grafana.rewake.fr" target="_blank" rel="noopener noreferrer" style="display:flex;flex-direction:column;justify-content:space-between;min-height:150px;padding:22px;border-radius:16px;background:linear-gradient(135deg,#713d19,#ef8b35);color:#fff;text-decoration:none;box-shadow:0 8px 22px #18334a30">
       <img src="https://cdn.simpleicons.org/grafana/ffffff" alt="" width="36" height="36" style="object-fit:contain"/><span><strong style="font-size:20px">Grafana</strong><br/><span style="opacity:.85">Explore metrics and dashboards</span></span>
     </a>
     <a href="https://status.rewake.fr" target="_blank" rel="noopener noreferrer" style="display:flex;flex-direction:column;justify-content:space-between;min-height:150px;padding:22px;border-radius:16px;background:linear-gradient(135deg,#3c286c,#7958c7);color:#fff;text-decoration:none;box-shadow:0 8px 22px #18334a30">
       <img src="https://raw.githubusercontent.com/louislam/uptime-kuma/master/public/icon.svg" alt="" width="36" height="36" style="object-fit:contain"/><span><strong style="font-size:20px">Kuma</strong><br/><span style="opacity:.85">Check service availability</span></span>
     </a>
     <a href="https://n8n.srv1336295.hstgr.cloud/home/workflows" target="_blank" rel="noopener noreferrer" style="display:flex;flex-direction:column;justify-content:space-between;min-height:150px;padding:22px;border-radius:16px;background:linear-gradient(135deg,#63254f,#d64a8b);color:#fff;text-decoration:none;box-shadow:0 8px 22px #18334a30">
       <img src="https://cdn.simpleicons.org/n8n/ffffff" alt="" width="36" height="36" style="object-fit:contain"/><span><strong style="font-size:20px">n8n</strong><br/><span style="opacity:.85">Open workflow automation</span></span>
     </a>
     <a href="https://github.com/rewake-fr" target="_blank" rel="noopener noreferrer" style="display:flex;flex-direction:column;justify-content:space-between;min-height:150px;padding:22px;border-radius:16px;background:linear-gradient(135deg,#24292f,#57606a);color:#fff;text-decoration:none;box-shadow:0 8px 22px #18334a30">
       <img src="https://cdn.simpleicons.org/github/ffffff" alt="" width="36" height="36" style="object-fit:contain"/><span><strong style="font-size:20px">GitHub</strong><br/><span style="opacity:.85">Browse Rewake repositories</span></span>
     </a>
   </div>

Reference
---------

- :doc:`routes` -- every endpoint, its access rules, and example responses.
- :doc:`authentication` -- the token/origin model behind those access rules.
- :doc:`architecture` -- how the project fits together, including the
  Celery/Redis queued tasks (scripts, OCR, AI research).
- :doc:`operations` -- configuration, deployment, and logging.
- :doc:`development` -- environment setup, Airtable/Shopify dev credentials,
  and the ``scripts/`` dev tooling.
- :doc:`scripts` -- what each registered script does, on demand or
  scheduled.
- :doc:`catalog_model` -- how Model, Variation and units are linked, how
  they become a Shopify product, and how to create a new one.
- :doc:`catalog_intake` -- the ``/internal/catalog`` routes behind the app's
  receiving workflow (draft push, validation, units, reprises, label OCR,
  reference suggestion) and commercial review (review queue, model sheet,
  verification), plus the central AI service behind ``/internal/ai``.

Manuals
-------

Step-by-step guides for the teams using the tools (in French):

- :doc:`manuals/reception-produits` -- receiving products in the intranet,
  article by article (operations team).

.. toctree::
   :maxdepth: 2
   :hidden:

   routes
   authentication
   architecture
   operations
   development
   scripts
   catalog_model
   catalog_intake
   translations

.. toctree::
   :maxdepth: 2
   :caption: Manuals
   :hidden:

   manuals/index
