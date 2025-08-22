import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Slider,
} from "@mui/material";
import { useState } from "react";
import "../styles/BuyInDialog.css";
import api from "../api.js";
import { useNavigate } from "react-router-dom";
import AutoCloseAlert from "./CustomAlerts.jsx";

export default function BuyInDialog({
    open,
    onClose,
    minBuyIn,
    maxBuyIn,
    smallBlind,
    bigBlind,
}) {
    const [buyIn, setBuyIn] = useState(0);
    const [alertMessage, setAlertMessage] = useState('');
    const navigate = useNavigate();

    const handleJoinGame = async (e) => {
        try {
            const response = await api.post("/api/join-game/", {
                big_blind: bigBlind,
                small_blind: smallBlind,
                buy_in: buyIn,
            });

            if (response.status === 200) {
                console.log(response.data.success);
                navigate("/game");
            }
        } catch (error) {
            if (error.response){
                setAlertMessage(error.response.data.error);
            } else {
                setAlertMessage("Could not join a game. Please refresh or try again later!");
            }
        }
    };

    return (
        <Dialog open={open} onClose={onClose}>
            <AutoCloseAlert
                message={alertMessage}
                severity="error"
                duration={3000}
                onClose={() => setAlertMessage("")}
            />
            <DialogTitle id="dialog-title">Enter Buy-In</DialogTitle>
            <DialogContent>
                <div id="dialog-content">
                    <div id="dialog-items">Select amount: £{buyIn}</div>
                    <Slider
                        id="dialog-items"
                        value={buyIn}
                        onChange={(e, newValue) => setBuyIn(newValue)}
                        color="primary"
                        size="small"
                        min={minBuyIn}
                        max={maxBuyIn}
                        step={10}
                    ></Slider>
                    <TextField
                        fullWidth
                        id="dialog-items"
                        label="Or enter exact amount"
                        type="number"
                        value={buyIn}
                        variant="filled"
                        size="small"
                        onChange={(e) => setBuyIn(e.target.value)}
                    ></TextField>
                </div>
            </DialogContent>
            <DialogActions>
                <Button variant="contained" color="secondary" onClick={onClose}>
                    Cancel
                </Button>
                <Button
                    onClick={handleJoinGame}
                    className="button"
                    variant="contained"
                    color="secondary"
                >
                    Join Game
                </Button>
            </DialogActions>
        </Dialog>
    );
}
