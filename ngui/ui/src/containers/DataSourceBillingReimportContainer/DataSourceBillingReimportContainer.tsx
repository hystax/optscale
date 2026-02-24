import DataSourceBillingReimportForm from "components/forms/DataSourceBillingReimportForm/DataSourceBillingReimportForm";
import { DataSourceDocument, useUpdateDataSourceMutation } from "graphql/__generated__/hooks/restapi";
import { getStartOfDayInUTCinSeconds } from "utils/datetime";

type DataSourceBillingReimportContainerProps = {
  dataSourceId: string;
  onSuccess: () => void;
};

const DataSourceBillingReimportContainer = ({ dataSourceId, onSuccess }: DataSourceBillingReimportContainerProps) => {
  const [updateDataSource, { loading }] = useUpdateDataSourceMutation();

  return (
    <DataSourceBillingReimportForm
      onSubmit={(formData) => {
        const importFrom = getStartOfDayInUTCinSeconds(formData.importFrom);

        return updateDataSource({
          variables: {
            dataSourceId,
            params: {
              lastImportAt: importFrom,
              lastImportModifiedAt: importFrom,
            },
          },
          refetchQueries: [DataSourceDocument],
        }).then(onSuccess);
      }}
      isSubmitLoading={loading}
    />
  );
};

export default DataSourceBillingReimportContainer;
