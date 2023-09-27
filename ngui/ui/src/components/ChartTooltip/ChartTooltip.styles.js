import { keyframes } from "tss-react";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({
  container: {
    background: theme.palette.common.white,
    borderRadius: theme.spacing(0.25),
    boxShadow: "rgba(0, 0, 0, 0.25) 0px 1px 2px",
    paddingTop: theme.spacing(0.5),
    paddingBottom: theme.spacing(0.5),
    paddingLeft: theme.spacing(1),
    paddingRight: theme.spacing(1),
    // styles below is a workaround https://github.com/plouc/nivo/issues/2161
    opacity: 0,
    animation: `${keyframes`
            0%, 10% {
              opacity: 0;
            }
            100% {
              opacity: 1;
            }
            `} 0.1s normal forwards ease-out`
  }
}));

export default useStyles;
