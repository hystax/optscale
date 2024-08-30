import { FormattedMessage } from "react-intl";
import { Switch } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.SHARE;

const ShareSwitch = () => (
  <Switch
    name={FIELD_NAME}
    label={<FormattedMessage id="share" />}
    adornment={<QuestionMark messageId="shareDashboardDescription" />}
    sx={{
      paddingLeft: (theme) => theme.spacing(1.75)
    }}
  />
);

export default ShareSwitch;
