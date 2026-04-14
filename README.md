# 💳 Payment Gateway API

A production-inspired payment processing backend built with **FastAPI** that simulates real-world payment gateway operations like Stripe. This project demonstrates modern backend engineering patterns through a complete payment flow: merchant authentication, payment intent creation, payment method attachment, confirmation, and webhook-based event delivery.

**Table of Contents**
- [What This Project Does](#what-this-project-does)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Core API](#core-api)
- [Payment Flow](#payment-flow)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [What I Learned](#what-i-learned)

---

## What This Project Does

This payment gateway simulates a real payment processor (like Stripe) with the following capabilities:

- **Merchant Management**: Register merchants and generate secure API keys for authentication
- **Payment Intents**: Create high-level payment operations with lifecycle management
- **Payment Methods**: Attach payment method references to intents before confirmation
- **Payment Processing**: Confirm and process payments through a state machine
- **Webhooks**: Deliver payment events asynchronously with automatic retry logic
- **Idempotency**: Safely retry failed requests without duplicate processing
- **Rate Limiting**: Merchant-scoped request throttling for payment operations

Perfect for:
- Learning payment gateway architecture and patterns
- Understanding state machines and event-driven systems
- Exploring production backend practices (separation of concerns, testing, migrations)
- Building a reference implementation for payment processing workflows

---

## Key Features

| Feature | Details |
|---------|---------|
| 🔐 **API Authentication** | Hashed API key storage with Bearer token auth |
| 💰 **Payment Lifecycle** | Multi-state flow: payment_method → confirmation → processing → success/failure |
| 💳 **Payment Methods** | Attach payment method references before confirming payments |
| ⚡ **Charge Management** | Automatic charge creation and state tracking |
| 🔁 **Idempotency** | Safe retries using Idempotency-Key header |
| ⏱️ **Rate Limiting** | Per-merchant request throttling (configurable window) |
| 🔔 **Webhook Events** | Automatic event creation and async delivery with retries |
| 🧪 **Comprehensive Tests** | 10+ integration test files covering all flows |
| 🗄️ **Database Migrations** | Alembic-managed schema evolution |
| 🧱 **Clean Architecture** | Layered design: routes → services → models |
| 📋 **Documentation** | Full architectural guide in [SEPARATION_OF_CONCERNS.md](SEPARATION_OF_CONCERNS.md) |

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **pip** or **poetry**
- **Redis** (optional, for rate limiting)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/payment-gateway.git
   cd payment-gateway
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   alembic upgrade head
   ```

5. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`

---

## Usage Example

### 1. Create a Merchant

```bash
curl -X POST http://localhost:8000/merchants/
```

Response:
```json
{
  "id": 1,
  "name": "My Store",
  "api_key": "sk_test_abc123...",
  "webhook_url": null,
  "created_at": "2026-04-14T10:30:00Z"
}
```

Save the `api_key` — you'll use this for all merchant operations.

### 2. Create a Payment Intent

```bash
curl -X POST http://localhost:8000/payment_intents/ \
  -H "Authorization: Bearer sk_test_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "currency": "USD"
  }'
```

Response:
```json
{
  "id": 1,
  "merchant_id": 1,
  "amount": 5000,
  "currency": "USD",
  "status": "requires_payment_method",
  "created_at": "2026-04-14T10:31:00Z"
}
```

### 3. Attach Payment Method

```bash
curl -X POST http://localhost:8000/payment_intents/1/attach_payment_method \
  -H "Authorization: Bearer sk_test_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method_reference": "pm_test_visa_4242"
  }'
```

Status updates to `requires_confirmation`.

### 4. Confirm Payment

```bash
curl -X POST http://localhost:8000/payment_intents/1/confirm \
  -H "Authorization: Bearer sk_test_abc123..."
```

Status updates to `succeeded` or `failed`. A webhook event is created and delivered asynchronously.

### 5. List Payment Intents with Filters

```bash
curl -X GET "http://localhost:8000/payment_intents/?status=succeeded&currency=USD&limit=10" \
  -H "Authorization: Bearer sk_test_abc123..."
```

---

## Project Structure

```
payment-gateway/
├── app/
│   ├── api/
│   │   ├── deps.py                    # Dependency injection (auth, db session)
│   │   └── routes/
│   │       ├── auth_debug.py          # Auth endpoints for testing
│   │       ├── merchants.py           # Merchant CRUD
│   │       ├── payment_intents.py     # Payment intent operations
│   │       └── webhooks.py            # Webhook test endpoints
│   ├── core/
│   │   ├── config.py                  # App settings
│   │   ├── enums.py                   # Status enums
│   │   ├── logging.py                 # Logging configuration
│   │   ├── security.py                # Auth utilities
│   │   ├── rate_limit.py              # Rate limiting logic
│   │   └── state_machine.py           # Status transition rules
│   ├── db/
│   │   ├── base.py                    # SQLAlchemy declarative base
│   │   ├── session.py                 # DB engine and session factory
│   │   └── models/
│   │       ├── merchant.py            # Merchant model
│   │       ├── payment_intent.py      # PaymentIntent model
│   │       ├── charge.py              # Charge model
│   │       ├── webhook_event.py       # WebhookEvent model
│   │       └── idempotency_record.py  # Idempotency tracking
│   ├── schemas/
│   │   ├── merchant.py                # Merchant Pydantic schemas
│   │   ├── payment_intent.py          # PaymentIntent schemas
│   │   └── webhook.py                 # Webhook schemas
│   ├── services/
│   │   ├── auth_service.py            # Authentication logic
│   │   ├── payment_intent_service.py  # PaymentIntent operations
│   │   ├── charge_service.py          # Charge creation/processing
│   │   ├── webhook_service.py         # Webhook event creation/delivery
│   │   ├── idempotency_service.py     # Idempotency key handling
│   │   ├── refund_service.py          # Refund operations
│   │   └── payment_state_machine.py   # State transition logic
│   ├── utils/
│   │   ├── api_key.py                 # API key generation
│   │   └── hashing.py                 # Secure hashing
│   ├── workers/
│   │   ├── celery_app.py              # Celery configuration
│   │   └── tasks.py                   # Background tasks
│   └── main.py                        # FastAPI app initialization
├── tests/
│   ├── test_merchants.py              # Merchant endpoint tests
│   ├── test_payment_intents.py        # Payment intent tests
│   ├── test_attach_payment_method.py  # Payment method attachment tests
│   ├── test_confirm_payment.py        # Confirmation flow tests
│   ├── test_cancel_payment.py         # Cancellation tests
│   ├── test_auth.py                   # Authentication tests
│   ├── test_idempotency.py            # Idempotency tests
│   ├── test_rate_limiting.py          # Rate limiting tests
│   ├── test_webhooks.py               # Webhook delivery tests
│   └── test_payment_state_machine.py  # State transition tests
├── alembic/
│   └── versions/                      # Database migration files
├── requirements.txt                   # Python dependencies
├── alembic.ini                        # Alembic configuration
├── SEPARATION_OF_CONCERNS.md          # Detailed architecture guide
└── README.md                          # This file
```

---

## Core API

### Merchants

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/merchants/` | Create a new merchant account |
| GET | `/merchants/me` | Get authenticated merchant details |

### Payment Intents

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/payment_intents/` | Create a new payment intent |
| GET | `/payment_intents/{id}` | Retrieve a specific payment intent |
| GET | `/payment_intents/` | List payment intents with filters |
| POST | `/payment_intents/{id}/attach_payment_method` | Attach a payment method |
| POST | `/payment_intents/{id}/confirm` | Confirm and process the payment |
| POST | `/payment_intents/{id}/cancel` | Cancel a payment intent |

### Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhooks/test-receiver` | Test webhook receiver endpoint |
| GET | `/webhooks/events` | List webhook events for your merchant |

**View complete API documentation at `/docs` when the server is running.**

---

## Payment Flow

1. Merchant creates a payment intent  
2. Status = `requires_payment_method`  
3. Merchant attaches a payment method  
4. Status = `requires_confirmation`  
5. Merchant confirms payment  
6. System creates charge and processes payment
7. Status updates to `succeeded` or `failed`  
8. Webhook event is created  
9. Webhook is delivered asynchronously in background  

---

## Payment Flow

The payment workflow follows a multi-step state machine:

```
Create Intent           Attach Method           Confirm Payment
(REQUIRES_PAYMENT_METHOD) → (REQUIRES_CONFIRMATION) → (PROCESSING)
                                                          ├→ SUCCEEDED
                                                          └→ FAILED
                    ↓ (anytime)
                CANCELED
```

### Flow Steps

1. **Create Intent**: Merchant creates a payment intent specifying amount and currency
2. **Attach Payment Method**: Merchant attaches a payment method reference
3. **Confirm**: Merchant confirms payment, triggering charge creation
4. **Processing**: System processes the charge
5. **Resolution**: Payment succeeds or fails, webhook event is created
6. **Delivery**: Webhook event is delivered asynchronously with retries

### Key Design Principles

- **Idempotent Operations**: Use `Idempotency-Key` header to safely retry requests
- **State Machine**: Enforces valid state transitions to prevent invalid operations
- **Event-Driven**: Webhook events are automatically created on status changes
- **Background Processing**: Webhook delivery happens asynchronously without blocking the request

---

## Architecture

### Layered Design

```
┌─────────────────────────────────────────────────┐
│                  FastAPI Routes                  │
│         (HTTP request handling, validation)      │
├─────────────────────────────────────────────────┤
│                    Services                      │
│      (Business logic, state transitions,         │
│       database operations, webhooks)             │
├─────────────────────────────────────────────────┤
│                   Database                       │
│        (SQLAlchemy ORM, SQLite storage)          │
└─────────────────────────────────────────────────┘
```

### Key Concepts

- **Routes** (`app/api/routes/`): Handle HTTP requests, authentication, and validation
- **Services** (`app/services/`): Implement business logic and coordinate operations
- **Models** (`app/db/models/`): Define database schema using SQLAlchemy
- **Schemas** (`app/schemas/`): Validate request/response payloads with Pydantic
- **Dependencies** (`app/api/deps.py`): Inject authenticated merchant and database session

### Service Responsibilities

| Service | Responsibility |
|---------|-----------------|
| `auth_service.py` | API key verification and merchant authentication |
| `payment_intent_service.py` | PaymentIntent CRUD and lifecycle management |
| `charge_service.py` | Charge creation and processing |
| `webhook_service.py` | Event creation and async delivery |
| `idempotency_service.py` | Idempotency key tracking and replay |
| `payment_state_machine.py` | Valid state transitions and validation |

For detailed architectural guidance, see [SEPARATION_OF_CONCERNS.md](SEPARATION_OF_CONCERNS.md).

---

## Running Tests

The project includes comprehensive test coverage for all major features:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_payment_intents.py

# Run tests matching a pattern
pytest -k "idempotency"

# Run with coverage report
pytest --cov=app
```

**Test Files:**
- `test_merchants.py` — Merchant creation and authentication
- `test_payment_intents.py` — Payment intent CRUD operations
- `test_attach_payment_method.py` — Payment method attachment flow
- `test_confirm_payment.py` — Payment confirmation and charge creation
- `test_cancel_payment.py` — Payment cancellation
- `test_auth.py` — API key authentication
- `test_idempotency.py` — Idempotent request handling
- `test_rate_limiting.py` — Rate limit enforcement
- `test_webhooks.py` — Webhook event creation and delivery
- `test_payment_state_machine.py` — State transition validation

---

## Configuration

Configuration is managed through environment variables in [app/core/config.py](app/core/config.py):

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `sqlite:///./payment_gateway.db` | SQLite database path |
| `WINDOW_SECONDS` | `60` | Rate limiting window (seconds) |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection for rate limiting |

---

## Development Workflow

### Database Migrations

Migrations are managed with Alembic. When you modify models:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Adding New Endpoints

1. Create route in `app/api/routes/`
2. Implement business logic in `app/services/`
3. Add Pydantic schemas in `app/schemas/`
4. Add tests in `tests/`
5. Update migration if schema changed

---

## Getting Help

### Documentation
- **API Docs**: Visit `http://localhost:8000/docs` (interactive Swagger UI)
- **Architecture**: See [SEPARATION_OF_CONCERNS.md](SEPARATION_OF_CONCERNS.md) for detailed design patterns
- **Code Comments**: All services include docstrings explaining key functions

### Common Issues

**Issue: `ModuleNotFoundError` when running tests**
- Solution: Ensure you're in the project directory and have activated the virtual environment

**Issue: Database locked errors**
- Solution: Delete `payment_gateway.db` and re-run `alembic upgrade head`

**Issue: Port 8000 already in use**
- Solution: Use `uvicorn app.main:app --reload --port 8001` to run on a different port

---

## What I Learned

This project demonstrates production-grade backend engineering through:

- **API Design**: RESTful endpoints with proper HTTP status codes and error handling
- **State Management**: State machines for complex workflows with validated transitions
- **Data Consistency**: Idempotency mechanisms to ensure safe request retries
- **Event Systems**: Asynchronous webhook delivery with automatic retries
- **Testing**: Comprehensive integration tests covering all major flows
- **Architecture**: Clean separation of concerns with layered service design
- **Database**: Schema versioning with Alembic and type-safe ORM queries
- **Security**: API key authentication with bcrypt hashing
- **Rate Limiting**: Per-merchant request throttling to prevent abuse

---

## Future Improvements

- [ ] Exponential backoff for webhook retries
- [ ] Celery integration for distributed task processing
- [ ] Enhanced monitoring and structured logging
- [ ] Multi-currency conversion with live rates
- [ ] Fraud detection pipeline
- [ ] Webhook signature verification (HMAC)
- [ ] Refund API endpoints with partial refund support
- [ ] Payment processor reconciliation
- [ ] PII encryption at rest
- [ ] Admin dashboard for monitoring transactions

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes and add tests
4. Run `pytest` to ensure tests pass
5. Commit with clear messages (`git commit -am 'Add feature'`)
6. Push to your fork (`git push origin feature/your-feature`)
7. Open a Pull Request

Please follow these guidelines:
- Write tests for new features
- Update documentation if behavior changes
- Follow existing code style and patterns
- Ensure all tests pass before submitting PR

---

## License

This project is open source and available under the MIT License.
