import { useState, useEffect } from "react";
import PersonIcon from "@mui/icons-material/Person";
import { Button } from "@mui/material";
import api from "../api.js";
import "../styles/Home.css";
import numeral from 'numeral';

export default function Home() {
    const [tableData, setTableData] = useState([]);
    const [playerChip, setPlayerChips] = useState(0);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get("/api/get-table-data/");
                if (response.status === 200) {
                    setTableData([...response.data.table_data])
                    setPlayerChips(response.data.chips)
                }
            } catch (error) {}
        };
        fetchData()
    }, []);

    return (
        <div id="home-root">
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
                            <div>{numeral(table.small_blind).format('0,0')}/{numeral(table.big_blind).format('0,0')}</div>
                            <div>{numeral(table.buy_in).format('0,0')}</div>
                            <div>{numeral(table.games).format('0,0')}</div>
                            <div>{numeral(table.players).format('0,0')}</div>
                            <div>
                                <Button
                                    variant="contained"
                                    color="secondary"
                                    className="button"
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
                    <div id="sidebar-chips">Chips: {playerChip}</div>
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
                    >
                        Claim chips
                    </Button>
                </div>
            </div>
        </div>
    );
}
