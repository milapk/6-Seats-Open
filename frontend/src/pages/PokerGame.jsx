import "../styles/PokerGame.css";
import { ACCESS_TOKEN } from "../constants";
import { Button, IconButton, Slider, Box } from "@mui/material";
import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import AutoCloseAlert from "../components/CustomAlerts";
import api from "../api";
import MenuIcon from "@mui/icons-material/Menu";
import CloseIcon from "@mui/icons-material/Close";
import ExitToAppIcon from "@mui/icons-material/ExitToApp";

export default function PokerGame() {
    const [alertMessage, setAlertMessage] = useState("");
    const navigate = useNavigate();
    const socketRef = useRef(null);
    const [gameState, setGameState] = useState({
        pot: 0,
        stakes: { small: 0, big: 0 },
        num_of_players: 0,
        mainUser: { maxBet: 0 },
        players: [],
    });
    const [betAmount, setBetAmount] = useState(0);
    const [maxBet, setMaxBet] = useState(0);
    const [showSidebar, setShowSidebar] = useState(true);
    const [windowSize, setWindowSize] = useState({
        width: window.innerWidth,
        height: window.innerHeight,
    });

    useEffect(() => {
        const access = localStorage.getItem(ACCESS_TOKEN);
        const socket = new WebSocket(
            `${import.meta.env.VITE_WS_URL}/ws/poker/${access}/`
        );

        socketRef.current = socket;

        socket.onopen = () => {
            console.log("WebSocket connection established");
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.event === "game_joined") {
                updateGameState(data);
            }

            if (data.event === "player_joined") {
                updateGameState(data);
            }
        };

        socket.onclose = () => {
            console.log("WebSocket connection closed");
        };

        const handleResize = () => {
            setWindowSize({
                width: window.innerWidth,
                height: window.innerHeight,
            });
        };

        window.addEventListener("resize", handleResize);
        handleResize();

        return () => {
            if (socketRef.current) {
                socketRef.current.close();
            }
            window.removeEventListener("resize", handleResize);
        };
    }, []);

    const updateGameState = (gameData) => {
        gameData = gameData.data;
        const transformedPlayers = [];
        let mainUser = null;

        for (let position = 1; position <= 6; position++) {
            const seatData = gameData.seats[position];

            if (seatData) {
                if (position === 1) {
                    mainUser = seatData;
                    console.log(mainUser);
                }
                transformedPlayers.push({
                    position: position,
                    username: seatData.username,
                    chips: seatData.chips,
                    playerId: seatData.id,
                    actualSeat: seatData.actual_seat,
                    active: false,
                });
            }
        }
        setGameState({
            pot: 20, //not done
            stakes: {
                small: gameData.small_blind,
                big: gameData.big_blind,
            },
            num_of_players: gameData.num_of_players,
            mainUser: { maxBet: mainUser.chips },
            players: transformedPlayers,
        });
        setMaxBet(mainUser.chips);

        console.log("Game state updated:", {
            stakes: { small: gameData.small_blind, big: gameData.big_blind },
            numPlayers: gameData.num_of_players,
            mainUser: { maxBet: mainUser.chips },
            players: transformedPlayers,
        });
    };

    const handleAction = (action, amount = null) => {
        if (
            socketRef.current &&
            socketRef.current.readyState === WebSocket.OPEN
        ) {
            socketRef.current.send(
                JSON.stringify({
                    event: "player_action",
                    action: action,
                    amount: amount || betAmount,
                })
            );
        }
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

    const isMobile = windowSize.width < 850 || windowSize.height < 500;
    const showCompactUI = isMobile;

    return (
        <div id="game-root">
            <AutoCloseAlert
                message={alertMessage}
                severity="error"
                duration={3000}
                onClose={() => setAlertMessage("")}
            />

            <div id="game-container">
                <div id="game-header">
                    <div className="table-info">
                        6 Max | Stakes: {gameState.stakes.small}/
                        {gameState.stakes.big} | {gameState.num_of_players}/6
                    </div>
                    <div id="game-leave-div">
                        <IconButton
                            className="game-leave-button"
                            onClick={handleLeaveGame}
                        >
                            <ExitToAppIcon></ExitToAppIcon>
                        </IconButton>
                    </div>

                    {showCompactUI && (
                        <IconButton
                            className="mobile-menu-button"
                            onClick={() => setShowSidebar(!showSidebar)}
                        >
                            {showSidebar ? <CloseIcon /> : <MenuIcon />}
                        </IconButton>
                    )}
                </div>

                <div id="game-poker-table">
                    {gameState.players.map((player) => (
                        <div
                            key={player.playerId}
                            className={`seat seat-${player.position}`}
                        >
                            <div
                                className={`player-circle ${
                                    player.active ? "active" : ""
                                }`}
                            ></div>
                            <div id="player-name">{player.username}</div>
                            <div id="player-chips">${player.chips}</div>
                        </div>
                    ))}
                </div>
                {!showCompactUI && (
                    <div id="game-controls">
                        <div className="bet-controls">
                            <div className="bet-slider-container">
                                <Box
                                    sx={{
                                        width: "100%",
                                        maxWidth: 300,
                                        margin: "0 auto",
                                    }}
                                >
                                    <Slider
                                        value={betAmount}
                                        onChange={(e, newValue) =>
                                            setBetAmount(newValue)
                                        }
                                        min={gameState.stakes.big}
                                        max={maxBet}
                                        step={gameState.stakes.big}
                                        valueLabelDisplay="auto"
                                        valueLabelFormat={(value) =>
                                            `£${value}`
                                        }
                                    />
                                </Box>
                                <div className="bet-amount-display">
                                    Bet: £{betAmount}
                                </div>
                            </div>

                            <div className="quick-bet-buttons">
                                <Button
                                    className="quick-bet-btn"
                                    variant="outlined"
                                    size="small"
                                    onClick={() =>
                                        setBetAmount(gameState.stakes.big * 2)
                                    }
                                >
                                    2x BB
                                </Button>
                                <Button
                                    className="quick-bet-btn"
                                    variant="outlined"
                                    size="small"
                                    onClick={() =>
                                        setBetAmount(gameState.stakes.big * 3)
                                    }
                                >
                                    3x BB
                                </Button>
                                <Button
                                    className="quick-bet-btn"
                                    variant="outlined"
                                    size="small"
                                    onClick={() =>
                                        setBetAmount(
                                            Math.floor(gameState.pot / 2)
                                        )
                                    }
                                >
                                    ½ Pot
                                </Button>
                                <Button
                                    className="quick-bet-btn"
                                    variant="outlined"
                                    size="small"
                                    onClick={() => setBetAmount(maxBet)}
                                >
                                    Max
                                </Button>
                            </div>
                        </div>

                        <div className="control-status">
                            Current action:{" "}
                            <span className="current-action">Your turn</span>
                        </div>

                        <div id="game-buttons">
                            <Button
                                className="action-btn fold-btn"
                                variant="contained"
                                onClick={() => handleAction("fold")}
                            >
                                Fold
                            </Button>
                            <Button
                                className="action-btn call-btn"
                                variant="contained"
                                onClick={() => handleAction("call")}
                            >
                                Call
                            </Button>
                            <Button
                                className="action-btn raise-btn"
                                variant="contained"
                                onClick={() => handleAction("raise")}
                            >
                                Raise
                            </Button>
                        </div>
                    </div>
                )}
                {showCompactUI && showSidebar && (
                    <div id="mobile-sidebar">
                        <IconButton
                            className="mobile-close-btn"
                            onClick={() => setShowSidebar(false)}
                            size="small"
                        >
                            <CloseIcon fontSize="small" />
                        </IconButton>

                        <div className="sidebar-content">
                            {/* Status Indicator */}
                            <div className="mobile-status">
                                Your turn •{" "}
                                <span className="mobile-current-action">
                                    Action required
                                </span>
                            </div>

                            <div className="bet-controls">
                                <Box
                                    sx={{
                                        width: "100%",
                                        maxWidth: 300,
                                        margin: "0 auto",
                                    }}
                                >
                                    <Slider
                                        value={betAmount}
                                        onChange={(e, newValue) =>
                                            setBetAmount(newValue)
                                        }
                                        min={gameState.stakes.big}
                                        max={maxBet}
                                        step={gameState.stakes.big}
                                        valueLabelDisplay="auto"
                                        valueLabelFormat={(value) =>
                                            `£${value}`
                                        }
                                    />
                                </Box>
                                <div className="bet-amount">
                                    Bet: £{betAmount}
                                </div>

                                {/* Quick Bet Buttons */}
                                <div className="mobile-quick-bets">
                                    <Button
                                        className="mobile-quick-bet-btn"
                                        variant="outlined"
                                        size="small"
                                        onClick={() =>
                                            setBetAmount(
                                                gameState.stakes.big * 2
                                            )
                                        }
                                    >
                                        2x BB
                                    </Button>
                                    <Button
                                        className="mobile-quick-bet-btn"
                                        variant="outlined"
                                        size="small"
                                        onClick={() =>
                                            setBetAmount(
                                                gameState.stakes.big * 3
                                            )
                                        }
                                    >
                                        3x BB
                                    </Button>
                                    <Button
                                        className="mobile-quick-bet-btn"
                                        variant="outlined"
                                        size="small"
                                        onClick={() =>
                                            setBetAmount(
                                                Math.floor(gameState.pot / 2)
                                            )
                                        }
                                    >
                                        ½ Pot
                                    </Button>
                                    <Button
                                        className="mobile-quick-bet-btn"
                                        variant="outlined"
                                        size="small"
                                        onClick={() => setBetAmount(maxBet)}
                                    >
                                        Max
                                    </Button>
                                </div>
                            </div>

                            <div className="action-buttons-mobile">
                                <Button
                                    className="action-btn fold-btn"
                                    variant="contained"
                                    onClick={() => handleAction("fold")}
                                >
                                    Fold
                                </Button>
                                <Button
                                    className="action-btn call-btn"
                                    variant="contained"
                                    onClick={() => handleAction("call")}
                                >
                                    Call
                                </Button>
                                <Button
                                    className="action-btn raise-btn"
                                    variant="contained"
                                    onClick={() => handleAction("raise")}
                                >
                                    Raise
                                </Button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
