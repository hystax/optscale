import { FormattedMessage } from "react-intl";
import { PasswordInput, TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAMES = Object.freeze({
  PASSWORD: "password",
  USER: "user"
});

const KubernetesCredentials = () => (
  <>
    <TextInput
      name={FIELD_NAMES.USER}
      required
      dataTestId="input_user"
      InputProps={{
        endAdornment: <QuestionMark messageId="userTooltip" dataTestId="qmark_user" />
      }}
      label={<FormattedMessage id="user" />}
    />
    <PasswordInput
      name={FIELD_NAMES.PASSWORD}
      required
      dataTestId="input_password"
      InputProps={{
        endAdornment: <QuestionMark messageId="passwordTooltip" dataTestId="qmark_password" />
      }}
      label={<FormattedMessage id="password" />}
      autoComplete="one-time-code"
    />
  </>
);

export default KubernetesCredentials;
