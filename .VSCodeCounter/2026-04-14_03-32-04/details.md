# Details

Date : 2026-04-14 03:32:04

Directory /home/zo/Desktop/CODE/Projects/payment_gateway/app

Total : 45 files,  1472 codes, 155 comments, 400 blanks, all 2027 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [app/\_\_init\_\_.py](/app/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/api/\_\_init\_\_.py](/app/api/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/api/deps.py](/app/api/deps.py) | Python | 72 | 1 | 21 | 94 |
| [app/api/routes/\_\_init\_\_.py](/app/api/routes/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/api/routes/auth\_debug.py](/app/api/routes/auth_debug.py) | Python | 39 | 34 | 17 | 90 |
| [app/api/routes/merchants.py](/app/api/routes/merchants.py) | Python | 29 | 1 | 8 | 38 |
| [app/api/routes/payment\_intents.py](/app/api/routes/payment_intents.py) | Python | 148 | 0 | 21 | 169 |
| [app/api/routes/webhooks.py](/app/api/routes/webhooks.py) | Python | 112 | 0 | 25 | 137 |
| [app/core/\_\_init\_\_.py](/app/core/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/core/config.py](/app/core/config.py) | Python | 8 | 0 | 4 | 12 |
| [app/core/enums.py](/app/core/enums.py) | Python | 16 | 0 | 2 | 18 |
| [app/core/logging.py](/app/core/logging.py) | Python | 0 | 0 | 1 | 1 |
| [app/core/rate\_limit.py](/app/core/rate_limit.py) | Python | 56 | 0 | 19 | 75 |
| [app/core/security.py](/app/core/security.py) | Python | 10 | 0 | 2 | 12 |
| [app/core/state\_machine.py](/app/core/state_machine.py) | Python | 34 | 0 | 6 | 40 |
| [app/db/\_\_init\_\_.py](/app/db/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/db/base.py](/app/db/base.py) | Python | 8 | 2 | 3 | 13 |
| [app/db/models/\_\_init\_\_.py](/app/db/models/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/db/models/charge.py](/app/db/models/charge.py) | Python | 31 | 0 | 7 | 38 |
| [app/db/models/customer.py](/app/db/models/customer.py) | Python | 0 | 0 | 1 | 1 |
| [app/db/models/idempotency\_record.py](/app/db/models/idempotency_record.py) | Python | 12 | 16 | 10 | 38 |
| [app/db/models/merchant.py](/app/db/models/merchant.py) | Python | 14 | 0 | 4 | 18 |
| [app/db/models/payment\_intent.py](/app/db/models/payment_intent.py) | Python | 34 | 0 | 4 | 38 |
| [app/db/models/webhook\_event.py](/app/db/models/webhook_event.py) | Python | 29 | 6 | 14 | 49 |
| [app/db/session.py](/app/db/session.py) | Python | 18 | 0 | 5 | 23 |
| [app/main.py](/app/main.py) | Python | 32 | 12 | 9 | 53 |
| [app/schemas/\_\_init\_\_.py](/app/schemas/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/schemas/charge.py](/app/schemas/charge.py) | Python | 11 | 0 | 6 | 17 |
| [app/schemas/merchant.py](/app/schemas/merchant.py) | Python | 15 | 0 | 8 | 23 |
| [app/schemas/payment\_intent.py](/app/schemas/payment_intent.py) | Python | 39 | 3 | 17 | 59 |
| [app/schemas/webhook.py](/app/schemas/webhook.py) | Python | 34 | 0 | 10 | 44 |
| [app/services/\_\_init\_\_.py](/app/services/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/services/auth\_service.py](/app/services/auth_service.py) | Python | 8 | 0 | 8 | 16 |
| [app/services/charge\_service.py](/app/services/charge_service.py) | Python | 37 | 6 | 9 | 52 |
| [app/services/idempotency\_service.py](/app/services/idempotency_service.py) | Python | 70 | 5 | 12 | 87 |
| [app/services/payment\_intent\_service.py](/app/services/payment_intent_service.py) | Python | 351 | 47 | 76 | 474 |
| [app/services/payment\_service.py](/app/services/payment_service.py) | Python | 23 | 0 | 9 | 32 |
| [app/services/payment\_state\_machine.py](/app/services/payment_state_machine.py) | Python | 43 | 6 | 15 | 64 |
| [app/services/refund\_service.py](/app/services/refund_service.py) | Python | 5 | 0 | 2 | 7 |
| [app/services/webhook\_service.py](/app/services/webhook_service.py) | Python | 111 | 14 | 24 | 149 |
| [app/utils/api\_key.py](/app/utils/api_key.py) | Python | 3 | 2 | 4 | 9 |
| [app/utils/hashing.py](/app/utils/hashing.py) | Python | 20 | 0 | 6 | 26 |
| [app/workers/\_\_init\_\_.py](/app/workers/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [app/workers/celery\_app.py](/app/workers/celery_app.py) | Python | 0 | 0 | 1 | 1 |
| [app/workers/tasks.py](/app/workers/tasks.py) | Python | 0 | 0 | 1 | 1 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)