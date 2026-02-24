import EventBusyOutlinedIcon from "@mui/icons-material/EventBusyOutlined";
import { Alert } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { EN_FORMAT, format, secondsToMilliseconds } from "utils/datetime";

type CanceledAlertProps = {
  endDate: number;
};

const CanceledAlert = ({ endDate }: CanceledAlertProps) => (
  <Alert icon={<EventBusyOutlinedIcon />} severity="info">
    <FormattedMessage
      id="yourSubscriptionWillBeCanceledOn"
      values={{
        time: format(secondsToMilliseconds(endDate), EN_FORMAT),
      }}
    />
  </Alert>
);

export default CanceledAlert;
