import { type ReactNode } from "react";
import Grid from "@mui/material/Grid";
import { useInnerBorders } from "hooks/useInnerBorders";

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

  const makeBorders = useInnerBorders({
    tileCount: squareNodes.length,
    columns: 2,
    borderStyle: "1px solid",
    lastChildBorderOnMobile: true
  });

  return (
    <Grid container>
      {squareNodes.map(({ key, node }, i) => (
        <Grid
          key={key}
          item
          xs={12}
          sm={6}
          sx={{
            ...makeBorders(i),
            borderColor: "divider"
          }}
        >
          {node}
        </Grid>
      ))}
    </Grid>
  );
};

export default DashboardGridLayout;
