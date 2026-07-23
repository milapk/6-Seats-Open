import * as React from "react";
import { cn } from "@/lib/utils";

const Input = React.forwardRef(({ className, type, ...props }, ref) => {
    return (
        <input
            type={type}
            ref={ref}
            className={cn(
                "flex h-10 w-full rounded-md border border-border bg-white/5 px-3 py-2 text-sm text-foreground placeholder:text-muted transition-colors outline-none",
                "focus-visible:border-ring focus-visible:ring-1 focus-visible:ring-ring",
                "disabled:cursor-not-allowed disabled:opacity-50",
                className,
            )}
            {...props}
        />
    );
});
Input.displayName = "Input";

export { Input };
