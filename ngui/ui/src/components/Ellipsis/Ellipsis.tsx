import Typography from "@mui/material/Typography";
import useStyles from "./Ellipsis.styles";

const Ellipsis = ({ variant, component = "span", className = "" }) => {
  const { classes } = useStyles();
  return (
    <Typography className={classes[className]} component={component} variant={variant}>
      ...
    </Typography>
  );
};

export default Ellipsis;
