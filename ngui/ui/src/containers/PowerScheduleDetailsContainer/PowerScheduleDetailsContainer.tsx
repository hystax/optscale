import { useEffect } from "react";
import { useParams } from "react-router-dom";
import PowerScheduleDetails from "components/PowerScheduleDetails";
import PowerScheduleService from "services/PowerScheduleService";

const REFRESH_INTERVAL_MS = 60_000;

const PowerScheduleDetailsContainer = () => {
  const { powerScheduleId } = useParams() as { powerScheduleId: string };

  const { useGet, useGetManually, useUpdate, useRunNow } = PowerScheduleService();

  const { isLoading: isGetPowerScheduleLoading, powerSchedule } = useGet(powerScheduleId);
  const { isLoading: isUpdatePowerScheduleLoading, onUpdate } = useUpdate();
  const { refresh } = useGetManually(powerScheduleId);
  const { onRunNow, isLoading: isRunNowLoading } = useRunNow();

  useEffect(() => {
    const id = setInterval(refresh, REFRESH_INTERVAL_MS);
    return () => clearInterval(id);
  }, [refresh]);

  const onActivate = () => onUpdate(powerScheduleId, { enabled: true });
  const onDeactivate = () => onUpdate(powerScheduleId, { enabled: false });
  const handleRunNow = (action: "power_on" | "power_off") =>
    onRunNow(powerScheduleId, action).then(() => refresh());

  return (
    <PowerScheduleDetails
      isLoadingProps={{
        isGetPowerScheduleLoading,
        isUpdatePowerScheduleLoading,
        isRunNowLoading,
      }}
      powerSchedule={powerSchedule}
      onActivate={onActivate}
      onDeactivate={onDeactivate}
      onRefresh={refresh}
      onRunNow={handleRunNow}
    />
  );
};

export default PowerScheduleDetailsContainer;
