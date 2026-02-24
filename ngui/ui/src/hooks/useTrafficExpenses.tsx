import { useCallback, useMemo, useState } from "react";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormattedMessage, useIntl } from "react-intl";
import FormattedDigitalUnit, { SI_UNITS } from "components/FormattedDigitalUnit";
import FormattedMoney from "components/FormattedMoney";
import { isEmptyArray } from "utils/arrays";
import { EXPENSES_MAP_OBJECT_TYPES, FORMATTED_MONEY_TYPES } from "utils/constants";
import {
  OTHER_LAT,
  OTHER_LON,
  EXTERNAL_NAME,
  INTER_CONTINENTAL_LAT,
  INTER_CONTINENTAL_LON,
  INTER_CONTINENTAL_NAME,
  INTER_REGION_LAT,
  INTER_REGION_LON,
  INTER_REGION_NAME,
  EXTERNAL_LAT,
  EXTERNAL_LON,
} from "utils/maps";

export const TABLE_SELECTION_STATE = Object.freeze({
  NOTHING_SELECTED: "NOTHING_SELECTED",
  SELECTION_ACTIVE: "SELECTION_ACTIVE",
});

const getTableData = (expenses, uniqueDestinations) =>
  uniqueDestinations
    .map((uniqueDestination) => {
      const filteredExpenses = expenses.filter((expense) => expense.from.name === uniqueDestination);
      const row = filteredExpenses.reduce(
        (resultObject, expense) => ({
          ...resultObject,
          [expense.to.name]: expense,
        }),
        {}
      );
      row.col_name = uniqueDestination;
      row.total_expenses = filteredExpenses.reduce((result, expense) => result + expense.cost, 0);
      row.total_usage = filteredExpenses.reduce((result, expense) => result + expense.usage, 0);
      return row;
    })
    .filter((row) => Object.keys(row).length > 3);

const OTHER_NAME = "Other";

const getMarkers = (expenses, uniqueDestinations, destinationsMap) => {
  const locations = uniqueDestinations.reduce((resultArray, uniqueDestination) => {
    const filteredExpenses = expenses
      .filter((expense) => expense.from.name === uniqueDestination)
      .sort((a, b) => b.cost - a.cost);

    const expense = expenses.find(
      ({ from, to }) => from.latitude && from.longitude && (from.name === uniqueDestination || to.name === uniqueDestination)
    );

    if (!expense) {
      return [...resultArray];
    }

    let latitude = OTHER_LAT;
    let longitude = OTHER_LON;
    if (expense.from.name === uniqueDestination) {
      latitude = expense.from.latitude;
      longitude = expense.from.longitude;
    } else if (expense.to.latitude && expense.to.longitude) {
      latitude = expense.to.latitude;
      longitude = expense.to.longitude;
    } else if (uniqueDestination === INTER_REGION_NAME) {
      latitude = INTER_REGION_LAT;
      longitude = INTER_REGION_LON;
    } else if (uniqueDestination === INTER_CONTINENTAL_NAME) {
      latitude = INTER_CONTINENTAL_LAT;
      longitude = INTER_CONTINENTAL_LON;
    } else if (uniqueDestination === EXTERNAL_NAME) {
      latitude = EXTERNAL_LAT;
      longitude = EXTERNAL_LON;
    }

    return [
      ...resultArray,
      {
        id: destinationsMap[uniqueDestination],
        originalId: uniqueDestination,
        latitude,
        longitude,
        summary: filteredExpenses.map((e) => ({
          original_from: e.from.name,
          original_to: e.to.name,
          mapped_from: destinationsMap[e.from.name],
          mapped_to: destinationsMap[e.to.name],
          cost: e.cost,
          usage: e.usage,
        })),
        name: destinationsMap[uniqueDestination],
        originalName: uniqueDestination,
        expenses: filteredExpenses,
        totalExpenses: filteredExpenses.reduce((result, e) => result + e.cost, 0),
        totalUsage: filteredExpenses.reduce((result, e) => result + e.usage, 0),
      },
    ];
  }, []);

  const accumulatedLocations = Object.values(
    locations.reduce((acc, curr) => {
      if (curr.id === OTHER_NAME) {
        return {
          ...acc,
          [OTHER_NAME]: {
            ...curr,
            expenses: [...(acc[OTHER_NAME]?.expenses || []), ...curr.expenses],
            summary: [...(acc[OTHER_NAME]?.summary || []), ...curr.summary],
            totalExpenses: (acc[OTHER_NAME]?.totalExpenses || 0) + curr.totalExpenses,
            totalUsage: (acc[OTHER_NAME]?.totalUsage || 0) + curr.totalUsage,
          },
        };
      }

      return {
        ...acc,
        [curr.id]: {
          ...curr,
        },
      };
    }, {})
  );

  const accumulatedFlows = Object.values(
    expenses
      .filter((expense) => expense.from.latitude && expense.from.longitude)
      .reduce((acc, curr) => {
        const sourceName = destinationsMap[curr.from.name];
        const targetName = destinationsMap[curr.to.name];

        const flowName = `${sourceName} -> ${targetName}`;

        if (targetName === OTHER_NAME) {
          return {
            ...acc,
            [flowName]: {
              ...curr,
              cost: (acc[flowName]?.cost || 0) + curr.cost,
              usage: (acc[flowName]?.usage || 0) + curr.usage,
              to: {
                name: OTHER_NAME,
              },
            },
          };
        }
        return {
          ...acc,
          [flowName]: {
            ...curr,
          },
        };
      }, {})
  );

  return {
    locations: accumulatedLocations,
    flows: accumulatedFlows,
    otherLocations: locations.filter((location) => location.latitude === OTHER_LAT && location.longitude === OTHER_LON),
    interRegion: locations.find((location) => location.name === INTER_REGION_NAME),
    interContinental: locations.find((location) => location.name === INTER_CONTINENTAL_NAME),
    externalLocation: locations.find((location) => location.name === EXTERNAL_NAME),
  };
};

const getColumns = ({
  uniqueToDestinations,
  onColumnHeaderClick,
  onRowHeaderClick,
  onCellClick,
  selectedColumns,
  tableData,
}) => {
  let columns = uniqueToDestinations.map((field) => ({
    header: (
      <Link component="button" onClick={() => onColumnHeaderClick(field)} color="inherit">
        <Typography variant="subtitle2" component="div">
          <strong>{field}</strong>
        </Typography>
      </Link>
    ),
    accessorKey: `${field}`,
    enableSorting: false,
    style: {
      whiteSpace: "nowrap",
    },
    cell: ({ cell }) => {
      const expense = cell.getValue();

      return (
        <Link component="button" onClick={() => onCellClick(expense)} color="inherit">
          <Typography variant="caption" component="div" align="left">
            <strong>
              <FormattedMoney value={expense.cost} type={FORMATTED_MONEY_TYPES.COMPACT} disableTooltip />{" "}
            </strong>
          </Typography>
          <Typography variant="caption" component="div" align="left">
            <FormattedDigitalUnit value={expense.usage} baseUnit={SI_UNITS.GIGABYTE} />
          </Typography>
        </Link>
      );
    },
  }));

  if (tableData.length === 1) {
    const rowValues = new Map(Object.values(tableData[0]).map((value) => [value?.to?.name, value.cost]));
    columns = columns
      .filter((column) => Object.keys(tableData[0]).includes(column.accessorKey))
      .sort((a, b) => rowValues.get(b.accessorKey) - rowValues.get(a.accessorKey));
  }

  if (!isEmptyArray(selectedColumns)) {
    columns = columns.filter((column) => selectedColumns.includes(column.accessorKey));
  }

  return [
    {
      id: "name_col",
      header: <FormattedMessage id="from/to" />,
      accessorKey: "col_name",
      enableSorting: false,
      style: {
        whiteSpace: "nowrap",
      },
      cell: ({ row: { original } }) => (
        <Link component="button" onClick={() => onRowHeaderClick(original.col_name)} color="inherit">
          <Typography variant="subtitle2" component="div" align="left">
            <strong>{original.col_name}</strong>
          </Typography>
          <Typography variant="caption" component="div" align="left">
            <FormattedMessage
              id="totalExpensesWithTotalExpensesAndCost"
              values={{
                totalExpenses: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={original.total_expenses} />,
                totalUsage: <FormattedDigitalUnit value={original.total_usage} baseUnit={SI_UNITS.GIGABYTE} />,
              }}
            />
          </Typography>
        </Link>
      ),
    },
    ...columns,
  ];
};

const useTableSelectionState = (selectedRows, selectedColumns) => {
  const intl = useIntl();

  if (isEmptyArray(selectedRows) && isEmptyArray(selectedColumns)) {
    return {
      state: TABLE_SELECTION_STATE.NOTHING_SELECTED,
      labels: {
        from: undefined,
        to: undefined,
      },
      data: {
        from: undefined,
        to: undefined,
      },
    };
  }

  if (!isEmptyArray(selectedRows) && isEmptyArray(selectedColumns)) {
    return {
      state: TABLE_SELECTION_STATE.SELECTION_ACTIVE,
      labels: {
        from: selectedRows.length > 1 ? intl.formatMessage({ id: "somewhere" }).toLowerCase() : selectedRows[0],
        to: intl.formatMessage({ id: "somewhere" }).toLowerCase(),
      },
      data: {
        from: selectedRows,
        to: undefined,
      },
    };
  }

  if (isEmptyArray(selectedRows) && !isEmptyArray(selectedColumns)) {
    return {
      state: TABLE_SELECTION_STATE.SELECTION_ACTIVE,
      labels: {
        from: intl.formatMessage({ id: "somewhere" }).toLowerCase(),
        to: selectedColumns.length > 1 ? intl.formatMessage({ id: "otherClouds" }) : selectedColumns[0],
      },
      data: {
        from: undefined,
        to: selectedColumns,
      },
    };
  }

  return {
    state: TABLE_SELECTION_STATE.SELECTION_ACTIVE,
    labels: {
      from: selectedRows.length > 1 ? intl.formatMessage({ id: "somewhere" }).toLowerCase() : selectedRows[0],
      to: selectedColumns.length > 1 ? intl.formatMessage({ id: "otherClouds" }) : selectedColumns[0],
    },
    data: {
      from: selectedRows,
      to: selectedColumns,
    },
  };
};

export const useTrafficExpenses = (expenses) => {
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [selectedRows, setSelectedRows] = useState([]);

  const setTableSelectionState = ({ rows = [], columns = [] }) => {
    setSelectedRows(rows);
    setSelectedColumns(columns);
  };

  const selectedCloudTrafficExpenses = useMemo(() => {
    const hasRowSelection = !isEmptyArray(selectedRows);
    const hasColumnSelection = !isEmptyArray(selectedColumns);

    if (hasRowSelection && hasColumnSelection) {
      return expenses.filter(
        (expense) => selectedRows.includes(expense.from.name) && selectedColumns.includes(expense.to.name)
      );
    }

    if (hasColumnSelection) {
      return expenses.filter((expense) => selectedColumns.includes(expense.to.name));
    }

    if (hasRowSelection) {
      return expenses.filter((expense) => selectedRows.includes(expense.from.name));
    }

    return expenses;
  }, [expenses, selectedColumns, selectedRows]);

  const uniqueDestinations = useMemo(
    () => [
      ...new Set([
        ...selectedCloudTrafficExpenses.map((expense) => expense.from.name),
        ...selectedCloudTrafficExpenses.map((expense) => expense.to.name),
      ]),
    ],
    [selectedCloudTrafficExpenses]
  );

  const uniqueToDestinations = useMemo(
    () => [...new Set([...selectedCloudTrafficExpenses.map((expense) => expense.to.name)])],
    [selectedCloudTrafficExpenses]
  );

  const otherLocationNames = useMemo(
    () =>
      expenses
        .filter(
          (expense) =>
            !expense.to.latitude &&
            !expense.to.longitude &&
            expense.to.name !== INTER_REGION_NAME &&
            expense.to.name !== INTER_CONTINENTAL_NAME &&
            expense.to.name !== EXTERNAL_NAME
        )
        .map((expense) => expense.to.name),
    [expenses]
  );

  const destinationsMap = useMemo(() => {
    const getDestinationMap = (location: { latitude: number; longitude: number; name: string }) => {
      if (
        (location.latitude && location.longitude) ||
        [INTER_REGION_NAME, INTER_CONTINENTAL_NAME, EXTERNAL_NAME].includes(location.name)
      ) {
        return location.name;
      }

      return OTHER_NAME;
    };

    return Object.fromEntries(
      expenses.flatMap((expense) => [
        [expense.from.name, getDestinationMap(expense.from)],
        [expense.to.name, getDestinationMap(expense.to)],
      ])
    );
  }, [expenses]);

  const markers = useMemo(
    () => getMarkers(selectedCloudTrafficExpenses, uniqueDestinations, destinationsMap),
    [destinationsMap, selectedCloudTrafficExpenses, uniqueDestinations]
  );

  const onMapClick = (object) => {
    if (object.type === EXPENSES_MAP_OBJECT_TYPES.LOCATION) {
      if (object.totals.outgoingCount) {
        setTableSelectionState({
          rows: [object.name],
          columns: [],
        });
      } else {
        setTableSelectionState({
          rows: [],
          columns: [object.name],
        });
      }
    }
    if (object.type === EXPENSES_MAP_OBJECT_TYPES.OTHER_MARKER) {
      setTableSelectionState({
        rows: [],
        columns: otherLocationNames,
      });
    }
    if (object.type === EXPENSES_MAP_OBJECT_TYPES.INTER_REGION_MARKER) {
      setTableSelectionState({
        rows: [],
        columns: [INTER_REGION_NAME],
      });
    }
    if (object.type === EXPENSES_MAP_OBJECT_TYPES.INTER_CONTINENTAL_MARKER) {
      setTableSelectionState({
        rows: [],
        columns: [INTER_CONTINENTAL_NAME],
      });
    }
    if (object.type === EXPENSES_MAP_OBJECT_TYPES.EXTERNAL_MARKER) {
      setTableSelectionState({
        rows: [],
        columns: [EXTERNAL_NAME],
      });
    }
    if (object.type === EXPENSES_MAP_OBJECT_TYPES.FLOW) {
      const flowSummary = object.origin.summary.filter(
        (datum) => datum.mapped_from === object.origin.name && datum.mapped_to === object.dest.name
      );
      const columns = flowSummary.map((datum) => datum.original_to);

      setTableSelectionState({
        rows: [object.origin.name],
        columns: columns,
      });
    }
  };

  const tableData = useMemo(
    () => getTableData(selectedCloudTrafficExpenses, uniqueDestinations),
    [selectedCloudTrafficExpenses, uniqueDestinations]
  );

  const columns = useMemo(() => {
    const onColumnHeaderClick = (name) => {
      setTableSelectionState({
        rows: [],
        columns: [name],
      });
    };

    const onRowHeaderClick = (name) => {
      setTableSelectionState({
        rows: [name],
        columns: [],
      });
    };

    const onCellClick = (expense) => {
      setTableSelectionState({
        rows: [expense.from.name],
        columns: [expense.to.name],
      });
    };

    return getColumns({ uniqueToDestinations, onColumnHeaderClick, onRowHeaderClick, onCellClick, selectedColumns, tableData });
  }, [selectedColumns, tableData, uniqueToDestinations]);

  const onFilterClear = useCallback(() => {
    setTableSelectionState({
      rows: [],
      columns: [],
    });
  }, []);

  const tableSelectionState = useTableSelectionState(selectedRows, selectedColumns);

  return {
    markers,
    defaultZoom: 0,
    defaultCenter: { lat: 0, lng: 0 },
    onMapClick,
    tableData,
    columns,
    tableSelectionState,
    onFilterClear,
  };
};
