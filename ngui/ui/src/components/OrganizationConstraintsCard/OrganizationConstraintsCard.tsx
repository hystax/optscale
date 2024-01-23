import { useMemo } from "react";
import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import WrapperCard from "components/WrapperCard";
import { ANOMALIES, QUOTAS_AND_BUDGETS, TAGGING_POLICIES } from "urls";
import { organizationConstraintName, organizationConstraintStatus } from "utils/columns";
import { isAnomalyConstraint, isQuotasAndBudgetsConstraint, isTaggingPolicyConstraint } from "utils/organizationConstraints";

const ConstraintsTable = ({ constraints }) => {
  const tableData = useMemo(() => constraints, [constraints]);

  const columns = useMemo(
    () => [
      organizationConstraintName(),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_type">
            <FormattedMessage id="type" />
          </TextWithDataTestId>
        ),
        accessorKey: "type",
        cell: ({ cell }) => {
          const constraintType = cell.getValue();

          switch (true) {
            case isAnomalyConstraint(constraintType): {
              return (
                <Link to={ANOMALIES} component={RouterLink}>
                  <FormattedMessage id="anomaly" />
                </Link>
              );
            }
            case isQuotasAndBudgetsConstraint(constraintType): {
              return (
                <Link to={QUOTAS_AND_BUDGETS} component={RouterLink}>
                  <FormattedMessage id="quota/Budget" />
                </Link>
              );
            }
            case isTaggingPolicyConstraint(constraintType): {
              return (
                <Link to={TAGGING_POLICIES} component={RouterLink}>
                  <FormattedMessage id="tagging" />
                </Link>
              );
            }
            default:
              return null;
          }
        }
      },
      organizationConstraintStatus()
    ],
    []
  );

  return (
    <Table
      enableSearchQueryParam={false}
      enablePaginationQueryParam={false}
      data={tableData}
      columns={columns}
      localization={{ emptyMessageId: "noPolicies" }}
      pageSize={5}
    />
  );
};

const OrganizationConstraintsCard = ({ constraints, isLoading = false }) => (
  <WrapperCard
    needAlign
    title={<FormattedMessage id="policyViolations" />}
    dataTestIds={{
      wrapper: "block_policies_violations",
      title: "lbl_policies_violations"
    }}
    elevation={0}
  >
    {isLoading ? <TableLoader columnsCounter={1} /> : <ConstraintsTable constraints={constraints} />}
  </WrapperCard>
);

export default OrganizationConstraintsCard;
