import { type ReactNode } from "react";
import Grid from "@mui/material/Grid";
import CapabilityWrapper from "components/CapabilityWrapper";
import { OPTSCALE_CAPABILITY } from "utils/constants";
import { getSquareNodesStyle } from "utils/layouts";

type DashboardGridLayoutProps = {
  topResourcesExpensesCard: ReactNode;
  policiesCard: ReactNode;
  organizationExpenses: ReactNode;
  recommendationsCard: ReactNode;
  poolsRequiringAttentionCard: ReactNode;
  recentTasksCard: ReactNode;
  recentModelsCard: ReactNode;
};

const DashboardGridLayout = ({
  topResourcesExpensesCard,
  policiesCard,
  organizationExpenses,
  recommendationsCard,
  poolsRequiringAttentionCard,
  recentTasksCard,
  recentModelsCard,
}: DashboardGridLayoutProps) => {
  const squareNodes = [
    {
      key: "recentModelsCard",
      node: recentModelsCard,
      capability: OPTSCALE_CAPABILITY.MLOPS,
    },
    {
      key: "recentTasksCard",
      node: recentTasksCard,
      capability: OPTSCALE_CAPABILITY.MLOPS,
    },
    { key: "organizationExpenses", node: organizationExpenses },
    {
      key: "topResourcesExpensesCard",
      node: topResourcesExpensesCard,
      capability: OPTSCALE_CAPABILITY.FINOPS,
    },
    { key: "recommendationsCard", node: recommendationsCard },
    {
      key: "policiesCard",
      node: policiesCard,
      capability: OPTSCALE_CAPABILITY.FINOPS,
    },
    {
      key: "poolsRequiringAttentionCard",
      node: poolsRequiringAttentionCard,
      capability: OPTSCALE_CAPABILITY.FINOPS,
    },
  ].filter(({ node }) => Boolean(node));

  return (
    <Grid container>
      {squareNodes.map(({ key, node, capability }, i) => (
        <CapabilityWrapper capability={capability} key={key}>
          <Grid item xs={12} lg={6} sx={getSquareNodesStyle(squareNodes.length, i)}>
            {node}
          </Grid>
        </CapabilityWrapper>
      ))}
    </Grid>
  );
};

export default DashboardGridLayout;
