import { useMemo } from "react";
import { Link } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import WrapperCard from "components/WrapperCard";
import { organizationConstraintName, organizationConstraintStatus } from "utils/columns";

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
        accessorKey: "typeMessageId",
        cell: ({
          row: {
            original: { typeMessageId, typeLink }
          }
        }) => (
          <Link to={typeLink} component={RouterLink}>
            <FormattedMessage id={typeMessageId} />
          </Link>
        )
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
