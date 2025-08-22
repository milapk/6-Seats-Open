import "../styles/PokerGame.css";
import { Button } from "@mui/material";
import { useState } from "react";

export default function PokerGame() {
    const [gameState, setGameState] = useState({
        stakes: { small: 1, big: 2 },
        players: [
            { id: 1, chips: 250000, active: true },
            { id: 2, chips: 250, active: false },
            { id: 3, chips: 250, active: false },
            { id: 4, chips: 2500, active: false },
            { id: 5, chips: 250, active: false },
            { id: 6, chips: 250, active: false },
        ],
    });

    const PlayerSeat = ({ position, chips, isActive }) => {
        return (
            <div
                className={`seat seat-${position}`}
            >   
                <div className={`player-circle ${isActive ? "active" : ""}`}></div>
                <div id="player-name">Player {position}</div>
                <div id="player-chips">{chips}</div>
            </div>
        );
    };

    return (
        <div id="game-root">
            <div id="game-container">
                <div id="game-leave-button">
                    <Button variant="contained" color="secondary">
                        Leave
                    </Button>
                </div>
                <div id="game-poker-table">
                    {gameState.players.map((player) => (
                        <PlayerSeat
                            key={player.id}
                            position={player.id}
                            chips={player.chips}
                            isActive={player.active}
                        />
                    ))}
                </div>
                <div id="game-buttons">
                    <Button className="action-btn fold-btn" variant="contained">
                        Fold
                    </Button>
                    <Button className="action-btn call-btn" variant="contained">
                        Call/Check
                    </Button>
                    <Button className="action-btn raise-btn" variant="contained">
                        Bet/Raise
                    </Button>
                </div>
            </div>
        </div>
    );
}
