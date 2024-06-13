import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.WEBHOOK_URL;

const WebhookUrlField = () => <TextInput name={FIELD_NAME} label={<FormattedMessage id="url" />} required margin="none" />;

export default WebhookUrlField;
