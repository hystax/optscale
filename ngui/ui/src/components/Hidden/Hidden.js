import { useMediaQuery } from "@mui/material";
import PropTypes from "prop-types";

const Hidden = ({ mode, breakpoint, children }) => {
  const hide = useMediaQuery((theme) => theme.breakpoints[mode](breakpoint));

  return hide ? null : children;
};

Hidden.propTypes = {
  mode: PropTypes.oneOf(["up", "down"]).isRequired,
  breakpoint: PropTypes.oneOf(["xs", "sm", "md", "lg", "xl"]).isRequired,
  children: PropTypes.node.isRequired
};

export default Hidden;
