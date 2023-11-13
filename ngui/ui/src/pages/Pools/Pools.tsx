import Mocked, { MESSAGE_TYPES } from "components/Mocked";
import PoolsOverview from "components/PoolsOverview";
import { PageMockupContextProvider } from "contexts/PageMockupContext";
import PoolsService, { dataMocked } from "services/PoolsService";
import { isEmpty } from "utils/arrays";

const Pools = () => {
  const { useGet } = PoolsService();
  const { isLoading, data, isGetPoolAllowedActionsLoading, isDataReady } = useGet();

  return (
    <Mocked
      mock={
        <PageMockupContextProvider>
          <PoolsOverview data={dataMocked} isLoading={false} isDataReady isGetPoolAllowedActionsLoading={false} />
        </PageMockupContextProvider>
      }
      backdropMessageType={MESSAGE_TYPES.POOLS}
      mockCondition={data.limit === 0 && data.parent_id === null && isEmpty(data.children)}
    >
      <PoolsOverview
        data={data}
        isLoading={isLoading}
        isDataReady={isDataReady}
        isGetPoolAllowedActionsLoading={isGetPoolAllowedActionsLoading}
      />
    </Mocked>
  );
};

export default Pools;
