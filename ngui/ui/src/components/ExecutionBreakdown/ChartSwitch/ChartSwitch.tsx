import { FormControlLabel, Typography } from "@mui/material";
import Switch from "@mui/material/Switch";
import { FormattedMessage } from "react-intl";

const ChartSwitch = ({ checked, onChange, messageId }) => (
  <FormControlLabel
    control={<Switch onChange={(e) => onChange(e.target.checked)} checked={checked} />}
    label={
      <Typography>
        <FormattedMessage id={messageId} />
      </Typography>
    }
    labelPlacement="end"
  />
);

export default ChartSwitch;
