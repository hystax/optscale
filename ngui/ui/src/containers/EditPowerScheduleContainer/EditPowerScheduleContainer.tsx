import { useNavigate, useParams } from "react-router-dom";
import EditPowerSchedule from "components/EditPowerSchedule";
import { type FormValues } from "components/PowerScheduleForm";
import {
  getEndDateApiParam,
  getNameApiParam,
  getStartDateApiParam,
  getTimeZoneApiParam,
  getTriggersApiParam,
} from "components/PowerScheduleForm/utils";
import PowerScheduleService, { type PowerScheduleApiParams } from "services/PowerScheduleService";
import { getPowerScheduleDetailsUrl } from "urls";

const EditPowerScheduleContainer = () => {
  const navigate = useNavigate();
  const { powerScheduleId } = useParams() as { powerScheduleId: string };

  const { useGet, useUpdate } = PowerScheduleService();

  const { powerSchedule, isLoading: isGetLoading } = useGet(powerScheduleId);
  const { onUpdate, isLoading: isUpdateLoading } = useUpdate();

  const onSubmit = (formData: FormValues) => {
    const data: Partial<PowerScheduleApiParams> = {
      name: getNameApiParam(formData),
      timezone: getTimeZoneApiParam(formData),
      start_date: getStartDateApiParam(formData),
      end_date: getEndDateApiParam(formData),
      triggers: getTriggersApiParam(formData),
    };

    onUpdate(powerScheduleId, data).then(() => navigate(getPowerScheduleDetailsUrl(powerScheduleId)));
  };

  const onCancel = () => navigate(getPowerScheduleDetailsUrl(powerScheduleId));

  return (
    <EditPowerSchedule
      powerSchedule={powerSchedule}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoadingProps={{
        isSubmitLoading: isUpdateLoading,
        isGetDataLoading: isGetLoading,
      }}
    />
  );
};

export default EditPowerScheduleContainer;
