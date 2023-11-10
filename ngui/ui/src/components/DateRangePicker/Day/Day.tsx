import { IconButton, Typography } from "@mui/material";
import useStyles from "./Day.styles";

const Day = ({ disabled, highlighted, outlined, filled, onClick, onHover, value }) => {
  const { classes, cx } = useStyles();
  return (
    <div
      className={cx(classes.buttonContainer, {
        [classes.highlighted]: !disabled && highlighted
      })}
    >
      <IconButton
        className={cx(classes.button, {
          [classes.outlined]: !disabled && outlined,
          [classes.filled]: !disabled && filled
        })}
        disabled={disabled}
        onClick={onClick}
        onMouseOver={onHover}
      >
        <Typography
          className={cx(classes.buttonText, {
            [classes.contrast]: !disabled && filled
          })}
          disabled={disabled}
        >
          {value}
        </Typography>
      </IconButton>
    </div>
  );
};

export default Day;
