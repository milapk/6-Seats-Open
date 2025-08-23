# ♠ 6 Seats Open ♠
> ⚠ **Note**  
> - This project is **under active development**.  
> - Most core features are not yet implemented.  
> - Will only be optimised for **desktop browsers**.
> - Once the MVP is complete, the app will be deployed and automatically updated via CI/CD pipelines, ensuring continuous delivery of new features and fixes.

6 Seats Open is a full-stack multiplayer poker platform built with **React** and **Django** with Channel and Reddis to handle concurrency, synchronisation and game state. 

Each poker game will run within a dedicated Channels consumer that coordinates player actions and broadcasts updates to all connected clients in that game room.


## Current Features

- **Authentication**: Login, Register, JWT-based authentication.
- **Lobby/Home**: Browse and join public tables.
- **Poker Gameplay**: Initial game set-up (WIP)

*This list may not be up-to-date. Last updated at: 23rd August 25

## Planned Features 📌

- **Lobby/Home**: Create and Join private tables.
- **Poker Gameplay**: Real-time gameplay, betting logic, chip management and everything else.
- **Game History**: Player stats, match history, leaderboards via a profile page.

## Tech Stack

**Frontend**
- React
- Material UI (for styling)
- WebSocket (for real-time gameplay)
- Axios (for APIs)

**Backend**
- Django + Django REST Framework
- PostgreSQL
- Django Channels + Redis (for WebSocket support)
