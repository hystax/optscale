import { FormattedMessage } from "react-intl";
import { Checkbox } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.AUTO_EXTENSION;

const AutoExtendCheckbox = ({ isLoading = false, isReadOnly = false }) => (
  <Checkbox
    name={FIELD_NAME}
    isLoading={isLoading}
    disabled={isReadOnly}
    label={
      <div style={{ display: "flex", alignItems: "center" }}>
        <FormattedMessage id="extendParentPoolsLimit" />
        <QuestionMark messageId="extendParentPoolsLimitDescription" dataTestId="qmark_auto_extension" />
      </div>
    }
  />
);

export default AutoExtendCheckbox;
