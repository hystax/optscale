import ResourceCountBreakdown from "components/ResourceCountBreakdown";
import { useBreakdownBy } from "hooks/useBreakdownBy";
import ResourcesCountBreakdownService from "services/ResourcesCountBreakdownService";
import { DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME } from "urls";

const ResourceCountBreakdownContainer = ({ requestParams }) => {
  const { useGet } = ResourcesCountBreakdownService();

  const [{ value: breakdownByValue }, onBreakdownByChange] = useBreakdownBy({
    queryParamName: DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME,
  });

  const { isGetResourceCountBreakdownLoading, data } = useGet(breakdownByValue, requestParams);

  return (
    <ResourceCountBreakdown
      resourceCountBreakdown={data}
      breakdownByValue={breakdownByValue}
      onBreakdownByChange={onBreakdownByChange}
      isLoading={isGetResourceCountBreakdownLoading}
      showTable
    />
  );
};

export default ResourceCountBreakdownContainer;
