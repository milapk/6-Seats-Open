import "../styles/PokerGame.css";
import { ACCESS_TOKEN } from "../constants";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import AutoCloseAlert from "../components/CustomAlerts";
import api from "../api";
import { Menu, X, LogOut } from "lucide-react";
import aceOfClubs from "../assets/cards/Ac.svg";
import twoOfDiamonds from "../assets/cards/2d.svg";

const demoHoleCards = [
    { src: aceOfClubs, alt: "Ace of clubs" },
    { src: twoOfDiamonds, alt: "Two of diamonds" },
];

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
        communityCards: []
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
                console.log(data);
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
        <div id="poker-root">
            <AutoCloseAlert
                message={alertMessage}
                severity="error"
                duration={3000}
                onClose={() => setAlertMessage("")}
            />

            <div className="poker-container">
                <div className="poker-header">
                    <div className="poker-stakes-badge">
                        6 Max | Stakes: {gameState.stakes.small}/
                        {gameState.stakes.big} | {gameState.num_of_players}/6
                    </div>
                    <div className="poker-leave-button-wrapper">
                        <Button
                            variant="icon"
                            size="icon"
                            className="poker-leave-button"
                            onClick={handleLeaveGame}
                        >
                            <LogOut size={18} />
                        </Button>
                    </div>

                    {showCompactUI && (
                        <Button
                            variant="icon"
                            size="icon"
                            className="poker-mobile-menu-button"
                            onClick={() => setShowSidebar(!showSidebar)}
                        >
                            {showSidebar ? <X size={18} /> : <Menu size={18} />}
                        </Button>
                    )}
                </div>

                <div className="poker-table">
                    {gameState.players.map((player) => (
                        <div
                            key={player.playerId}
                            className={`poker-seat poker-seat-${player.position}`}
                        >
                            <div
                                className={`poker-player-avatar ${
                                    player.active ? "active" : ""
                                }`}
                            ></div>
                            <div className="poker-player-info">
                                <div className="poker-player-name">
                                    {player.username}
                                </div>
                                <div className="poker-player-chips">
                                    ${player.chips}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
                {!showCompactUI && (
                    <div className="poker-action-area">
                        <div
                            className="poker-hole-cards"
                            aria-label="Your hole cards"
                        >
                            {demoHoleCards.map((card) => (
                                <img
                                    key={card.alt}
                                    className="poker-hole-card"
                                    src={card.src}
                                    alt={card.alt}
                                />
                            ))}
                        </div>

                        <div className="poker-controls">
                        <div className="poker-bet-controls">
                                    <Slider
                                        value={[betAmount]}
                                        onValueChange={([newValue]) =>
                                            setBetAmount(newValue)
                                        }
                                        min={gameState.stakes.big}
                                        max={maxBet}
                                        step={gameState.stakes.big}
                                    />


                            <div className="poker-quick-bet-buttons">
                                <Button
                                    className="poker-quick-bet-button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() =>
                                        setBetAmount(gameState.stakes.big * 2)
                                    }
                                >
                                    2x BB
                                </Button>
                                <Button
                                    className="poker-quick-bet-button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() =>
                                        setBetAmount(gameState.stakes.big * 3)
                                    }
                                >
                                    3x BB
                                </Button>
                                <Button
                                    className="poker-quick-bet-button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() =>
                                        setBetAmount(
                                            Math.floor(gameState.pot / 2)
                                        )
                                    }
                                >
                                    ½ Pot
                                </Button>
                                <Button
                                    className="poker-quick-bet-button"
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setBetAmount(maxBet)}
                                >
                                    Max
                                </Button>
                                <div className="poker-bet-amount">
                                    Bet: £{betAmount}
                                </div>
                            </div>
                        </div>

                        <div className="poker-control-status">
                            Current action:{" "}
                            <span className="poker-current-action">
                                Your turn
                            </span>
                        </div>

                        <div className="poker-action-buttons">
                            <Button
                                className="poker-action-button poker-fold-button"
                                size="sm"
                                onClick={() => handleAction("fold")}
                            >
                                Fold
                            </Button>
                            <Button
                                className="poker-action-button poker-call-button"
                                size="sm"
                                onClick={() => handleAction("call")}
                            >
                                Call
                            </Button>
                            <Button
                                className="poker-action-button poker-raise-button"
                                size="sm"
                                onClick={() => handleAction("raise")}
                            >
                                Raise
                            </Button>
                        </div>
                        </div>
                    </div>
                )}
                {showCompactUI && showSidebar && (
                    <div></div>
                )}
            </div>
        </div>
    );
}
