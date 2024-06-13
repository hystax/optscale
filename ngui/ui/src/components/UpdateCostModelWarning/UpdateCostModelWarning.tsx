import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import useStyles from "./UpdateCostModelWarning.styles";

const UpdateCostModelWarning = ({ costModelType, dataTestId }) => {
  const { classes } = useStyles();

  return (
    <Typography className={classes.warningText} gutterBottom data-test-id={dataTestId}>
      <FormattedMessage
        id="costModelFormWarning"
        values={{
          break: <br />,
          costModelType
        }}
      />
    </Typography>
  );
};

export default UpdateCostModelWarning;
