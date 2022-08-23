import React from "react";
import Grid from "@mui/material/Grid";
import { SPACING_2 } from "utils/layouts";

const DashboardGridLayout = ({
  topResourcesExpensesCard,
  environmentsCard,
  organizationExpenses,
  recommendationsCard,
  myTasksCard
}) => {
  const squareNodes = [
    { key: "organizationExpenses", node: organizationExpenses },
    {
      key: "topResourcesExpensesCard",
      node: topResourcesExpensesCard
    },
    { key: "recommendationsCard", node: recommendationsCard },
    {
      key: "environmentsCard",
      node: environmentsCard
    }
  ].filter(({ node }) => Boolean(node));

  return (
    <Grid container spacing={SPACING_2}>
      {squareNodes.map(({ key, node }) => (
        <Grid key={key} item xs={12} sm={6}>
          {node}
        </Grid>
      ))}
      <Grid item xs={12}>
        {myTasksCard}
      </Grid>
    </Grid>
  );
};

export default DashboardGridLayout;
