import { useState } from "react";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import {
    Button,
    TextField,
    Alert,
    ToggleButton,
    ToggleButtonGroup,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import "../styles/UserForm.css";
import formImg from "../assets/191.jpg";

export default function UserForm({ type }) {
    const title = type === "LOGIN" ? "Login" : "Register";
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [authMode, setAuthMode] = useState(type);
    const navigate = useNavigate();

    const handleToggleChange = (e, newMode) => {
        if (newMode !== null) {
            setAuthMode(newMode);
        }
    };

    const goToLogin = (e) => {
        if (type !== 'LOGIN'){
            navigate('/login')
        }
    }

    const goToRegister = (e) => {
        if (type !== 'REGISTER'){
            navigate('/register')
        }
    }
    return (
        <div id="user-form-root">
            <div id="form-container">
                <div id="container-left">
                    <img id="img" src={formImg} />
                </div>
                <div id="container-right">
                    <div id="container-switch-page">
                        <ToggleButtonGroup
                            value={authMode}
                            exclusive
                            onChange={handleToggleChange}
                            sx={{
                                width: "100%",
                                "& .MuiToggleButton-root": {
                                    flex: 1,
                                    border: "1px solid #ccc",
                                    borderRadius: 0,
                                    color: "white",
                                    backgroundColor: "#1e2b36ba",
                                    "&.Mui-selected": {
                                        backgroundColor: "#4a85b8",
                                        color: "white",
                                    },
                                    "&:hover": {
                                        backgroundColor: "#3a5a7f",
                                    },
                                },
                            }}
                        >
                            <ToggleButton value="LOGIN" onClick={goToLogin}>LOGIN</ToggleButton>
                            <ToggleButton value="REGISTER" onClick={goToRegister}>
                                REGISTER
                            </ToggleButton>
                        </ToggleButtonGroup>
                    </div>
                    <div id="container-form">
                        <div id="form-textfield">
                            <TextField
                                variant="filled"
                                size="small"
                                label="Username"
                                color="primary"
                            ></TextField>
                        </div>
                        <div id="form-textfield">
                            <TextField
                                variant="filled"
                                size="small"
                                label="Password"
                                color="primary"
                            ></TextField>
                        </div>
                        <Button
                            id="form-sumbit"
                            variant="contained"
                            color="secondary"
                        >
                            {title}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
