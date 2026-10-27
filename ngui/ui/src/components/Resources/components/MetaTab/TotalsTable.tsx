import { useMemo } from "react";
import { FormattedMessage, FormattedNumber, useIntl } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import TableComponent from "components/Table";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import TextWithDate from "components/TextWithDate";
import { FORMATTED_MONEY_TYPES, EMPTY_BREAKDOWN_KEY } from "utils/constants";
import { getMetaFormattedValue } from "utils/metadata";
import { TableLoadingWrapperProps, TotalsTableProps } from "./types";

const TotalsTable = ({ startDate, endDate, totals, metaName }: TotalsTableProps) => {
  const intl = useIntl();

  const tableData = useMemo(
    () =>
      Object.entries(totals).map(([key, datum]) => ({
        name: key,
        count: datum.count,
        cost: datum.cost,
      })),
    [totals]
  );

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        id: "name",
        accessorFn: (originalRow) => {
          if (originalRow.name === EMPTY_BREAKDOWN_KEY.NOT_SET) {
            return intl.formatMessage({ id: "(not set)" });
          }
          if (originalRow.name === EMPTY_BREAKDOWN_KEY.NULL) {
            return "null";
          }
          return getMetaFormattedValue(metaName, originalRow.name);
        },
        style: {
          maxWidth: "500px",
          overflowWrap: "anywhere",
        },
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_resource_count">
            <TextWithDate
              text={<FormattedMessage id="resourceCount" />}
              startDateTimestamp={startDate}
              endDateTimestamp={endDate}
            />
          </TextWithDataTestId>
        ),
        accessorKey: "count",
        cell: ({ cell }) => <FormattedNumber value={cell.getValue()} />,
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_expenses">
            <TextWithDate text={<FormattedMessage id="expenses" />} startDateTimestamp={startDate} endDateTimestamp={endDate} />
          </TextWithDataTestId>
        ),
        accessorKey: "cost",
        cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />,
        defaultSort: "desc",
      },
    ],
    [startDate, endDate, metaName, intl]
  );

  return (
    <TableComponent
      data={tableData}
      columns={columns}
      withSearch
      pageSize={50}
      enableSearchQueryParam
      enablePaginationQueryParam
    />
  );
};

const TableLoadingWrapper = ({ isLoading = false, ...rest }: TableLoadingWrapperProps) => {
  if (isLoading) {
    return <TableLoader showHeader />;
  }

  return <TotalsTable {...rest} />;
};

export default TableLoadingWrapper;
