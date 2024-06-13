import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";

export const FIELD_NAME = "name";

const DataSourceNameField = () => (
  <TextInput name={FIELD_NAME} required dataTestId="input_cloud_account_name" label={<FormattedMessage id="name" />} />
);

export default DataSourceNameField;
