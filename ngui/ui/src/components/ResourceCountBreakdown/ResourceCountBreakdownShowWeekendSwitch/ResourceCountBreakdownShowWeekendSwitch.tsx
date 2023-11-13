import { FormControlLabel, Typography } from "@mui/material";
import Switch from "@mui/material/Switch";
import { FormattedMessage } from "react-intl";
import { useShowWeekends } from "hooks/useShowWeekends";

const ResourceCountBreakdownShowWeekendSwitch = () => {
  const { showWeekends, onChange } = useShowWeekends();

  return (
    <FormControlLabel
      control={<Switch onChange={(e) => onChange(e.target.checked)} checked={showWeekends} />}
      label={
        <Typography>
          <FormattedMessage id="showWeekends" />
        </Typography>
      }
      labelPlacement="start"
      sx={{
        marginRight: (theme) => theme.spacing(2)
      }}
    />
  );
};

export default ResourceCountBreakdownShowWeekendSwitch;
