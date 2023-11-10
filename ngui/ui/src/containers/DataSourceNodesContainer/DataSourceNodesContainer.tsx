import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getDataSourceNodes } from "api";
import { GET_DATA_SOURCE_NODES } from "api/restapi/actionTypes";
import DataSourceNodes from "components/DataSourceNodes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

const DataSourceNodesContainer = ({ cloudAccountId, costModel = {} }) => {
  const dispatch = useDispatch();

  const { isLoading, shouldInvoke } = useApiState(GET_DATA_SOURCE_NODES, cloudAccountId);

  const { apiData: { nodes = [] } = {} } = useApiData(GET_DATA_SOURCE_NODES);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getDataSourceNodes(cloudAccountId));
    }
  }, [cloudAccountId, dispatch, shouldInvoke]);

  return <DataSourceNodes nodes={nodes} costModel={costModel} cloudAccountId={cloudAccountId} isLoading={isLoading} />;
};

export default DataSourceNodesContainer;
