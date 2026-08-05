# Smart Shop Backend

Production-ready Django REST API for an automated smart shopping basket system with NFC tags, JWT authentication, real-time ESP device communication, and wallet-based checkout.

## Architecture

```
Mobile App ──JWT──▶ Django REST API ──▶ PostgreSQL
                         │
                         ├── WebSocket (Channels) ──▶ Mobile (live updates)
                         │
                         └── HTTP/WS/MQTT ──▶ ESP Device (quantity events)
```

## Features

- JWT authentication (`djangorestframework-simplejwt`)
- Custom User model with wallet balance
- NFC tag → product mapping
- Shopping session lifecycle (start → live updates → checkout)
- Real-time updates via Django Channels WebSockets
- ESP communication via HTTP API, WebSocket, and optional MQTT
- Atomic wallet deduction with duplicate payment prevention
- OpenAPI/Swagger documentation
- Docker deployment with PostgreSQL and Redis

## Project Structure

```
apps/
  users/          # User model, registration, profile
  products/       # Product catalog
  nfc/            # NFC tag management
  shopping/       # Sessions, start/checkout APIs
  transactions/   # Payment records
  esp/            # ESP device communication layer
config/           # Django settings, ASGI/WSGI, URLs
tests/            # Unit tests
```

## Quick Start

### Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
export USE_INMEMORY_CHANNEL_LAYER=True

python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

API docs: http://localhost:8000/api/docs/

### Docker

```bash
cp .env.example .env
docker compose up --build
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/token/` | Public | Obtain JWT tokens |
| POST | `/api/auth/token/refresh/` | Public | Refresh JWT token |
| POST | `/api/users/register/` | Public | Register user |
| GET | `/api/users/profile/` | JWT | User profile |
| GET | `/api/products/` | JWT | List products |
| GET | `/api/nfc/tags/` | JWT | List NFC tags |
| POST | `/api/shopping/start/` | JWT | Start shopping session |
| GET | `/api/shopping/active/` | JWT | Get active session |
| POST | `/api/shopping/checkout/` | JWT | Checkout session |
| POST | `/api/esp/events/` | ESP API Key | ESP quantity event |
| GET | `/api/transactions/` | JWT | Transaction history |

## WebSocket Endpoints

| URL | Auth | Description |
|-----|------|-------------|
| `ws/shopping/user/?token=<jwt>` | JWT query param | User-level session updates |
| `ws/shopping/session/<id>/?token=<jwt>` | JWT query param | Session-specific updates |
| `ws/esp/events/` | `X-ESP-API-Key` header | ESP device WebSocket events |

### Mobile WebSocket Example

```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/shopping/session/1/?token=${accessToken}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // { type: "session.updated", data: { session_id, product, quantity, unit_price, current_total, status } }
};
```

### ESP Event Example

```bash
curl -X POST http://localhost:8000/api/esp/events/ \
  -H "X-ESP-API-Key: change-me-esp-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "tag_uuid": "abc123-...",
    "quantity": 3,
    "timestamp": "2026-01-01T10:00:00Z"
  }'
```

## Shopping Flow

1. User scans NFC tag in mobile app
2. App sends `POST /api/shopping/start/` with `tag_uuid` and JWT
3. Backend creates session and connects ESP device
4. ESP sends quantity updates via HTTP/WebSocket/MQTT
5. Backend updates session and broadcasts to mobile via WebSocket
6. User calls `POST /api/shopping/checkout/`
7. Backend validates ESP connection, deducts wallet, creates transaction

## Running Tests

```bash
USE_INMEMORY_CHANNEL_LAYER=True pytest
```

## Environment Variables

See `.env.example` for all configuration options.

## Security

- All API endpoints require JWT except registration and token endpoints
- ESP endpoints require `X-ESP-API-Key` header
- Checkout uses `select_for_update()` for atomic wallet deduction
- Idempotency keys prevent duplicate transactions
- Session checkout locking prevents concurrent payments
- ESP disconnect detection blocks checkout when device is offline
