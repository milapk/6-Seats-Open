import "../styles/PokerGame.css";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
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
        stakes: { small: 0, big: 0 },
        num_of_players: 0,
        players: []
    });

    useEffect(() => {
        const access = localStorage.getItem(ACCESS_TOKEN);
        const socket = new WebSocket(`${import.meta.env.VITE_WS_URL}/ws/poker/${access}/`);

        socketRef.current = socket;

        socket.onopen = () => {
            console.log("WebSocket connection established");
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.event === 'game_joined') {
                updateGameState(data);
            }
            
            if (data.event === 'player_joined') {
                updateGameState(data);
            }
        };

        socket.onclose = () => {
            console.log("WebSocket connection closed");
        };

        return () => {
            if (socketRef.current) {
                socketRef.current.close();
            }
        };
    }, []);

    const updateGameState = (gameData) => {
        const transformedPlayers = [];
        
        for (let position = 1; position <= 6; position++) {
            const seatData = gameData.data.seats[position];
            
            if (seatData) {
                transformedPlayers.push({
                    position: position,
                    username: seatData.username,
                    chips: seatData.chips,
                    playerId: seatData.id,
                    actualSeat: seatData.actual_seat,
                    active: false
                });
            }
        }
        setGameState({
            stakes: {
                small: gameData.small_blind,
                big: gameData.big_blind
            },
            num_of_players: gameData.num_of_players,
            players: transformedPlayers
        });
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
                    "Could not leave a game. Please refresh or try again later!"
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
                        <div key={player.playerId} className={`seat seat-${player.position}`}>
                            <div className={`player-circle ${player.active ? "active" : ""}`}></div>
                            <div id="player-name">{player.username}</div>
                            <div id="player-chips">${player.chips}</div>
                        </div>
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
