import React from "react";
import { number } from "@storybook/addon-knobs";
import { FormattedMessage } from "react-intl";
import Grid from "@mui/material/Grid";
import WrapperCard from "components/WrapperCard";
import CloudExpensesChart from "components/CloudExpensesChart";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/CloudExpensesChart`
};

const cloudAccounts = [
  {
    details: { tracked: 768, last_month_cost: 559.7434027942, cost: 141.0194095445, forecast: 546.45 },
    type: "aws_cnr",
    name: "AWS",
    organization_id: "9eb8d5fe-b5a8-4c6f-899a-bf761109d11f",
    created_at: 1605527921,
    last_import_at: 1607410812,
    process_recommendations: true,
    auto_import: true,
    last_import_modified_at: 1607382770,
    import_period: 1,
    deleted_at: 0,
    config: {
      access_key_id: "AKIAQUWY5LJ4X2L4DXFN",
      config_scheme: "create_report",
      region_name: "eu-central-1",
      bucket_prefix: "reports",
      bucket_name: "yv-report-bucket",
      linked: false,
      report_name: "yv_report"
    },
    account_id: "044478323321",
    id: "3d4236be-e167-4801-86ff-944943a9ae6f"
  },
  {
    details: { tracked: 22, last_month_cost: 85.1889819768111, cost: 5.958978755733334, forecast: 23.09 },
    type: "azure_cnr",
    name: "EK_azure_connection",
    organization_id: "9eb8d5fe-b5a8-4c6f-899a-bf761109d11f",
    created_at: 1595938251,
    last_import_at: 1607410823,
    process_recommendations: true,
    auto_import: true,
    last_import_modified_at: 0,
    import_period: 1,
    deleted_at: 0,
    config: {
      tenant: "28ac62fa-dc92-4770-bc5a-18d7005efe29",
      client_id: "a8529a01-fc44-44b1-8725-59196f91e1b9",
      subscription_id: "318bd278-e4ef-4230-9ab4-2ad6a29f578c"
    },
    account_id: "318bd278-e4ef-4230-9ab4-2ad6a29f578c",
    id: "31b0fdf7-cace-4dc9-9ec0-7ce66f983f6a"
  }
];

export const basic = () => <CloudExpensesChart cloudAccounts={cloudAccounts} pool={100} forecast={559} />;

export const loading = () => <CloudExpensesChart cloudAccounts={[]} pool={0} forecast={0} isLoading />;

export const withKnobs = () => (
  <WrapperCard title={<FormattedMessage id="summary" />}>
    <div>
      <p>percent = (forecast / pool) * 100</p>
      <p>Corner cases:</p>
      <ul>
        <li>{`pool = 0 & forecast = 0 => border color is "success"`}</li>
        <li>{`pool = 0 & forecast != 0 => border color is "error"`}</li>
        <li>{`pool != 0 & forecast = 0 => border color is "success"`}</li>
      </ul>
    </div>
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <CloudExpensesChart cloudAccounts={cloudAccounts} pool={number("pool", 123)} forecast={number("forecast", 321)} />
      </Grid>
    </Grid>
  </WrapperCard>
);
