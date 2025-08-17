import { useState, useEffect } from "react";
import PersonIcon from "@mui/icons-material/Person";
import { Button } from "@mui/material";
import AutoCloseAlert from "../components/CustomAlerts.jsx";
import BuyInDialog from "../components/BuyInDialog.jsx";
import api from "../api.js";
import "../styles/Home.css";
import numeral from "numeral";


export default function Home() {
    const [tableData, setTableData] = useState([]);
    const [smallBlind, setSmallBlind] = useState(0);
    const [bigBlind, setBigBlind] = useState(0);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [playerChip, setPlayerChips] = useState(0);
    const [alertMessage, setAlertMessage] = useState("");
    const [alertType, setAlertType] = useState('error')

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get("/api/get-table-data/");
                if (response.status === 200) {
                    setTableData([...response.data.table_data]);
                    setPlayerChips(response.data.chips);
                }
            } catch (error) {}
        };
        fetchData();
    }, []);

    const handleClaimChips = async () => {
        try {
            const response = await api.post("/api/claim-chips/");
            if (response.status === 200) {
                setPlayerChips(response.data.chips);
                setAlertType('success');
                setAlertMessage('Chips claimed successfully! Get more in an Hour!')
            }
        } catch (error) {
            if (error.response && error.response.status === 406){
                const time =  Math.floor(error.response.data.cool_down / 60)
                setAlertType('error');
                setAlertMessage(`Chips already claimed! Get more in an ${time} minutes!`)
            }
        }
    };

    const handleLeave = async () => {
        const response = await api.post("/api/leave-game/");
    }

    const handleDialognOpen = async (smallBlind, bigBlind) => {
        setBigBlind(bigBlind);
        setSmallBlind(smallBlind);
        setDialogOpen(true)

    }
    return (
        <div id="home-root">
            <BuyInDialog
                open={dialogOpen}
                onClose={() => setDialogOpen(false)}
                minBuyIn={100}
                maxBuyIn={1000}
                smallBlind={smallBlind}
                bigBlind={bigBlind}
            ></BuyInDialog>
            <AutoCloseAlert
                message={alertMessage}
                severity={alertType}
                duration={3000}
                onClose={() => setAlertMessage("")}
            />
            <div id="table-container">
                <h1 id="table-title">Browse and Join Tables</h1>

                <div id="tables-header">
                    <div id="tables-header-stakes-column">Stakes</div>
                    <div id="tables-header-column">Buy-In</div>
                    <div id="tables-header-column">Tables</div>
                    <div id="tables-header-column">Players</div>
                    <div id="tables-header-column">Action</div>
                </div>
                <div id="tables-rows">
                    {tableData.map((table, index) => (
                        <div key={index} className="table-row">
                            <div>
                                {numeral(table.small_blind).format("0,0")}/
                                {numeral(table.big_blind).format("0,0")}
                            </div>
                            <div>{numeral(table.buy_in).format("0,0")}</div>
                            <div>{numeral(table.games).format("0,0")}</div>
                            <div>{numeral(table.players).format("0,0")}</div>
                            <div>
                                <Button
                                    variant="contained"
                                    color="secondary"
                                    className="button"
                                    onClick={() => handleDialognOpen(table.small_blind, table.big_blind)}
                                >
                                    JOIN
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            <div id="sidebar">
                <div id="sidebar-profile">
                    <PersonIcon></PersonIcon>
                    <div id="sidebar-chips">Chips: £{playerChip}</div>
                </div>
                <div id="sidebar-private">
                    <div>Private tables</div>
                    <div id="sidebar-buttons">
                        <Button
                            variant="contained"
                            color="secondary"
                            className="button"
                        >
                            Join private table
                        </Button>
                    </div>

                    <div id="sidebar-buttons">
                        <Button
                            variant="contained"
                            color="secondary"
                            className="button"
                        >
                            Create private table
                        </Button>
                    </div>
                </div>
                <div id="sidebar-claim">
                    <Button
                        variant="contained"
                        color="secondary"
                        className="button"
                        onClick={handleClaimChips}
                    >
                        Claim chips
                    </Button>
                </div>
                <div id="sidebar-claim">
                    <Button
                        variant="contained"
                        color="secondary"
                        className="button"
                        onClick={handleLeave}
                    >
                        Leave
                    </Button>
                </div>
            </div>
        </div>
    );
}
