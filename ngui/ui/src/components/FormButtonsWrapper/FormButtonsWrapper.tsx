import Box from "@mui/material/Box";
import useStyles from "./FormButtonsWrapper.styles";

const FormButtonsWrapper = ({ children, justifyContent = "flex-start", alignItems, mt = 2, mb = 0 }) => {
  const { classes } = useStyles();
  return (
    <Box display="flex" mt={mt} mb={mb} justifyContent={justifyContent} alignItems={alignItems} className={classes.wrapper}>
      {children}
    </Box>
  );
};

export default FormButtonsWrapper;
