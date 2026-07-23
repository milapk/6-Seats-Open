import * as React from "react";
import * as ToggleGroupPrimitive from "@radix-ui/react-toggle-group";
import { cn } from "@/lib/utils";
import { toggleVariants } from "@/components/ui/toggle";

const ToggleGroup = React.forwardRef(({ className, ...props }, ref) => (
    <ToggleGroupPrimitive.Root
        ref={ref}
        className={cn("flex w-full", className)}
        {...props}
    />
));
ToggleGroup.displayName = ToggleGroupPrimitive.Root.displayName;

const ToggleGroupItem = React.forwardRef(
    ({ className, children, ...props }, ref) => (
        <ToggleGroupPrimitive.Item
            ref={ref}
            className={cn(toggleVariants(), className)}
            {...props}
        >
            {children}
        </ToggleGroupPrimitive.Item>
    ),
);
ToggleGroupItem.displayName = ToggleGroupPrimitive.Item.displayName;

export { ToggleGroup, ToggleGroupItem };
