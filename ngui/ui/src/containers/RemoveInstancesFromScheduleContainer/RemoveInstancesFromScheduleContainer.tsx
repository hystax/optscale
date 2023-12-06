import RemoveInstancesFromSchedule from "components/RemoveInstancesFromSchedule";
import PowerScheduleService from "services/PowerScheduleService";

const RemoveInstancesFromScheduleContainer = ({ powerScheduleId, instancesToRemove, closeSideModal }) => {
  const { useRemoveInstancesFromSchedule } = PowerScheduleService();

  const { onRemove, isLoading } = useRemoveInstancesFromSchedule();

  const onDelete = () => {
    const instanceIdsToRemove = instancesToRemove.map(({ id }) => id);

    onRemove(powerScheduleId, instanceIdsToRemove).then(() => closeSideModal());
  };

  return (
    <RemoveInstancesFromSchedule
      instancesToRemove={instancesToRemove}
      onDelete={onDelete}
      onCancel={closeSideModal}
      isLoading={isLoading}
    />
  );
};

export default RemoveInstancesFromScheduleContainer;
