import { FormattedMessage } from "react-intl";
import { RadioGroup } from "components/forms/common/fields";
import { FIELD_NAMES, REASONS } from "../constants";

const FIELD_NAME = FIELD_NAMES.REASON;

const ReasonsRadioGroup = () => (
  <RadioGroup
    name={FIELD_NAME}
    labelMessageId="reasonQuestion"
    radioButtons={[
      {
        label: <FormattedMessage id="reasonSavings" />,
        value: REASONS.SAVINGS,
        dataTestId: "radiobtn_savings"
      },
      {
        label: <FormattedMessage id="reasonFeatures" />,
        value: REASONS.FEATURES,
        dataTestId: "radiobtn_features"
      },
      {
        label: <FormattedMessage id="reasonGoal" />,
        value: REASONS.GOAL,
        dataTestId: "radiobtn_goal"
      },
      {
        label: <FormattedMessage id="other" />,
        value: REASONS.OTHER,
        dataTestId: "radiobtn_other"
      }
    ]}
  />
);

export default ReasonsRadioGroup;
