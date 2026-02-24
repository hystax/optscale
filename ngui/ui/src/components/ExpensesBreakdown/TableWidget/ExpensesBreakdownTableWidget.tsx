import ListAltOutlinedIcon from "@mui/icons-material/ListAltOutlined";
import { FormattedMessage } from "react-intl";
import ExpensesBreakdownTable from "components/ExpensesBreakdown/Table";
import IconButton from "components/IconButton";
import Tooltip from "components/Tooltip";
import { isEmptyArray, sortObjects } from "utils/arrays";
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
    [EXPENSES_FILTERBY_TYPES.RESOURCE_TYPE]: RESOURCE_TYPE,
  })[filterBy];

const getTableEmptyMessageId = (filterBy) =>
  ({
    [EXPENSES_FILTERBY_TYPES.POOL]: "noPoolExpenses",
    [EXPENSES_FILTERBY_TYPES.CLOUD]: "noDataSourceExpenses",
    [EXPENSES_FILTERBY_TYPES.SERVICE]: "noServiceExpenses",
    [EXPENSES_FILTERBY_TYPES.REGION]: "noRegionExpenses",
    [EXPENSES_FILTERBY_TYPES.EMPLOYEE]: "noOwnerExpenses",
    [EXPENSES_FILTERBY_TYPES.RESOURCE_TYPE]: "noResourceTypeExpenses",
  })[filterBy];

const getExpensesTableData = ({ filteredBreakdown, totalExpenses, urlGetter, colorsMap }) =>
  sortObjects({ array: filteredBreakdown, field: "total" }).map((value) => ({
    percent: percentXofY(value.total, totalExpenses),
    link: urlGetter(value.id, value.type),
    color: colorsMap[value.name],
    ...value,
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
  endDateTimestamp,
}) => {
  const title = (
    <FormattedMessage
      id="summaryBy"
      values={{
        name: getTableWrapperCardTitleName(filterBy),
      }}
    />
  );

  const tableOptions = {
    data: getExpensesTableData({
      filteredBreakdown,
      totalExpenses: total,
      urlGetter: getEntityExpensesUrl,
      colorsMap,
    }),
    localization: {
      emptyMessageId: getTableEmptyMessageId(filterBy),
    },
    rowActions: [
      {
        key: "showResources",
        tooltipMessageId: "showResources",
        onClick: (rowData) => {
          onRowActionClick(rowData);
        },
        icon: <ListAltOutlinedIcon />,
      },
    ],
  };

  return (
    <>
      {title}
      {!isEmptyArray(filteredBreakdown) ? (
        <Tooltip title={<FormattedMessage id="showResources" />}>
          <IconButton icon={<ListAltOutlinedIcon />} isLoading={isLoading} onClick={onTitleButtonClick} />
        </Tooltip>
      ) : null}
      <ExpensesBreakdownTable
        data={tableOptions.data}
        localization={tableOptions.localization}
        isLoading={isLoading}
        rowActions={tableOptions.rowActions}
        filterBy={filterBy}
        startDateTimestamp={startDateTimestamp}
        endDateTimestamp={endDateTimestamp}
      />
    </>
  );
};

export default ExpensesBreakdownTableWidget;
