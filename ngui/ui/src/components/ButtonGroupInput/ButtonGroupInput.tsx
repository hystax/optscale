import FormControl from "@mui/material/FormControl";
import Typography from "@mui/material/Typography";
import ButtonGroup from "components/ButtonGroup";
import StyledFormLabel from "components/StyledFormLabel";
import useStyles from "./ButtonGroupInput.styles";

const ButtonGroupInput = ({
  labelText,
  buttons,
  activeButtonIndex,
  fullWidth = false,
  required = true,
  helperText,
  typographyProps
}) => {
  const { classes } = useStyles();

  return (
    <FormControl fullWidth={fullWidth}>
      <StyledFormLabel required={required}>{labelText}</StyledFormLabel>
      <ButtonGroup fullWidth={fullWidth} buttons={buttons} activeButtonIndex={activeButtonIndex} />
      {helperText && (
        <Typography className={classes.helperText} {...typographyProps}>
          {helperText}
        </Typography>
      )}
    </FormControl>
  );
};

export default ButtonGroupInput;
