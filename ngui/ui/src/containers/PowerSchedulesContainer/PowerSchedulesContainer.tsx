import PowerSchedules from "components/PowerSchedules";
import PowerScheduleService from "services/PowerScheduleService";

const PowerSchedulesContainer = () => {
  const { useGetAll, useUpdate } = PowerScheduleService();
  const { isLoading: isGetPowerSchedulesLoading, powerSchedules } = useGetAll();

  const { isLoading: isUpdatePowerScheduleLoading, onUpdate, updatingEntityId } = useUpdate();

  return (
    <PowerSchedules
      isLoadingProps={{
        isGetPowerSchedulesLoading,
        isUpdatePowerScheduleLoading
      }}
      powerSchedules={powerSchedules}
      updatingEntityId={updatingEntityId}
      onActivate={(powerScheduleId) => onUpdate(powerScheduleId, { enabled: true })}
      onDeactivate={(powerScheduleId) => onUpdate(powerScheduleId, { enabled: false })}
    />
  );
};

export default PowerSchedulesContainer;
