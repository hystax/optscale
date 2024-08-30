import { FormattedMessage } from "react-intl";
import { RadioGroup } from "components/forms/common/fields";
import { FIELD_NAMES, SAVE_AS_VALUES } from "../constants";

const FIELD_NAME = FIELD_NAMES.SAVE_AS;

const SaveAsRadioGroup = ({ saveThisDisabled = false }) => (
  <RadioGroup
    name={FIELD_NAME}
    radioButtons={[
      {
        dataTestId: "radio_btn_save_this",
        disabled: saveThisDisabled,
        value: SAVE_AS_VALUES.SAVE_THIS,
        label: <FormattedMessage id="saveThisDashboard" />
      },
      {
        dataTestId: "radio_btn_save_as_new",
        value: SAVE_AS_VALUES.SAVE_AS_NEW,
        label: <FormattedMessage id="saveAsNewDashboard" />
      }
    ]}
  />
);

export default SaveAsRadioGroup;
