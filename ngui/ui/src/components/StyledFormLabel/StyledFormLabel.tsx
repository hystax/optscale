import FormLabel from "@mui/material/FormLabel";
import useStyles from "./StyledFormLabel.styles";

const StyledFormLabel = ({ children, ...rest }) => {
  const { classes } = useStyles();
  return (
    <FormLabel {...rest} className={classes.label}>
      {children}
    </FormLabel>
  );
};

export default StyledFormLabel;
