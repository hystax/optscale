import { MERIDIEM_NAMES } from "utils/datetime";

export type FormValues = {
  name: string;
  powerOn: { time: string; timeOfDay: (typeof MERIDIEM_NAMES)[keyof typeof MERIDIEM_NAMES] };
  powerOff: { time: string; timeOfDay: (typeof MERIDIEM_NAMES)[keyof typeof MERIDIEM_NAMES] };
  timeZone: string;
  expirationDate?: Date;
  initiationDate?: Date;
};
