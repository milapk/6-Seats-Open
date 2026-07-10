# ♠ 6 Seats Open

A 6-max No-Limit Hold'em poker game, built from scratch; no poker SDK, no game-engine library. Django Channels handles the real-time table state over WebSockets, React renders it.

This is a portfolio project, not a finished product. It's currently under  development.

## Why this project exists

I wanted something that would force me to deal with and solve more complex problems instead of another CRUD app: concurrent writes to shared game state, keeping multiple clients in sync over WebSockets, and dealing with timeouts and other more complex designs. Poker turns out to be a good game for this.

## What's actually working

- **Auth**: register/login with JWT (SimpleJWT). The access token gets reused as the WebSocket auth mechanism, it's passed straight in the socket URL (`ws/poker/<token>/`) since browsers don't let you set auth headers on a WebSocket handshake.
- **Matchmaking & seating**: joining a table type finds/creates a game and assigns you a seat using actual table geometry . `GameModel.get_assigned_seat` looks at who's already seated and tries to avoid clustering players together.
- **Per-player table view**: every client sees themselves at the same seat position (bottom-middle) regardless of their real seat number. The backend rotates the seat list per-request (`_get_centric_adjusted_seats`) so there's one shared game state but a personalized view for each player.
- **Live table updates**: Django Channels broadcasts `player_joined` / `player_left` / `player_to_act` events to everyone in the room.
- **Atomic transactions**: anything that touches chip balances or seat state is wrapped in `transaction.atomic()` + `select_for_update()`, so two players can't race into the same seat or double-spend a buy-in.
- **Docker Compose for local dev and future deployment**: `db`, `redis`, and `backend` come up together with one command with healthchecks.
- **CI on GitHub Actions**: every push/PR to `main` spins up Postgres/Redis, runs `flake8`, and runs the tests.

## Coming up soon

- **Betting logic.** The consumer's `receive()` currently parses the incoming JSON and throws it away. Fold/Call/Raise buttons exist in the UI and fire the right socket events, but the server doesn't act on them yet.
- Hole cards, pot size, and "active player" highlighting in the UI are hardcoded demo values until the above lands.
- Community cards, showdown, side-pot resolution
- Django test; currently only seat assignment tests to set up CI.


## Tech stack

**Backend** — Django 5.2, Django REST Framework, Django Channels 4, Daphne as the ASGI server, SimpleJWT, PostgreSQL.

**Frontend** — React 19 (Vite), Material UI, Axios, React Router 7.

**Infra** — Docker Compose (`db` / `redis` / `backend`), CI/CD via GitHub Actions

## Running it locally

```bash
# 1. copy env files and fill in real values
cp .env.example .env
cp backend/.env.example backend/.env
```

```bash
# 2. backend + db + redis
docker compose up --build
```

```bash
# 3. frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Backend serves on `localhost:8000` (via Daphne, so Channels/WebSockets work), frontend on `localhost:5173`.

Without Docker: setup up Postgres and Redis yourself, `pip install -r backend/requirements.txt`, then in `backend/`: `python manage.py migrate` and `daphne -b 0.0.0.0 -p 8000 core.asgi:application` .

## Codebase layout

```
backend/
  core/-------------settings, ASGI/WSGI entrypoints, root urls
  api/--------------REST app — users, games, table types, matchmaking, seat assignment
  websocket/--------Channels app — the per-game consumer, Redis-backed seat<->socket mapping

frontend/
  src/pages/--------Home, Login, Register, PokerGame, NotFound
  src/components/---BuyInDialog, ProtectedRoute, alerts, form helpers

planning/-----------design docs written before implementation (seat assignment, hand lifecycle)
```
