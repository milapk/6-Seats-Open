# 6 Seats Open — Build Checklist

Status snapshot based on current code (not just `planning/plan.txt`, which is stale in places). Grouped by what's blocking a playable end-to-end hand, then polish/deploy items for the CV story.

## 🔴 Core gameplay — biggest gap, do these next

- [ ] **Dispatch player actions in the consumer.** `PokerGameConsumer.receive()` (`backend/websocket/consumers.py:31`) parses incoming JSON but does nothing with it. Frontend already sends `{event: "player_action", action, amount}` — need to route fold/check/call/bet/raise to model logic.
- [ ] **Betting round engine.** Nothing currently: validates legal actions (min-raise, can't bet more than `chips_in_play`), advances `current_turn`/`had_acted`, detects when a betting round is complete (all active players acted and bets equal, or everyone all-in/folded).
- [ ] **Street progression.** Auto-advance `betting_stage` (Pre-flop → Flop → Turn → River → Showdown) once a betting round closes; deal community cards at each street.
- [ ] **Showdown / hand evaluation.** No poker hand-ranking code exists yet (best 5-of-7, tiebreakers, split pots).
- [ ] **Pot distribution.** `PotModel` supports side pots via the `players` M2M, but nothing creates side pots on all-ins or pays out winners at showdown.
- [ ] **Next-hand reset.** After showdown: rotate dealer button, reset `is_folded`/`all_in`/`had_acted`/bets, re-deal, remove players with 0 chips (or prompt rebuy).
- [ ] **Turn timeouts.** `poker_logic_plan.txt` calls for a 1-minute action clock with auto-fold/check on timeout and disconnect handling — no timer mechanism (Channels' `asyncio` or Celery-beat/Redis TTL) implemented.
- [ ] **`send_cards` consumer handler** (`consumers.py:52`) sends an empty payload — hole cards are never actually delivered to the client over WS yet.
- [ ] **Illegal action handling.** No validation path for out-of-turn actions or invalid amounts — currently anything sent to `receive()` is silently dropped.

## 🟡 Frontend wiring for the above

- [ ] Replace `demoHoleCards` in `PokerGame.jsx` with real cards pushed via a WS event (depends on `send_cards` above).
- [ ] Replace hardcoded `pot: 20 //not done` with real pot value from game state.
- [ ] Highlight the active-to-act player (`active: false` is hardcoded on every seat currently).
- [ ] Render community cards (flop/turn/river) — no UI element for this yet in `PokerGame.jsx`.
- [ ] Show betting stage / round in the UI (currently only stakes + player count are shown).
- [ ] Handle WS reconnect/error states (e.g., token expiry mid-game, server restart) — `onclose`/`onerror` are just `console.log`s today.
- [ ] Disable action buttons when it isn't the user's turn (buttons are always clickable right now).

## 🟢 Already working (per `plan.txt` + code read)

- [x] JWT auth: register/login, `ProtectedRoute`, Axios token injection.
- [x] Home/lobby page listing table stakes + occupancy (`HomePageDataView`).
- [x] Join/leave game REST endpoints with buy-in validation.
- [x] Matchmaking (`game_matchmaking()` in `api/utils.py`) seats players into existing open games before creating new ones.
- [x] Deterministic, "realistic" seat assignment algorithm (side-by-side/triangulation logic) with a dedicated test (`api/tests/test_seat_assignment.py`).
- [x] Centric seat rotation so each client sees themselves bottom-middle.
- [x] Blinds posting + hole card dealing on game start (`GameModel.start_game`).
- [x] WS room join/leave broadcasting with per-client personalized `game_info`.
- [x] Hourly free-chip claim system with cooldown.

## ⚪ Testing & quality

- [ ] Real Django `TestCase`/`ChannelsLiveServerTestCase` coverage for: betting logic, showdown, WS consumer flows. Current tests (`test_seat_assignment.py`, `card_count.py`) only cover seat assignment and a card-count sanity check.
- [ ] `websocket/tests.py` is an empty stub — no consumer tests at all.
- [ ] Concurrency/race-condition tests for simultaneous actions from two players (the whole point of `select_for_update` — worth demonstrating you tested it).
- [ ] Frontend tests (none currently — no test runner configured in `package.json`).
- [ ] Add `requirements.txt` (or switch to `pyproject.toml`/Poetry) — currently no dependency manifest is checked into `backend/`, so the project isn't pip-installable from a fresh clone.

## ⚪ Security / config hardening (matters for a CV project people will actually clone/run)

- [ ] `backend/core/settings.py` hardcodes the Postgres password (`MKrandom1`) and DB name/user directly in `DATABASES` instead of reading from `.env` like `SECRET_KEY`/`REDIS_URL` do — move these to env vars.
- [ ] `DEBUG = os.environ.get('DJANGO_DEBUG', 'False')` — this is always truthy (non-empty string), even when set to the string `"False"`. Needs explicit string comparison or `python-decouple`/`django-environ` casting.
- [ ] Confirm `.env` files are gitignored (both `backend/.env` and `frontend/.env` exist locally) and that `db.sqlite3` isn't meant to be tracked.
- [ ] Add rate limiting to `ClaimChipsView`/`JoinGameView`/auth endpoints (DRF throttling) before deploying publicly.
- [ ] CORS is currently single-origin from an env var — fine for now, just confirm it's tightened for prod domain before deploy.

## ⚪ Deploy & CI/CD (explicitly called out in your README as "planned")

- [ ] Dockerize backend (Daphne/ASGI) + frontend build + Postgres + Redis (docker-compose for local parity with prod).
- [ ] Pick and configure a host (Render/Railway/Fly.io — README mentions Render/Heroku) for both the ASGI app and a managed Postgres + Redis.
- [ ] CI pipeline (GitHub Actions): run backend tests + frontend lint/build on PRs.
- [ ] CD: auto-deploy on merge to `main`.
- [ ] Production static file serving for the Vite build (currently `frontend/dist` exists but nothing serves it in prod config).

## ⚪ Nice-to-haves / stretch (from README "Planned Features")

- [ ] Private tables with join codes (`GameModel.code` field already exists but is unused).
- [ ] Game history / player stats / leaderboard page.
- [ ] AI bot opponent for 1v1 play.
- [ ] Spectator mode.

---
**Suggested order of attack:** finish the betting engine + action dispatch (🔴) since everything else — frontend wiring, tests, even the "is this actually a poker game" pitch on your CV — depends on a hand being playable start to finish. Security/deploy items are cheap wins to do in parallel once gameplay is solid.
