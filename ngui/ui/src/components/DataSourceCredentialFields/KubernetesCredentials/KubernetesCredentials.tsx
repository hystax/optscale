import { FormattedMessage } from "react-intl";
import { Checkbox, PasswordInput, TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAMES = Object.freeze({
  PASSWORD: "password",
  USER: "user",
  USE_FLAVOR_BASED_COST_MODEL: "flavor_based_cost_model",
});

const KubernetesCredentials = () => (
  <>
    <TextInput
      name={FIELD_NAMES.USER}
      required
      dataTestId="input_user"
      InputProps={{
        endAdornment: <QuestionMark messageId="userTooltip" dataTestId="qmark_user" />,
      }}
      label={<FormattedMessage id="user" />}
    />
    <PasswordInput
      name={FIELD_NAMES.PASSWORD}
      required
      dataTestId="input_password"
      InputProps={{
        endAdornment: <QuestionMark messageId="passwordTooltip" dataTestId="qmark_password" />,
      }}
      label={<FormattedMessage id="password" />}
      autoComplete="one-time-code"
    />
    <Checkbox
      name={FIELD_NAMES.USE_FLAVOR_BASED_COST_MODEL}
      label={<FormattedMessage id="useK8sFlavorBasedCostModel" />}
      defaultValue={false}
      adornment={<QuestionMark tooltipText={<FormattedMessage id="useK8sFlavorBasedCostModelDescription" />} />}
    />
  </>
);

export default KubernetesCredentials;
