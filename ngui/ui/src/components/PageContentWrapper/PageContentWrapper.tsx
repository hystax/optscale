import Box from "@mui/material/Box";
import useStyles from "./PageContentWrapper.styles";

const PageContentWrapper = ({ children }) => {
  const { classes } = useStyles();

  return <Box className={classes.page}>{children}</Box>;
};

export default PageContentWrapper;
