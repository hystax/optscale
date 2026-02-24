import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import InputLoader from "components/InputLoader";
import QuestionMark from "components/QuestionMark";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.VIRTUAL_ENVIRONMENT_PATH;

const VirtualEnvironmentPathField = ({ isLoading = false }) =>
  isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <TextInput
      label={<FormattedMessage id="virtualEnvironmentPath" />}
      name={FIELD_NAME}
      InputProps={{
        endAdornment: (
          <QuestionMark
            messageId="runsetVirtualEnvironmentPathDescription"
            messageValues={{
              i: (chunks) => <i>{chunks}</i>,
            }}
            dataTestId="qmark_runset_virtual_environment_path"
          />
        ),
      }}
    />
  );

export default VirtualEnvironmentPathField;
