import MlExecutorsTable from "components/MlExecutorsTable";
import { useIsOptScaleCapabilityEnabled } from "hooks/useIsOptScaleCapabilityEnabled";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import MlExecutorsService from "services/MlExecutorsService";
import { OPTSCALE_CAPABILITY } from "utils/constants";
import { inDateRange, secondsToMilliseconds } from "utils/datetime";

const MlExecutorsContainer = ({ dateRange }) => {
  const getFilteredExecutors = (executors) =>
    executors.filter(({ last_used: lastUsed }) => inDateRange(dateRange, secondsToMilliseconds(lastUsed)));

  const { organizationId } = useOrganizationInfo();

  const { useGet } = MlExecutorsService();
  const { isLoading, executors } = useGet({
    organizationId,
  });

  const isFinOpsEnabled = useIsOptScaleCapabilityEnabled(OPTSCALE_CAPABILITY.FINOPS);

  return <MlExecutorsTable executors={getFilteredExecutors(executors)} isLoading={isLoading} withExpenses={isFinOpsEnabled} />;
};

export default MlExecutorsContainer;
