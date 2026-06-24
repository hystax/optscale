import { POWER_SCHEDULE_ACTIONS } from "utils/constants";
import { MERIDIEM_NAMES } from "utils/datetime";
import { ObjectValues } from "utils/types";

export type Meridiem = ObjectValues<typeof MERIDIEM_NAMES>;

type Action = ObjectValues<typeof POWER_SCHEDULE_ACTIONS>;

export type FormValues = {
  name: string;
  timeZone: string;
  expirationDate?: Date;
  initiationDate?: Date;
  triggers: {
    time: string;
    action: Action;
    meridiem: Meridiem;
    daysOfWeek: number[];
  }[];
};
