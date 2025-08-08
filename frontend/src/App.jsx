import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, CssBaseline } from "@mui/material";
import theme from "./styles/theme";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Home from './pages/Home'
import NotFound from './pages/NotFound'
import Register from './pages/Register'

function Logout() {
    localStorage.clear();
    sessionStorage.clear();
    return <Navigate to="/login"></Navigate>;
}

function App() {
    return (
        <ThemeProvider theme={theme}>
            <BrowserRouter>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/logout" element={<Logout />} />
                    <Route path="/" element={<ProtectedRoute />}>
                        <Route index element={<Home />} />
                    </Route>
                    <Route path="*" element={<NotFound />} />
                </Routes>
            </BrowserRouter>
        </ThemeProvider>
    );
}

export default App;
