import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogFooter,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import api from "../api.js";
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
    const [alertMessage, setAlertMessage] = useState("");
    const navigate = useNavigate();

    const handleJoinGame = async () => {
        try {
            const response = await api.post("/api/join-game/", {
                big_blind: bigBlind,
                small_blind: smallBlind,
                buy_in: buyIn,
            });

            if (response.status === 200) {
                navigate("/game");
            }
        } catch (error) {
            if (error.response) {
                setAlertMessage(error.response.data.error);
            } else {
                setAlertMessage(
                    "Could not join a game. Please refresh or try again later!"
                );
            }
        }
    };

    return (
        <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
            <AutoCloseAlert
                message={alertMessage}
                severity="error"
                duration={3000}
                onClose={() => setAlertMessage("")}
            />
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Enter Buy-In</DialogTitle>
                </DialogHeader>
                <div className="flex flex-col gap-4">
                    <div className="text-sm text-muted">
                        Select amount: £{buyIn}
                    </div>
                    <Slider
                        value={[buyIn]}
                        onValueChange={([newValue]) => setBuyIn(newValue)}
                        min={minBuyIn}
                        max={maxBuyIn}
                        step={10}
                    />
                    <Input
                        type="number"
                        placeholder="Or enter exact amount"
                        value={buyIn}
                        onChange={(e) => setBuyIn(Number(e.target.value))}
                    />
                </div>
                <DialogFooter>
                    <Button variant="outline" size="sm" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button size="sm" onClick={handleJoinGame}>
                        Join Game
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
