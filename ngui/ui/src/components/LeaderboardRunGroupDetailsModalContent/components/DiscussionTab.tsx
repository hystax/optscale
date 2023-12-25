import SendIcon from "@mui/icons-material/Send";
import { InputAdornment, OutlinedInput, Typography } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import IconButton from "components/IconButton";
import { SPACING_2 } from "utils/layouts";

const DiscussionTab = () => {
  const intl = useIntl();
  return (
    <>
      <Typography>
        <FormattedMessage id="noCommentsHereYet" />
      </Typography>
      <OutlinedInput
        sx={{ mt: SPACING_2 }}
        placeholder={intl.formatMessage({ id: "comment..." })}
        id="outlined-adornment-password"
        endAdornment={
          <InputAdornment position="end">
            <IconButton disabled icon={<SendIcon />} />
          </InputAdornment>
        }
      />
    </>
  );
};

export default DiscussionTab;
