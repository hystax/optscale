import { type ReactNode } from "react";
import Grid from "@mui/material/Grid";
import { getSquareNodesStyle } from "utils/layouts";

type DashboardGridLayoutProps = {
  topResourcesExpensesCard: ReactNode;
  policiesCard: ReactNode;
  organizationExpenses: ReactNode;
  recommendationsCard: ReactNode;
  poolsRequiringAttentionCard: ReactNode;
};

const DashboardGridLayout = ({
  topResourcesExpensesCard,
  policiesCard,
  organizationExpenses,
  recommendationsCard,
  poolsRequiringAttentionCard
}: DashboardGridLayoutProps) => {
  const squareNodes = [
    { key: "organizationExpenses", node: organizationExpenses },
    {
      key: "topResourcesExpensesCard",
      node: topResourcesExpensesCard
    },
    { key: "recommendationsCard", node: recommendationsCard },
    {
      key: "policiesCard",
      node: policiesCard
    },
    {
      key: "poolsRequiringAttentionCard",
      node: poolsRequiringAttentionCard
    }
  ].filter(({ node }) => Boolean(node));

  return (
    <Grid container>
      {squareNodes.map(({ key, node }, i) => (
        <Grid key={key} item xs={12} lg={6} sx={getSquareNodesStyle(squareNodes.length, i)}>
          {node}
        </Grid>
      ))}
    </Grid>
  );
};

export default DashboardGridLayout;
