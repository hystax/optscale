import { FormattedMessage } from "react-intl";
import { TextInput } from "components/forms/common/fields";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.CALENDAR_ID;

const CalendarIdField = () => (
  <TextInput name={FIELD_NAME} maxLength={null} label={<FormattedMessage id="calendarId" />} required />
);

export default CalendarIdField;
