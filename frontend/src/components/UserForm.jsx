import { useState } from "react";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import { Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import CustomAlerts from "./CustomAlerts";
import { useNavigate } from "react-router-dom";
import "../styles/UserForm.css";
import api from "../api.js";
import formImg from "../assets/poker-image.jpg";

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
                    "Invalid Username or Password, please try again!",
                );
            } else {
                setAlertMessage(
                    "An error occurred. Please refresh or try again later.",
                );
            }
        }
    };

    const handleFormSubmit = async () => {
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
            localStorage.clear();
            sessionStorage.clear();
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
                    "Username is already taken, please enter another one!",
                );
            } else {
                setAlertMessage(
                    "An error occurred. Please refresh or try again later.",
                );
            }
        }
    };

    const handleToggleChange = (newMode) => {
        if (newMode !== null && newMode !== "") {
            setAuthMode(newMode);
            if (newMode === "LOGIN") goToLogin();
            if (newMode === "REGISTER") goToRegister();
        }
    };

    const handleShowPassword = () => {
        setShowPassword((show) => !show);
    };

    const handleUsernameChange = (e) => {
        setUsername(e.target.value);
    };

    const handlePasswordChange = (e) => {
        setPassword(e.target.value);
    };

    const goToLogin = () => {
        if (type !== "LOGIN") {
            navigate("/login");
        }
    };

    const goToRegister = () => {
        if (type !== "REGISTER") {
            navigate("/register");
        }
    };
    return (
        <div id="auth-root">
            <CustomAlerts
                message={alertMessage}
                severity="error"
                duration={3000}
                onClose={() => setAlertMessage("")}
            />
            <div className="auth-card">
                <div className="auth-hero">
                    <img className="auth-hero-image" src={formImg} />
                </div>
                <div className="auth-panel">
                    <div className="auth-mode-toggle">
                        <ToggleGroup
                            type="single"
                            value={authMode}
                            onValueChange={handleToggleChange}
                        >
                            <ToggleGroupItem value="LOGIN">
                                LOGIN
                            </ToggleGroupItem>
                            <ToggleGroupItem value="REGISTER">
                                REGISTER
                            </ToggleGroupItem>
                        </ToggleGroup>
                    </div>
                    <div className="auth-fields">
                        <div className="auth-field">
                            <Label htmlFor="username">Username</Label>
                            <Input
                                id="username"
                                onChange={handleUsernameChange}
                            />
                        </div>
                        <div className="auth-field">
                            <Label htmlFor="password">Password</Label>
                            <div className="auth-password-field relative">
                                <Input
                                    id="password"
                                    onChange={handlePasswordChange}
                                    type={showPassword ? "text" : "password"}
                                    className="pr-10"
                                />
                                <button
                                    type="button"
                                    onClick={handleShowPassword}
                                    className="auth-password-toggle absolute right-2 top-1/2 -translate-y-1/2 text-muted hover:text-foreground"
                                >
                                    {showPassword ? (
                                        <EyeOff size={18} />
                                    ) : (
                                        <Eye size={18} />
                                    )}
                                </button>
                            </div>
                        </div>
                        <Button
                            className="auth-submit-button"
                            onClick={handleFormSubmit}
                        >
                            {title}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
