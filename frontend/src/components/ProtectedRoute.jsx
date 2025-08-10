import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import api from "../api";
import { useState, useEffect } from "react";
import { Outlet } from "react-router-dom";

export default function ProtectedRoute({ children }) {
    const [isAuthorized, setIsAuthorized] = useState(null);

    useEffect(() => {
        //auth().catch(() => setIsAuthorized(false));
        setIsAuthorized(true);
    }, []);

    const refreshToken = async () => {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN);
        const decodedRefresh = jwtDecode(refreshToken);
        const timeNow = Date.now() / 1000;

        if (timeNow > decodedRefresh.exp) {
            setIsAuthorized(false);
        } else {
            try {
                const response = await api.post("/api/refresh-token/", {
                    refresh: refreshToken,
                });
                if (response.status === 200) {
                    localStorage.setItem(ACCESS_TOKEN, response.data.access);
                    setIsAuthorized(true);
                } else {
                    console.log(response.data.detail);
                    setIsAuthorized(false);
                }
            } catch (error) {
                setIsAuthorized(false);
            }
        }
    };

    const auth = async () => {
        const access = localStorage.getItem(ACCESS_TOKEN);
        const refresh = localStorage.getItem(REFRESH_TOKEN);
        if (!access) {
            setIsAuthorized(false);
        } else {
            const decodedAccess = jwtDecode(access);
            const timeNow = Date.now() / 1000;
            if (timeNow > decodedAccess.exp) {
                await refreshToken();
            } else {
                setIsAuthorized(true);
            }
        }
    };
    if (isAuthorized == null) {
        return <div>loading..</div>;
    }
    return isAuthorized ? <Outlet /> : <Navigate to="/login" />;
}
