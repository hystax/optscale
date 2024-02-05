import { type ReactNode } from "react";
import { useDataSources } from "hooks/useDataSources";
import ItemContent from "../ItemContent";

type ItemContentWithDataSourceIconProps = {
  dataSourceType:
    | "aws_cnr"
    | "azure_cnr"
    | "azure_tenant"
    | "databricks"
    | "kubernetes_cnr"
    | "alibaba_cnr"
    | "environment"
    | "gcp_cnr"
    | "nebius";
  children: ReactNode;
};

const ItemContentWithDataSourceIcon = ({ dataSourceType, children }: ItemContentWithDataSourceIconProps) => {
  const { icon } = useDataSources(dataSourceType);

  return (
    <ItemContent
      icon={{
        IconComponent: icon
      }}
    >
      {children}
    </ItemContent>
  );
};

export default ItemContentWithDataSourceIcon;
