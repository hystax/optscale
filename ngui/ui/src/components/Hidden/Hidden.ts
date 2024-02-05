import { type ReactNode } from "react";
import { useMediaQuery } from "@mui/material";

type HiddenProps = {
  mode: "up" | "down";
  breakpoint: "xs" | "sm" | "md" | "lg" | "xl";
  children: ReactNode;
};

const Hidden = ({ mode, breakpoint, children }: HiddenProps) => {
  const hide = useMediaQuery((theme) => theme.breakpoints[mode](breakpoint));

  return hide ? null : children;
};

export default Hidden;
