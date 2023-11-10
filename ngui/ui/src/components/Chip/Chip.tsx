import CancelIcon from "@mui/icons-material/Cancel";
import MuiChip from "@mui/material/Chip";
import useStyles from "./Chip.styles";

const Chip = ({
  color = "info",
  variant = "filled",
  size = "small",
  uppercase = false,
  dataTestIds = {},
  stopMouseDownPropagationOnDelete = false, // use case: when chip is inside selector value, need to delete chip, not to open selector
  multiline = false,
  className,
  ...rest
}) => {
  const { classes, cx } = useStyles();

  const chipClasses = cx(classes.chip, uppercase ? classes.uppercase : "", multiline ? classes.multiline : "", className);

  const { chip: chipDataTestId, deleteIcon: deleteIconDataTestId } = dataTestIds;

  return (
    <MuiChip
      {...rest}
      variant={variant}
      color={color}
      deleteIcon={
        <CancelIcon
          data-test-id={deleteIconDataTestId}
          onMouseDown={stopMouseDownPropagationOnDelete ? (e) => e.stopPropagation() : undefined}
        />
      }
      data-test-id={chipDataTestId}
      className={chipClasses}
      size={size}
    />
  );
};

export default Chip;
