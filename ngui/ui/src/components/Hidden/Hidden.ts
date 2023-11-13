import { useMediaQuery } from "@mui/material";

const Hidden = ({ mode, breakpoint, children }) => {
  const hide = useMediaQuery((theme) => theme.breakpoints[mode](breakpoint));

  return hide ? null : children;
};

export default Hidden;
