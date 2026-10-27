import DataSourceBillingReimportForm from "components/forms/DataSourceBillingReimportForm/DataSourceBillingReimportForm";
import { DataSourceDocument, useScheduleDataSourceReimportMutation } from "graphql/__generated__/hooks/restapi";
import { getStartOfDayInUTCinSeconds } from "utils/datetime";

type DataSourceBillingReimportContainerProps = {
  dataSourceId: string;
  onSuccess: () => void;
};

const DataSourceBillingReimportContainer = ({ dataSourceId, onSuccess }: DataSourceBillingReimportContainerProps) => {
  const [scheduleDataSourceReimport, { loading }] = useScheduleDataSourceReimportMutation();

  return (
    <DataSourceBillingReimportForm
      onSubmit={(formData) => {
        const importFrom = getStartOfDayInUTCinSeconds(formData.importFrom);

        return scheduleDataSourceReimport({
          variables: {
            dataSourceId,
            importFrom,
          },
          refetchQueries: [DataSourceDocument],
        }).then(onSuccess);
      }}
      isSubmitLoading={loading}
    />
  );
};

export default DataSourceBillingReimportContainer;
