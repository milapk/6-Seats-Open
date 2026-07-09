# 6 Seats Open

Full-stack multiplayer poker web app (6-max No-Limit Hold'em), built as a CV/portfolio project to demonstrate full-stack + real-time systems skills.

## Tech Stack

- **Backend**: Django 5.2.4, Django REST Framework, Django Channels 4 (+ `channels_redis`, Daphne ASGI server), `djangorestframework-simplejwt`, `django-cors-headers`, `psycopg2`
- **Frontend**: React 19 (Vite), Material UI, Axios, React Router 7
- **Database**: PostgreSQL (dev/prod); SQLite in-memory when `test` is in `sys.argv`
- **Real-time transport**: Redis-backed Django Channels layer, one consumer/room per game (`poker_{game.id}`)
- **Auth**: JWT (SimpleJWT) — the WebSocket URL itself carries the access token (`ws/poker/<token>/`)

## Repo Layout

```
backend/
  core/            # settings, asgi/wsgi entrypoints, root urls
  api/              # REST app: CustomUser, Game/Player/Pot/TableType models, views, serializers, urls
    utils.py        # JWT helpers, matchmaking
    tests/          # test_seat_assignment.py, card_count.py (ad hoc, not full Django TestCase suite)
  websocket/        # Channels app: consumer, routing, game/redis async helpers
    consumers.py    # PokerGameConsumer — connect/disconnect/receive handlers
    utils/game.py   # async DB-bound helpers (get_user, start_game, get_game_info, leave_game)
    utils/redis_manager.py  # per-game channel-name <-> seat mapping in Redis
frontend/
  src/pages/        # Home, Login, Register, PokerGame, NotFound
  src/components/    # BuyInDialog, CustomAlerts, ProtectedRoute, UserForm
  src/api.js        # Axios instance (JWT header injection)
planning/           # plan.txt, poker_logic_plan.txt, assign_seats_plan.txt, wireframes
```

## Key Domain Model (`backend/api/models.py`)

- `CustomUser` — extends `AbstractUser`, holds bankroll (`chips`) and an hourly free-chip claim (`can_claim_chips` / `claim_chips`, 1hr cooldown, 500 chips).
- `TableTypeModel` — stakes definition (small/big blind, min/max buy-in). Games are matched to a `TableTypeModel` via `game_matchmaking()` in `api/utils.py`.
- `GameModel` — one poker table/hand-state machine.
  - `open_seats` is a string of digits (e.g. `"123456"`) used as a mutable set of free seats 1-6 — deliberately not a normalized table.
  - Seat assignment (`get_assigned_seat`) places new players non-randomly based on existing seating geometry (side-by-side detection, triangulation) — see `planning/assign_seats_plan.txt` for the original pseudocode/rationale before reading the implementation.
  - `_get_centric_adjusted_seats` rotates the seat list so the requesting player is always shown at seat index 1 (bottom-middle) — this is how each client gets a personalized table view from shared game state.
  - `cards` is the shuffled deck as a comma-joined string; `_deal_cards` slices 5 chars per player (note: card codes are 2 chars, e.g. `"Ac"` — check slicing math here, see checklist).
  - `start_game` posts blinds and deals, returns the seat number of the next player to act.
- `PlayerModel` — per-user, per-game state (seat, cards, `chips_in_play`, current/total bets, folded/all-in/had-acted flags). `join_game`/`leave_game` handle buy-in transfer and state reset, wrapped in `select_for_update` transactions.
- `PotModel` — supports side pots via M2M `players`, but multi-pot split-on-all-in logic is not yet wired up anywhere.

## Real-time Flow (`backend/websocket/`)

1. Client opens `ws/poker/<jwt_access_token>/`.
2. `PokerGameConsumer.connect` validates the token, finds the user's current game, joins the `poker_{game_id}` channel group, registers `channel_name` against the player's seat in Redis (`redis_manager.py`), and calls `start_game()` if this join brought the table to enough players.
3. Group events (`player_joined`, `player_left`, `player_to_act`) are broadcast to all consumers in the room; each consumer resolves a **personalized** payload via `get_game_info(self.user)` before sending to its own client.
4. `receive()` currently just parses incoming JSON and does nothing with it — **no action dispatch yet** (fold/call/raise are frontend-only stubs, see checklist).

See `planning/poker_logic_plan.txt` for the intended full hand lifecycle (blinds → deal → betting rounds → showdown → next hand) and the anytime-events list (timeout, leave, illegal move, sync) — useful context for what `receive()` is meant to grow into.

## Frontend Notes

- `frontend/src/pages/PokerGame.jsx` renders the table from `gameState`, wires Fold/Call/Raise buttons to `handleAction`, which sends `{event: "player_action", action, amount}` over the socket — but since the backend doesn't consume these yet, they're currently no-ops server-side.
- Hole cards, pot amount, and "active" player highlighting are still hardcoded/demo values (`demoHoleCards`, `pot: 20 //not done`) pending real WS events.
- Auth uses JWT stored in `localStorage` (`ACCESS_TOKEN` from `constants.js`), injected by `src/api.js` via Axios interceptor; `ProtectedRoute.jsx` gates authenticated pages.

## Conventions Observed

- Model methods that touch balances/seats wrap reads+writes in `transaction.atomic()` with `select_for_update()` — follow this pattern for any new money- or seat-mutating logic to avoid race conditions between concurrent players.
- Docstrings on model/util methods use a `Return:` (and occasionally `Arguments:`) convention — match this style when adding methods rather than switching to a different docstring format.
- Business logic lives on model methods (fat models), not in views/consumers — views and consumers stay thin and delegate.
- No `requirements.txt` currently checked in; installed backend packages (from the active venv) include `Django==5.2.4`, `djangorestframework==3.16.0`, `channels==4.3.1`, `channels_redis==4.3.0`, `djangorestframework_simplejwt==5.5.1`, `django-cors-headers==4.7.0`, `psycopg2==2.9.10`, `redis==6.4.0`.

## Commands

```bash
# Backend (from backend/)
python manage.py runserver          # NOTE: for Channels you likely want daphne core.asgi:application
python manage.py test               # runs against in-memory sqlite (see settings.py)
python manage.py makemigrations && python manage.py migrate

# Frontend (from frontend/)
npm run dev
npm run lint
npm run build
```
