import * as React from "react";
import * as TogglePrimitive from "@radix-ui/react-toggle";
import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

const toggleVariants = cva(
    "inline-flex flex-1 items-center justify-center whitespace-nowrap border border-border bg-transparent px-3 py-2.5 text-sm font-medium tracking-wide text-muted transition-colors first:rounded-l-md last:rounded-r-md hover:text-foreground data-[state=on]:border-accent/40 data-[state=on]:bg-accent/10 data-[state=on]:text-accent",
);

const Toggle = React.forwardRef(({ className, ...props }, ref) => (
    <TogglePrimitive.Root
        ref={ref}
        className={cn(toggleVariants(), className)}
        {...props}
    />
));
Toggle.displayName = TogglePrimitive.Root.displayName;

export { Toggle, toggleVariants };
