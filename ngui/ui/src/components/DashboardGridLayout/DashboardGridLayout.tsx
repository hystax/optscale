import { type ReactNode } from "react";
import Grid from "@mui/material/Grid";
import ModeWrapper from "components/ModeWrapper";
import { OPTSCALE_MODE } from "utils/constants";
import { getSquareNodesStyle } from "utils/layouts";

type DashboardGridLayoutProps = {
  topResourcesExpensesCard: ReactNode;
  policiesCard: ReactNode;
  organizationExpenses: ReactNode;
  recommendationsCard: ReactNode;
  poolsRequiringAttentionCard: ReactNode;
  recentTasksCard: ReactNode;
};

const DashboardGridLayout = ({
  topResourcesExpensesCard,
  policiesCard,
  organizationExpenses,
  recommendationsCard,
  poolsRequiringAttentionCard,
  recentTasksCard
}: DashboardGridLayoutProps) => {
  const squareNodes = [
    { key: "organizationExpenses", node: organizationExpenses },
    {
      key: "topResourcesExpensesCard",
      node: topResourcesExpensesCard,
      mode: OPTSCALE_MODE.FINOPS
    },
    { key: "recommendationsCard", node: recommendationsCard },
    {
      key: "policiesCard",
      node: policiesCard,
      mode: OPTSCALE_MODE.FINOPS
    },
    {
      key: "poolsRequiringAttentionCard",
      node: poolsRequiringAttentionCard,
      mode: OPTSCALE_MODE.FINOPS
    },
    {
      key: "recentTasksCard",
      node: recentTasksCard,
      mode: OPTSCALE_MODE.MLOPS
    }
  ].filter(({ node }) => Boolean(node));

  return (
    <Grid container>
      {squareNodes.map(({ key, node, mode }, i) => (
        <ModeWrapper mode={mode} key={key}>
          <Grid item xs={12} lg={6} sx={getSquareNodesStyle(squareNodes.length, i)}>
            {node}
          </Grid>
        </ModeWrapper>
      ))}
    </Grid>
  );
};

export default DashboardGridLayout;
