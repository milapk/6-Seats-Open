import { useEffect } from "react";
import { toast } from "sonner";

export default function AutoCloseAlert({
    message,
    severity = "error",
    duration = 3000,
    onClose,
}) {
    useEffect(() => {
        if (!message) return;
        const toastFn = severity === "success" ? toast.success : toast.error;
        toastFn(message, {
            duration,
            onDismiss: onClose,
            onAutoClose: onClose,
        });
    }, [message]);

    return null;
}
