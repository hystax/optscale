import React from "react";
import DataSourceNodes from "components/DataSourceNodes";

export default {
  title: "Components/DataSourceNodes"
};

const nodes = [
  {
    id: "495d1e45-3fdc-469a-bfbe-d618e84ebfac",
    cloud_account_id: "a9d91b08-17d0-4d8d-9c56-b591627c4399",
    name: "aks-agentpool-11122481-vmss000000",
    last_seen: 1626048069,
    flavor: "A m3.medium",
    provider_id:
      "azure:///subscriptions/7a26946b-0d60-4c01-adce-b6269d527407/resourceGroups/mc_pkozlov-kuber_pkozlov-k8s_westus/providers/Microsoft.Compute/virtualMachineScaleSets/aks-agentpool-11122481-vmss/virtualMachines/0",
    hourly_price: 0.14,
    provider: "azure_cnr",
    cpu: 1,
    memory: 2
  },
  {
    id: "41ab3548-fd23-4cda-bcfe-2aa4841f7879",
    cloud_account_id: "a9d91b08-17d0-4d8d-9c56-b591627c4399",
    name: "ip-192-168-57-15.us-west-2.compute.internal",
    last_seen: 1625835668,
    flavor: "B m3.medium",
    provider_id: "aws:///us-west-2a/i-0bfb49cf43789b008",
    hourly_price: 0.0416,
    provider: "aws_cnr",
    cpu: 2,
    memory: 4
  },
  {
    id: "111b3548-fd23-4cda-bcfe-2aa4841f7879",
    cloud_account_id: "11191b08-17d0-4d8d-9c56-b591627c4399",
    name: "ip-192-168-11-11.us-west-2.compute.internal",
    last_seen: 1625835668,
    flavor: "D m3.medium",
    provider_id: "aws:///us-west-2a/i-0bfb49cf43789b008",
    hourly_price: 0.0416,
    provider: "aws_cnr",
    cpu: 2,
    memory: 4
  },
  {
    id: "b6af91aa-8a4e-4c98-a4e6-3d36393e0969",
    cloud_account_id: "a9d91b08-17d0-4d8d-9c56-b591627c4399",
    name: "providerless name",
    last_seen: 1625835668,
    flavor: null,
    provider_id: null,
    hourly_price: 0.0416,
    provider: null,
    cpu: 1,
    memory: 2
  }
];

export const basic = () => (
  <DataSourceNodes
    cloudAccountId="cloudAccountId"
    costModel={{
      cpu_hourly_cost: 0.002,
      memory_hourly_cost: 0.001
    }}
    nodes={nodes}
  />
);
