import { useState, useEffect } from "react";
import PersonIcon from "@mui/icons-material/Person";
import { Button } from "@mui/material";
import "../styles/Home.css";
export default function Home() {
    const tableData = [
        { stakes: "1k/2k", buyIn: 50, tables: "8 Tables", players: 16 },
        { stakes: "250/500", buyIn: 50, tables: "18 Tables", players: 26 },
        { stakes: "50/100", buyIn: 50, tables: "34 Tables", players: 71 },
        { stakes: "5/10", buyIn: 500, tables: "9 Tables", players: 130 },
        { stakes: "1/2", buyIn: 50, tables: "53 Tables", players: 276 },
    ];
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
                    {tableData.map((row, index) => (
                        <div key={index} className="table-row">
                            <div>{row.stakes}</div>
                            <div>{row.buyIn}</div>
                            <div>{row.tables}</div>
                            <div>{row.players}</div>
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
                    <div id="sidebar-chips">Chips: 590</div>
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
