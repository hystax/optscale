import { useMemo } from "react";
import Link from "@mui/material/Link";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CircleLabel from "components/CircleLabel";
import CloudLabel from "components/CloudLabel";
import ExpensesTableHeader from "components/ExpensesTableHeader";
import FormattedMoney from "components/FormattedMoney";
import IconButton from "components/IconButton";
import PoolLabel from "components/PoolLabel";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { FORMATTED_MONEY_TYPES, EXPENSES_FILTERBY_TYPES } from "utils/constants";

const getNameCellContentGetter = (filterBy) => {
  const getNameLabel = ({ link, name }) =>
    link ? (
      <Link to={link} component={RouterLink}>
        {name}
      </Link>
    ) : (
      name
    );

  const getDataSourceNameCellContent = (original) => <CloudLabel label={getNameLabel(original)} type={original.type} />;

  const getPoolNameCellContent = (original) => <PoolLabel type={original.purpose} label={getNameLabel(original)} />;

  const getDefaultSourceNameCellContent = (original) => getNameLabel(original);

  return (
    {
      [EXPENSES_FILTERBY_TYPES.CLOUD]: getDataSourceNameCellContent,
      [EXPENSES_FILTERBY_TYPES.POOL]: getPoolNameCellContent
    }[filterBy] || getDefaultSourceNameCellContent
  );
};

const renderNameCell = (row, filterBy) => {
  const { original } = row;

  const getContent = getNameCellContentGetter(filterBy);
  const content = getContent(original);

  return original.total ? <CircleLabel figureColor={original.color} textFirst={false} label={content} /> : content;
};

const ExpensesBreakdownTable = ({
  data = [],
  rowActions = [],
  localization,
  filterBy,
  isLoading = false,
  startDateTimestamp,
  endDateTimestamp
}) => {
  const tableData = useMemo(() => data, [data]);
  const columns = useMemo(
    () => [
      {
        accessorKey: "name",
        header: <FormattedMessage id="name" />,
        cell: ({ row }) => renderNameCell(row, filterBy)
      },
      {
        accessorKey: "total",
        header: <ExpensesTableHeader startDateTimestamp={startDateTimestamp} endDateTimestamp={endDateTimestamp} />,
        cell: ({ cell }) => <FormattedMoney value={cell.getValue()} type={FORMATTED_MONEY_TYPES.COMMON} />,
        defaultSort: "desc"
      },
      {
        accessorKey: "percent",
        header: <FormattedMessage id="percent" />,
        cell: ({ cell }) => <FormattedNumber value={cell.getValue()} format="percentage" />
      },
      {
        id: "actions",
        header: <FormattedMessage id="actions" />,
        cell: ({ row: { original = {} } }) =>
          rowActions.map(({ key, tooltipMessageId, onClick, icon }) => (
            <IconButton
              key={key}
              onClick={(event) => onClick(original, event)}
              icon={icon}
              tooltip={{
                show: true,
                value: <FormattedMessage id={tooltipMessageId} />
              }}
            />
          )),
        enableSorting: false
      }
    ],
    [endDateTimestamp, filterBy, rowActions, startDateTimestamp]
  );

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <Table data={tableData} columns={columns} localization={localization} pageSize={50} />
  );
};

export default ExpensesBreakdownTable;
