import { useParams } from "react-router-dom";
import PowerScheduleDetails from "components/PowerScheduleDetails";
import PowerScheduleService from "services/PowerScheduleService";

const PowerScheduleDetailsContainer = () => {
  const { powerScheduleId } = useParams();

  const { useGet, useUpdate } = PowerScheduleService();

  const { isLoading: isGetPowerScheduleLoading, powerSchedule } = useGet(powerScheduleId);
  const { isLoading: isUpdatePowerScheduleLoading, onUpdate } = useUpdate(powerScheduleId);

  const onActivate = () => onUpdate(powerScheduleId, { enabled: true });
  const onDeactivate = () => onUpdate(powerScheduleId, { enabled: false });

  return (
    <PowerScheduleDetails
      isLoadingProps={{
        isGetPowerScheduleLoading,
        isUpdatePowerScheduleLoading
      }}
      powerSchedule={powerSchedule}
      onActivate={onActivate}
      onDeactivate={onDeactivate}
    />
  );
};

export default PowerScheduleDetailsContainer;
