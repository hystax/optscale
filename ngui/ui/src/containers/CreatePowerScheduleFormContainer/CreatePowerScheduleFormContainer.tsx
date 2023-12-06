import { useNavigate } from "react-router-dom";
import CreatePowerScheduleForm, { FIELD_NAMES } from "components/CreatePowerScheduleForm";
import PowerScheduleService from "services/PowerScheduleService";
import { POWER_SCHEDULES } from "urls";
import {
  EN_TIME_FORMAT,
  EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
  endOfDay,
  formatTimeString,
  millisecondsToSeconds,
  moveDateFromUTC,
  startOfDay
} from "utils/datetime";

const CreatePowerScheduleFormContainer = () => {
  const navigate = useNavigate();

  const { useCreate } = PowerScheduleService();
  const { onCreate, isLoading: isCreateLoading } = useCreate();

  const onSubmit = (formData) => {
    const data = {
      name: formData[FIELD_NAMES.NAME],
      power_on: formatTimeString({
        timeString: `${formData[FIELD_NAMES.POWER_ON.FIELD][FIELD_NAMES.POWER_ON.TIME]} ${
          formData[FIELD_NAMES.POWER_ON.FIELD][FIELD_NAMES.POWER_ON.TIME_OF_DAY]
        }`,
        timeStringFormat: EN_TIME_FORMAT,
        parsedTimeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM
      }),
      power_off: formatTimeString({
        timeString: `${formData[FIELD_NAMES.POWER_OFF.FIELD][FIELD_NAMES.POWER_OFF.TIME]} ${
          formData[FIELD_NAMES.POWER_OFF.FIELD][FIELD_NAMES.POWER_OFF.TIME_OF_DAY]
        }`,
        timeStringFormat: EN_TIME_FORMAT,
        parsedTimeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM
      }),
      timezone: formData[FIELD_NAMES.TIME_ZONE],
      start_date: formData[FIELD_NAMES.INITIATION_DATE]
        ? millisecondsToSeconds(moveDateFromUTC(startOfDay(formData[FIELD_NAMES.INITIATION_DATE])))
        : undefined,
      end_date: formData[FIELD_NAMES.EXPIRATION_DATE]
        ? millisecondsToSeconds(moveDateFromUTC(endOfDay(formData[FIELD_NAMES.EXPIRATION_DATE])))
        : undefined,
      enabled: true
    };

    onCreate(data).then(() => navigate(POWER_SCHEDULES));
  };

  const onCancel = () => navigate(POWER_SCHEDULES);

  return (
    <CreatePowerScheduleForm
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoadingProps={{
        isSubmitLoading: isCreateLoading
      }}
    />
  );
};

export default CreatePowerScheduleFormContainer;
