import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
    "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-semibold transition-transform",
    {
        variants: {
            variant: {
                default:
                    "bg-accent text-accent-foreground hover:bg-accent/90",
                outline:
                    "border border-border bg-transparent text-foreground hover:bg-white/5",
                ghost: "bg-transparent text-foreground hover:bg-white/5",
                icon: "bg-transparent text-foreground hover:bg-white/5",
            },
            size: {
                default: "h-10 px-4 py-2 w-full",
                sm: "h-8 px-3 text-xs",
                icon: "h-9 w-9 shrink-0 p-0",
            },
        },
        defaultVariants: {
            variant: "default",
            size: "default",
        },
    }
);

const Button = React.forwardRef(
    ({ className, variant, size, asChild = false, ...props }, ref) => {
        const Comp = asChild ? Slot : "button";
        return (
            <Comp
                ref={ref}
                className={cn(buttonVariants({ variant, size }), className)}
                {...props}
            />
        );
    }
);
Button.displayName = "Button";

export { Button, buttonVariants };
