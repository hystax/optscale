import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import InputLoader from "components/InputLoader";
import QuestionMark from "components/QuestionMark";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.IMAGE;

const ImageField = ({ isLoading = false }) =>
  isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <TextInput
      label={<FormattedMessage id="image" />}
      name={FIELD_NAME}
      InputProps={{
        endAdornment: <QuestionMark messageId="runsetImageDescription" dataTestId="qmark_runset_image" />,
      }}
    />
  );

export default ImageField;
