import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.CALENDAR_ID]: string;
};

export type ConnectGoogleCalendarFormProps = {
  serviceAccount: string;
  onCancel: () => void;
  onSubmit: (calendarId: string) => void;
  isLoading: boolean;
};
