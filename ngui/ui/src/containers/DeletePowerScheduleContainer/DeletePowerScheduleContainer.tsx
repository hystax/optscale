import { useNavigate } from "react-router-dom";
import DeletePowerSchedule from "components/DeletePowerSchedule";
import PowerScheduleService from "services/PowerScheduleService";
import { POWER_SCHEDULES } from "urls";

const DeletePowerScheduleContainer = ({ id, name, closeSideModal }) => {
  const navigate = useNavigate();

  const { useDelete } = PowerScheduleService();
  const { onDelete, isLoading } = useDelete();

  const onSubmit = () =>
    onDelete(id).then(() => {
      closeSideModal();
      navigate(POWER_SCHEDULES);
    });

  return <DeletePowerSchedule onSubmit={onSubmit} name={name} onCancel={closeSideModal} isLoading={isLoading} />;
};

export default DeletePowerScheduleContainer;
