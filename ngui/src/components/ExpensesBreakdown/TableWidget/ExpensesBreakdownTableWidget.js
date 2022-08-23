import React from "react";
import ListAltOutlinedIcon from "@mui/icons-material/ListAltOutlined";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ExpensesBreakdownTable from "components/ExpensesBreakdown/Table";
import WrapperCard from "components/WrapperCard";
import { isEmpty, sortObjects } from "utils/arrays";
import { EXPENSES_FILTERBY_TYPES } from "utils/constants";
import { percentXofY } from "utils/math";

const CLOUD = "cloud";
const POOL = "pool";
const SERVICE = "service";
const REGION = "region";
const OWNER = "owner";
const RESOURCE_TYPE = "resourceType";

const getTableWrapperCardTitleName = (filterBy) =>
  ({
    [EXPENSES_FILTERBY_TYPES.POOL]: POOL,
    [EXPENSES_FILTERBY_TYPES.CLOUD]: CLOUD,
    [EXPENSES_FILTERBY_TYPES.EMPLOYEE]: OWNER,
    [EXPENSES_FILTERBY_TYPES.SERVICE]: SERVICE,
    [EXPENSES_FILTERBY_TYPES.REGION]: REGION,
    [EXPENSES_FILTERBY_TYPES.RESOURCE_TYPE]: RESOURCE_TYPE
  }[filterBy]);

const getTableEmptyMessageId = (filterBy) =>
  ({
    [EXPENSES_FILTERBY_TYPES.POOL]: "noPools",
    [EXPENSES_FILTERBY_TYPES.CLOUD]: "noDataSources",
    [EXPENSES_FILTERBY_TYPES.SERVICE]: "noServices",
    [EXPENSES_FILTERBY_TYPES.REGION]: "noRegions",
    [EXPENSES_FILTERBY_TYPES.EMPLOYEE]: "noOwners",
    [EXPENSES_FILTERBY_TYPES.RESOURCE_TYPE]: "noResourceTypes"
  }[filterBy]);

const getExpensesTableData = ({ filteredBreakdown, totalExpenses, urlGetter, colorsMap }) =>
  sortObjects({ array: filteredBreakdown, field: "total" }).map((value) => ({
    percent: percentXofY(value.total, totalExpenses),
    link: urlGetter(value.id, value.type),
    color: colorsMap[value.name],
    ...value
  }));

const ExpensesBreakdownTableWidget = ({
  filteredBreakdown,
  colorsMap,
  total,
  filterBy,
  isLoading,
  getEntityExpensesUrl,
  onTitleButtonClick,
  onRowActionClick,
  startDateTimestamp,
  endDateTimestamp
}) => {
  const title = (
    <FormattedMessage
      id="summaryBy"
      values={{
        name: getTableWrapperCardTitleName(filterBy)
      }}
    />
  );

  const tableOptions = {
    data: getExpensesTableData({
      filteredBreakdown,
      totalExpenses: total,
      urlGetter: getEntityExpensesUrl,
      colorsMap
    }),
    localization: {
      emptyMessageId: getTableEmptyMessageId(filterBy)
    },
    rowActions: [
      {
        key: "showResources",
        tooltipMessageId: "showResources",
        onClick: (rowData) => {
          onRowActionClick(rowData);
        },
        icon: <ListAltOutlinedIcon />
      }
    ]
  };

  return (
    <WrapperCard
      needAlign
      title={title}
      titleButton={
        !isEmpty(filteredBreakdown)
          ? {
              type: "icon",
              tooltip: {
                title: <FormattedMessage id="showResources" />
              },
              buttonProps: {
                icon: <ListAltOutlinedIcon />,
                isLoading,
                onClick: onTitleButtonClick
              }
            }
          : null
      }
    >
      <ExpensesBreakdownTable
        data={tableOptions.data}
        localization={tableOptions.localization}
        isLoading={isLoading}
        rowActions={tableOptions.rowActions}
        filterBy={filterBy}
        startDateTimestamp={startDateTimestamp}
        endDateTimestamp={endDateTimestamp}
      />
    </WrapperCard>
  );
};

ExpensesBreakdownTableWidget.propTypes = {
  filteredBreakdown: PropTypes.array.isRequired,
  total: PropTypes.number.isRequired,
  filterBy: PropTypes.string.isRequired,
  getEntityExpensesUrl: PropTypes.func.isRequired,
  startDateTimestamp: PropTypes.number,
  endDateTimestamp: PropTypes.number,
  onTitleButtonClick: PropTypes.func,
  colorsMap: PropTypes.object,
  onRowActionClick: PropTypes.func,
  isLoading: PropTypes.bool
};

export default ExpensesBreakdownTableWidget;
