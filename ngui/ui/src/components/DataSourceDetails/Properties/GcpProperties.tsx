import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { GCP_CNR } from "utils/constants";

const GcpProperties = ({ accountId, config }) => {
  const { billing_data: { dataset_name: datasetName, table_name: tableName, project_id: projectId } = {} } = config;

  return (
    <>
      <KeyValueLabel
        keyMessageId="GCPProjectId"
        value={accountId}
        dataTestIds={{
          key: `p_${GCP_CNR}_id`,
          value: `p_${GCP_CNR}_value`
        }}
      />
      <KeyValueLabel
        keyMessageId="billingDataDatasetName"
        value={datasetName}
        dataTestIds={{ key: "p_dataset_name_key", value: "p_dataset_name_value" }}
      />
      <KeyValueLabel
        keyMessageId="billingDataTableName"
        value={tableName}
        dataTestIds={{ key: "p_table_name_key", value: "p_table_name_value" }}
      />
      {projectId && (
        <KeyValueLabel
          keyMessageId="billingDataProjectId"
          value={projectId}
          dataTestIds={{ key: "p_project_id", value: "p_project_id" }}
        />
      )}
    </>
  );
};

export default GcpProperties;
