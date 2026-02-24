import { ReactNode } from "react";
import { Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import SummaryList from "components/SummaryList";
import {
  ALIBABA_CNR,
  AWS_CNR,
  AZURE_CNR,
  AZURE_TENANT,
  GCP_CNR,
  KUBERNETES_CNR,
  NEBIUS,
  DATABRICKS,
  GCP_TENANT,
} from "utils/constants";
import { formatUTC } from "utils/datetime";
import { SPACING_2 } from "utils/layouts";
import { ChildrenList } from "./ChildrenList";
import { K8sHelp } from "./Help";
import {
  AlibabaProperties,
  AwsProperties,
  AzureProperties,
  NebiusProperties,
  GcpProperties,
  K8sProperties,
  DatabricksProperties,
} from "./Properties";
import { K8sPropertiesProps } from "./Properties/types";
import type { ConfigMap, DataSourceDetailsProps, PropertiesMap } from "./types";

const propertiesMap: PropertiesMap = {
  [AWS_CNR]: AwsProperties,
  [AZURE_CNR]: AzureProperties,
  [AZURE_TENANT]: AzureProperties,
  [GCP_CNR]: GcpProperties,
  [GCP_TENANT]: GcpProperties,
  [ALIBABA_CNR]: AlibabaProperties,
  [KUBERNETES_CNR]: K8sProperties,
  [NEBIUS]: NebiusProperties,
  [DATABRICKS]: DatabricksProperties,
};

const renderHelpMap = (id: string, config: ConfigMap) => ({
  [KUBERNETES_CNR]: <K8sHelp dataSourceId={id} user={(config as K8sPropertiesProps["config"]).user} />,
  [AWS_CNR]: null,
  [AZURE_CNR]: null,
  [AZURE_TENANT]: null,
  [GCP_CNR]: null,
  [GCP_TENANT]: null,
  [ALIBABA_CNR]: null,
  [NEBIUS]: null,
  [DATABRICKS]: null,
});

const childrenListMap = (id: string) => ({
  [AZURE_TENANT]: <ChildrenList parentId={id} />,
  [GCP_TENANT]: <ChildrenList parentId={id} />,
  [KUBERNETES_CNR]: null,
  [AWS_CNR]: null,
  [AZURE_CNR]: null,
  [GCP_CNR]: null,
  [ALIBABA_CNR]: null,
  [NEBIUS]: null,
  [DATABRICKS]: null,
});

const DataSourceDetails = ({ id, accountId, parentId, type, createdAt, config = {} }: DataSourceDetailsProps) => {
  const Properties = propertiesMap[type];
  const renderHelp: ReactNode = renderHelpMap(id, config)[type];
  const childrenList: ReactNode = childrenListMap(id)[type];

  return (
    <Stack spacing={SPACING_2}>
      {Properties && (
        <div>
          <SummaryList
            titleMessage={<FormattedMessage id="properties" />}
            items={
              <Properties config={config} createdAt={formatUTC(createdAt)} accountId={accountId} id={id} parentId={parentId} />
            }
          />
        </div>
      )}
      {renderHelp && <div>{renderHelp}</div>}
      {childrenList && <div>{childrenList}</div>}
    </Stack>
  );
};

export default DataSourceDetails;
