import React from "react";
import DataSourceSkusTable from "components/DataSourceSkusTable";
import DataSourceSkusService from "services/DataSourceSkusService";

const DataSourceSkusContainer = ({ dataSourceId, costModel }) => {
  const { useGet } = DataSourceSkusService();
  const { isLoading, skus, usedSkus } = useGet(dataSourceId);

  return (
    <DataSourceSkusTable
      usedSkus={usedSkus}
      skus={skus}
      dataSourceId={dataSourceId}
      isLoading={isLoading}
      costModel={costModel}
    />
  );
};

export default DataSourceSkusContainer;
