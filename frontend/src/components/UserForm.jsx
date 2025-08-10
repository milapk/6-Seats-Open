import { useState } from "react";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import {
    Button,
    TextField,
    ToggleButton,
    ToggleButtonGroup,
    FormControl,
    InputLabel,
    InputAdornment,
    IconButton,
    FilledInput,
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import CustomAlerts from "./CustomAlerts";
import { useNavigate } from "react-router-dom";
import "../styles/UserForm.css";
import api from "../api.js";
import formImg from "../assets/191.jpg";

export default function UserForm({ type }) {
    const title = type === "LOGIN" ? "Login" : "Register";
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [authMode, setAuthMode] = useState(type);
    const [alertMessage, setAlertMessage] = useState("");
    const navigate = useNavigate();

    const handleLogin = async () => {
        try {
            const response = await api.post("/api/obtain-token/", {
                username,
                password,
            });
            if (response.status === 200) {
                localStorage.setItem(ACCESS_TOKEN, response.data.access);
                localStorage.setItem(REFRESH_TOKEN, response.data.refresh);
                navigate("/");
            }
        } catch (error) {
            if (error.response && error.response.status === 401) {
                setAlertMessage(
                    "Invalid Username or Password, please try again!"
                );
            } else {
                setAlertMessage(
                    "An error occurred. Please refresh or try again later."
                );
            }
        }
    };

    const handleUserFormSumbition = async (e) => {
        if (password === "" && username === "") {
            setAlertMessage("Please enter both Username and Password!");
            return;
        } else if (username === "") {
            setAlertMessage("Please enter a Username!");
            return;
        } else if (password === "") {
            setAlertMessage("Please enter a Password!");
            return;
        }
        try {
            if (type === "LOGIN") {
                handleLogin();
            } else if (type === "REGISTER") {
                const response = await api.post("/api/register/", {
                    username,
                    password,
                });
                if (response.status === 201) {
                    handleLogin();
                }
            }
        } catch (error) {
            if (error.response && error.response.data.username) {
                setAlertMessage(
                    "Username is already taken, please enter another one!"
                );
            } else {
                setAlertMessage(
                    "An error occurred. Please refresh or try again later."
                );
            }
        }
    };

    const handleToggleChange = (e, newMode) => {
        if (newMode !== null) {
            setAuthMode(newMode);
        }
    };

    const handleShowPassword = () => {
        setShowPassword((show) => !show);
    };

    const handleMouseDownPassword = (event) => {
        event.preventDefault();
    };

    const handleMouseUpPassword = (event) => {
        event.preventDefault();
    };

    const handleUsernameChange = (e) => {
        setUsername(e.target.value);
    };

    const handlePasswordChange = (e) => {
        setPassword(e.target.value);
    };

    const goToLogin = (e) => {
        if (type !== "LOGIN") {
            navigate("/login");
        }
    };

    const goToRegister = (e) => {
        if (type !== "REGISTER") {
            navigate("/register");
        }
    };
    return (
        <div id="user-form-root">
            <CustomAlerts
                message={alertMessage}
                severity="error"
                duration={3000}
                onClose={() => setAlertMessage("")}
            />
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
                            <ToggleButton value="LOGIN" onClick={goToLogin}>
                                LOGIN
                            </ToggleButton>
                            <ToggleButton
                                value="REGISTER"
                                onClick={goToRegister}
                            >
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
                                onChange={handleUsernameChange}
                                sx={{width:'100%'}}
                            ></TextField>
                        </div>
                        <div id="form-textfield">
                            <FormControl variant="filled" sx={{width:'100%'}}>
                                <InputLabel htmlFor="filled-adornment-password">
                                    Password
                                </InputLabel>
                                <FilledInput
                                    id="filled-adornment-password"
                                    type={showPassword ? "text" : "password"}
                                    endAdornment={
                                        <InputAdornment position="end">
                                            <IconButton
                                                
                                                onClick={handleShowPassword}
                                                
                                            >
                                                {showPassword ? (
                                                    <VisibilityOff />
                                                ) : (
                                                    <Visibility />
                                                )}
                                            </IconButton>
                                        </InputAdornment>
                                    }
                                />
                            </FormControl>
                        </div>
                        <Button
                            id="form-sumbit"
                            variant="contained"
                            color="secondary"
                            onClick={handleUserFormSumbition}
                        >
                            {title}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
