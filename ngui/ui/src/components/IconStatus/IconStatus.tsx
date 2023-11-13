import { FormattedMessage } from "react-intl";
import IconLabel from "components/IconLabel";

const IconStatus = ({ icon: Icon, color, labelMessageId, text }) => (
  <IconLabel
    icon={<Icon fontSize="small" color={color} />}
    label={
      <>
        <FormattedMessage id={labelMessageId} />
        {text && <>&nbsp;({text})</>}
      </>
    }
  />
);

export default IconStatus;
