import PowerSchedules from "components/PowerSchedules";
import PowerScheduleService from "services/PowerScheduleService";

const PowerSchedulesContainer = () => {
  const { useGetAll, useUpdate } = PowerScheduleService();
  const { isLoading: isGetPowerSchedulesLoading, powerSchedules } = useGetAll();

  const { isLoading: isUpdatePowerScheduleLoading, onUpdate, updatingEntityId } = useUpdate();

  const onActivate = (powerScheduleId) => onUpdate(powerScheduleId, { enabled: true });
  const onDeactivate = (powerScheduleId) => onUpdate(powerScheduleId, { enabled: false });

  return (
    <PowerSchedules
      isLoadingProps={{
        isGetPowerSchedulesLoading,
        isUpdatePowerScheduleLoading
      }}
      powerSchedules={powerSchedules}
      updatingEntityId={updatingEntityId}
      onActivate={onActivate}
      onDeactivate={onDeactivate}
    />
  );
};

export default PowerSchedulesContainer;
