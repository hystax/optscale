import { FormControl, FormControlLabel, Switch, Typography } from "@mui/material";
import { Box } from "@mui/system";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import QuestionMark from "components/QuestionMark";
import { FIELD_NAMES } from "../constants";

const ShareSwitch = ({ name = FIELD_NAMES.SHARE }) => {
  const { control } = useFormContext();

  return (
    <FormControl
      fullWidth
      sx={{
        paddingLeft: (theme) => theme.spacing(1.75)
      }}
    >
      <FormControlLabel
        control={
          <Controller
            name={name}
            control={control}
            render={({ field: { onChange, value } }) => <Switch checked={value} onChange={(e) => onChange(e.target.checked)} />}
          />
        }
        label={
          <Box display="flex" alignItems="center">
            <Typography>
              <FormattedMessage id="share" />
            </Typography>
            <QuestionMark messageId="shareDashboardDescription" />
          </Box>
        }
      />
    </FormControl>
  );
};

export default ShareSwitch;
