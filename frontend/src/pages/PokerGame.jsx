import "../styles/PokerGame.css";
import { Button } from "@mui/material";
import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import AutoCloseAlert from "../components/CustomAlerts";
import api from "../api";

export default function PokerGame() {
    const [alertMessage, setAlertMessage] = useState("");
    const navigate = useNavigate();
    const socketRef = useRef(null);
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

    useEffect(() => {
        const socket = new WebSocket('ws://localhost:8000/ws/poker/')

        socket.onopen = () => {
            console.log('WebSocket connection established');
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received message:', data);
        };
         
        socket.onclose = () => {
            console.log('WebSocket connection closed');
        };

        socketRef.current = socket;

        return () => {
            if (socketRef.current) {
                socketRef.current.close();
            }
          };
    }, [])

    const PlayerSeat = ({ position, chips, isActive }) => {
        return (
            <div className={`seat seat-${position}`}>
                <div
                    className={`player-circle ${isActive ? "active" : ""}`}
                ></div>
                <div id="player-name">Player {position}</div>
                <div id="player-chips">{chips}</div>
            </div>
        );
    };

    const handleLeaveGame = async (e) => {
        try {
            const response = await api.post("/api/leave-game/");
            navigate("/");
        } catch (error) {
            if (error.response) {
                setAlertMessage(error.response.data.error);
            } else {
                setAlertMessage(
                    "Could not join a game. Please refresh or try again later!"
                );
            }
            navigate("/");
        }
    };

    return (
        <div id="game-root">
            <AutoCloseAlert
                message={alertMessage}
                severity="error"
                duration={3000}
                onClose={() => setAlertMessage("")}
            />
            <div id="game-container">
                <div id="game-leave-button">
                    <Button
                        variant="contained"
                        color="secondary"
                        onClick={handleLeaveGame}
                    >
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
                    <Button
                        className="action-btn raise-btn"
                        variant="contained"
                    >
                        Bet/Raise
                    </Button>
                </div>
            </div>
        </div>
    );
}
