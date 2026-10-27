import { useNavigate } from "react-router-dom";
import { CreatePowerScheduleForm, FormValues } from "components/PowerScheduleForm";
import {
  getEndDateApiParam,
  getNameApiParam,
  getStartDateApiParam,
  getTimeZoneApiParam,
  getTriggersApiParam,
} from "components/PowerScheduleForm/utils";
import PowerScheduleService, { type PowerScheduleApiParams } from "services/PowerScheduleService";
import { POWER_SCHEDULES } from "urls";

const CreatePowerScheduleFormContainer = () => {
  const navigate = useNavigate();

  const { useCreate } = PowerScheduleService();
  const { onCreate, isLoading: isCreateLoading } = useCreate();

  const onSubmit = (formData: FormValues) => {
    const data: PowerScheduleApiParams = {
      name: getNameApiParam(formData),
      triggers: getTriggersApiParam(formData),
      timezone: getTimeZoneApiParam(formData),
      start_date: getStartDateApiParam(formData),
      end_date: getEndDateApiParam(formData),
      enabled: true,
    };

    onCreate(data).then(() => navigate(POWER_SCHEDULES));
  };

  const onCancel = () => navigate(POWER_SCHEDULES);

  return (
    <CreatePowerScheduleForm
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoadingProps={{
        isSubmitLoading: isCreateLoading,
      }}
    />
  );
};

export default CreatePowerScheduleFormContainer;
