import { FormattedMessage } from "react-intl";
import { Checkbox } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAMES = Object.freeze({
  USE_EDP_DISCOUNT: "useEdpDiscount"
});

const AwsRootUseAwsEdpDiscount = () => (
  <Checkbox
    name={FIELD_NAMES.USE_EDP_DISCOUNT}
    label={<FormattedMessage id="useAwsEdpDiscount" />}
    defaultValue={false}
    adornment={<QuestionMark tooltipText={<FormattedMessage id="useAwsEdpDiscountDescription" />} />}
  />
);

export default AwsRootUseAwsEdpDiscount;
