import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Slider,
    Typography,
    SvgIcon,
} from "@mui/material";
import { useState } from "react";
import '../styles/BuyInDialog.css'
import api from '../api.js'

export default function BuyInDialog({
    open,
    onClose,
    minBuyIn,
    maxBuyIn,
    smallBlind,
    bigBlind,
}) {
    const [buyIn, setBuyIn] = useState(0);

    const handleJoinGame = async (e) => {
        const response = await api.post("/api/join-game/", {
            big_blind: bigBlind,
            small_blind: smallBlind,
            buy_in: buyIn,
        });

        if (response.status === 200) {
            console.log(response.data.success);
        }
    };

    return (
        <Dialog open={open} onClose={onClose}>
            <DialogTitle id='dialog-title'>Enter Buy-In</DialogTitle>
            <DialogContent>
                <div id="dialog-content">
                    <div id="dialog-items">Select amount: £{buyIn}</div>
                    <Slider
                        id='dialog-items'
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
                        onChange={(e) =>
                            setBuyIn(e.target.value)
                        }
                    ></TextField>
                </div>
            </DialogContent>
            <DialogActions>
                <Button variant="contained" color="secondary" onClick={onClose}>Cancel</Button>
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
