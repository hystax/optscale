import React, { useMemo } from "react";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
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
        accessor: "name",
        Header: <FormattedMessage id="name" />,
        Cell: ({ row }) => renderNameCell(row, filterBy)
      },
      {
        accessor: "total",
        Header: <ExpensesTableHeader startDateTimestamp={startDateTimestamp} endDateTimestamp={endDateTimestamp} />,
        Cell: ({ cell: { value: total } }) => <FormattedMoney value={total} type={FORMATTED_MONEY_TYPES.COMMON} />,
        defaultSort: "desc"
      },
      {
        accessor: "percent",
        Header: <FormattedMessage id="percent" />,
        Cell: ({ cell: { value: percent } }) => <FormattedNumber value={percent} format="percentage" />
      },
      {
        id: "actions",
        Header: <FormattedMessage id="actions" />,
        Cell: ({ row: { original = {} } }) =>
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
        disableSortBy: true
      }
    ],
    [endDateTimestamp, filterBy, rowActions, startDateTimestamp]
  );

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <Table data={tableData} columns={columns} localization={localization} />
  );
};

ExpensesBreakdownTable.propTypes = {
  filterBy: PropTypes.string.isRequired,
  startDateTimestamp: PropTypes.number,
  endDateTimestamp: PropTypes.number,
  data: PropTypes.array,
  rowActions: PropTypes.array,
  localization: PropTypes.object,
  isLoading: PropTypes.bool
};

export default ExpensesBreakdownTable;
