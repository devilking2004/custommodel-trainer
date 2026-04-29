import Link, { type LinkProps } from "next/link";
import type { AnchorHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type LinkButtonProps = LinkProps &
  AnchorHTMLAttributes<HTMLAnchorElement> & {
    variant?: "primary" | "secondary" | "ghost";
  };

export function LinkButton({ className, variant = "primary", ...props }: LinkButtonProps) {
  const variants = {
    primary: "bg-slate-950 text-white hover:bg-slate-800 shadow-sm",
    secondary: "bg-white text-slate-950 border border-slate-200 hover:bg-slate-50",
    ghost: "text-slate-700 hover:bg-slate-100",
  };

  return (
    <Link
      className={cn(
        "inline-flex h-10 items-center justify-center rounded-xl px-4 text-sm font-semibold transition",
        variants[variant],
        className,
      )}
      {...props}
    />
  );
}
