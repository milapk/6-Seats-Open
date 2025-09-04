# ♠ 6 Seats Open ♠
> ⚠ **Note**  
> - This project is **under development**.  
> - Planned deployment with CI/CD pipelines, ensuring continuous delivery of new features and fixes.

6 Seats Open is a full-stack multiplayer poker platform built with **React** and **Django**.

Each poker game runs within a dedicated Django Channels consumer that coordinates player actions and broadcasts updates to all connected clients in that game room.


## Current Features

- **Authentication**: Login, Register, JWT-based authentication.
- **Lobby/Home**: Browse and join public tables.
- **Poker Gameplay**: Initial game set-up

**Currently working on:**
-  THE ACTUAL GAME(Real-time gameplay, betting logic, chip management and everything else)

***This list may not be up-to-date. Last updated at: 4/9/25**

## Planned Features 📌

- **Lobby/Home**: Create and Join private tables.
- **Game History**: Player stats, match history, leaderboards via a profile page.
- **AI Bot**: For 1v1??? 

## Tech Stack

**Frontend**
- React
- Material UI (for styling)
- Axios (for APIs)

**Backend**
- Django
- Django REST Framework (for APIs)
- Django Channels + Redis (for WebSocket)
- PostgreSQL
