import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import QuestionMark from "components/QuestionMark";

export const FIELD_NAME = "serviceAccountId";

const ServiceAccountId = () => (
  <TextInput
    name={FIELD_NAME}
    required
    dataTestId="input_nebius_service_account_id"
    InputProps={{
      endAdornment: (
        <QuestionMark
          messageId="nebiusServiceAccountIdTooltip"
          messageValues={{
            i: (chunks) => <i>{chunks}</i>
          }}
          dataTestId="qmark_service_account_id"
        />
      )
    }}
    label={<FormattedMessage id="serviceAccountId" />}
    autoComplete="off"
    sx={{
      marginBottom: (theme) => theme.spacing(1)
    }}
  />
);

export default ServiceAccountId;
