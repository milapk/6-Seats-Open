import { useState, useEffect } from "react";
import { Button } from "@mui/material";
import "../styles/Home.css";
export default function Home() {
    const tableData = [
        { stakes: "1k/2k", buyIn: 50, tables: "8 Tables", players: 276 },
        { stakes: "250/500", buyIn: 50, tables: "18 Tables", players: 276 },
        { stakes: "50/100", buyIn: 50, tables: "34 Tables", players: 276 },
        { stakes: "5/10", buyIn: 500, tables: "9 Tables", players: 276 },
        { stakes: "1/2", buyIn: 50, tables: "53 Tables", players: 276 },
    ];
    return (
        <div id="home-root">
            <div id="table-container">
                <h1 id="table-title">Browse and Join Tables</h1>

                <div id="tables-header">
                    <div id="tables-header-column">Stakes</div>
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
                                    className="join-button"
                                >
                                    JOIN
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            <div id="sidebar">
                <div id="play-money">Play Money: 589</div>
                <Button
                    variant="contained"
                    color="secondary"
                    className="sidebar-button"
                >
                    Claim 500 chips every hour
                </Button>
                <Button
                    variant="contained"
                    color="secondary"
                    className="sidebar-button"
                >
                    Join private table
                </Button>
                <Button
                    variant="contained"
                    color="secondary"
                    className="sidebar-button"
                >
                    Create private table
                </Button>
            </div>
        </div>
    );
}
