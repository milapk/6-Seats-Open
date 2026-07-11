import { Toaster as Sonner } from "sonner";

const Toaster = (props) => {
    return (
        <Sonner
            theme="dark"
            position="top-center"
            toastOptions={{
                classNames: {
                    toast: "!bg-panel-alt !text-foreground !border !border-border !rounded-lg",
                    error: "!bg-red-800",
                    success: "!border-accent/40",
                },
            }}
            {...props}
        />
    );
};

export { Toaster };
