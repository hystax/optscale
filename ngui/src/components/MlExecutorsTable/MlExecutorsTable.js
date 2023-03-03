import React, { useMemo } from "react";
import { Typography } from "@mui/material";
import { Box } from "@mui/system";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import FormattedMoney from "components/FormattedMoney";
import QuestionMark from "components/QuestionMark";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { lastUsed, firstSeen } from "utils/columns";
import executor from "utils/columns/executor";

const MlExecutorsTable = ({ executors, isLoading }) => {
  const { isDemo } = useOrganizationInfo();

  const memoizedExecutors = useMemo(() => executors, [executors]);

  const columns = useMemo(
    () => [
      executor(),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_expenses">
            <FormattedMessage id="location" />
          </TextWithDataTestId>
        ),
        id: "location",
        cell: ({
          row: {
            original: { discovered, resource }
          }
        }) => {
          if (discovered) {
            const { cloud_account: { id, name, type } = {} } = resource ?? {};

            return <CloudLabel id={id} name={name} type={type} disableLink={isDemo} />;
          }

          return (
            <Box display="flex" alignItems="center">
              <Typography>
                <FormattedMessage id="unknown" />
              </Typography>
              <QuestionMark messageId="executorIsNotFoundInConnectedDataSources" />
            </Box>
          );
        }
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_expenses">
            <FormattedMessage id="expenses" />
          </TextWithDataTestId>
        ),
        id: "cost",
        accessorFn: (rowData) => rowData.resource?.total_cost,
        cell: ({ cell }) => <FormattedMoney value={cell.getValue()} />
      },
      lastUsed({ headerDataTestId: "lbl_last_used", accessorFn: (rowData) => rowData.resource?.last_seen }),
      firstSeen({ headerDataTestId: "lbl_first_seen", accessorFn: (rowData) => rowData.resource?.first_seen })
    ],
    [isDemo]
  );

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <Table
      data={memoizedExecutors}
      columns={columns}
      dataTestIds={{
        searchInput: "input_search"
      }}
      localization={{ emptyMessageId: "noExecutors" }}
    />
  );
};

MlExecutorsTable.propTypes = {
  executors: PropTypes.array.isRequired,
  isLoading: PropTypes.bool.isRequired
};

export default MlExecutorsTable;
