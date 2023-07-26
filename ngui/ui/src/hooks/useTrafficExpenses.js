import React, { useCallback, useMemo, useState } from "react";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormattedMessage, useIntl } from "react-intl";
import FormattedDigitalUnit, { SI_UNITS } from "components/FormattedDigitalUnit";
import FormattedMoney from "components/FormattedMoney";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { EXPENSES_MAP_OBJECT_TYPES, FORMATTED_MONEY_TYPES } from "utils/constants";
import { EXTERNAL_LAT, EXTERNAL_LON, INTER_REGION_LAT, INTER_REGION_LON, INTER_REGION_NAME } from "utils/maps";

const DEFAULT_SELECTION_STATE = Object.freeze({ selectedCell: null, selectedColumnNames: [], selectedRowName: "" });

export const TABLE_SELECTION_STATE = Object.freeze({
  NOTHING_SELECTED: "NOTHING_SELECTED",
  ROW_SELECTED: "ROW_SELECTED",
  COLUMNS_SELECTED: "COLUMNS_SELECTED",
  CELL_SELECTED: "CELL_SELECTED"
});

const getTableData = (expenses, uniqueDestinations) =>
  uniqueDestinations
    .map((uniqueDestination) => {
      const filteredExpenses = expenses.filter((expense) => expense.from.name === uniqueDestination);
      const row = filteredExpenses.reduce(
        (resultObject, expense) => ({
          ...resultObject,
          [expense.to.name]: expense
        }),
        {}
      );
      row.col_name = uniqueDestination;
      row.total_expenses = filteredExpenses.reduce((result, expense) => result + expense.cost, 0);
      row.total_usage = filteredExpenses.reduce((result, expense) => result + expense.usage, 0);
      return row;
    })
    .filter((row) => Object.keys(row).length > 3);

const getMarkers = (expenses, uniqueDestinations) => {
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

    let latitude = EXTERNAL_LAT;
    let longitude = EXTERNAL_LON;
    if (expense.from.name === uniqueDestination) {
      latitude = expense.from.latitude;
      longitude = expense.from.longitude;
    } else if (expense.to.latitude && expense.to.longitude) {
      latitude = expense.to.latitude;
      longitude = expense.to.longitude;
    } else if (uniqueDestination === INTER_REGION_NAME) {
      latitude = INTER_REGION_LAT;
      longitude = INTER_REGION_LON;
    }

    return [
      ...resultArray,
      {
        id: uniqueDestination,
        latitude,
        longitude,
        type: expense.cloud_type,
        name: uniqueDestination,
        expenses: filteredExpenses,
        totalExpenses: filteredExpenses.reduce((result, e) => result + e.cost, 0),
        totalUsage: filteredExpenses.reduce((result, e) => result + e.usage, 0)
      }
    ];
  }, []);

  return {
    locations,
    flows: expenses.filter((expense) => expense.from.latitude && expense.from.longitude),
    externalLocations: locations.filter(
      (location) => location.latitude === EXTERNAL_LAT && location.longitude === EXTERNAL_LON
    ),
    interRegion: locations.find((location) => location.name === INTER_REGION_NAME)
  };
};

const getColumns = ({ uniqueToDestinations, onColumnHeaderClick, onRowHeaderClick, onCellClick, selectedState, tableData }) => {
  const { selectedColumnNames } = selectedState;
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
      whiteSpace: "nowrap"
    },
    cell: ({ cell }) => {
      const expense = cell.getValue();

      return (
        <Link component="button" onClick={() => onCellClick(expense)} color="inherit">
          <Typography variant="caption" component="div" align={"left"}>
            <strong>
              <FormattedMoney value={expense.cost} type={FORMATTED_MONEY_TYPES.COMPACT} disableTooltip />{" "}
            </strong>
          </Typography>
          <Typography variant="caption" component="div" align={"left"}>
            <FormattedDigitalUnit value={expense.usage} baseUnit={SI_UNITS.GIGABYTE} />
          </Typography>
        </Link>
      );
    }
  }));

  if (tableData.length === 1) {
    const rowValues = new Map(Object.values(tableData[0]).map((value) => [value?.to?.name, value.cost]));
    columns = columns
      .filter((column) => Object.keys(tableData[0]).includes(column.accessorKey))
      .sort((a, b) => rowValues.get(b.accessorKey) - rowValues.get(a.accessorKey));
  }

  if (!isEmptyArray(selectedColumnNames)) {
    columns = columns.filter((column) => selectedColumnNames.includes(column.accessorKey));
  }

  return [
    {
      id: "name_col",
      header: <FormattedMessage id="from/to" />,
      accessorKey: "col_name",
      enableSorting: false,
      style: {
        whiteSpace: "nowrap"
      },
      cell: ({ row: { original } }) => (
        <Link component="button" onClick={() => onRowHeaderClick(original.col_name)} color="inherit">
          <Typography variant="subtitle2" component="div" align={"left"}>
            <strong>{original.col_name}</strong>
          </Typography>
          <Typography variant="caption" component="div" align={"left"}>
            <FormattedMessage
              id="totalExpensesWithTotalExpensesAndCost"
              values={{
                totalExpenses: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={original.total_expenses} />,
                totalUsage: <FormattedDigitalUnit value={original.total_usage} baseUnit={SI_UNITS.GIGABYTE} />
              }}
            />
          </Typography>
        </Link>
      )
    },
    ...columns
  ];
};

const useTableSelectionState = (selectedState) => {
  const intl = useIntl();

  const isRowSelected = !!selectedState.selectedRowName;
  const isColumnsSelected = !isEmptyArray(selectedState.selectedColumnNames);
  const isCellSelected = !!selectedState.selectedCell;

  if ([isRowSelected, isColumnsSelected, isCellSelected].every((isSelected) => isSelected === false)) {
    return {
      state: TABLE_SELECTION_STATE.NOTHING_SELECTED,
      labels: {
        from: undefined,
        to: undefined
      },
      data: {
        from: undefined,
        to: undefined
      }
    };
  }

  if (isRowSelected) {
    return {
      state: TABLE_SELECTION_STATE.ROW_SELECTED,
      labels: {
        from: selectedState.selectedRowName,
        to: intl.formatMessage({ id: "somewhere" }).toLowerCase()
      },
      data: {
        from: selectedState.selectedRowName,
        to: undefined
      }
    };
  }
  if (isColumnsSelected) {
    return {
      state: TABLE_SELECTION_STATE.COLUMNS_SELECTED,
      labels: {
        from: intl.formatMessage({ id: "somewhere" }).toLowerCase(),
        to:
          selectedState.selectedColumnNames.length > 1
            ? intl.formatMessage({ id: "externalAndOtherClouds" })
            : selectedState.selectedColumnNames[0]
      },
      data: {
        from: undefined,
        to: [...selectedState.selectedColumnNames]
      }
    };
  }
  return {
    state: TABLE_SELECTION_STATE.CELL_SELECTED,
    labels: {
      from: selectedState.selectedCell.from.name,
      to: selectedState.selectedCell.to.name
    },
    data: {
      from: selectedState.selectedCell.from.name,
      to: selectedState.selectedCell.to.name
    }
  };
};

export const useTrafficExpenses = (expenses) => {
  const [selectedState, setSelectedState] = useState(DEFAULT_SELECTION_STATE);

  const selectedCloudTrafficExpenses = useMemo(() => {
    const { selectedCell, selectedColumnNames, selectedRowName } = selectedState;

    if (selectedCell !== null) {
      return expenses.filter(
        (expense) => expense.from.name === selectedCell.from.name && expense.to.name === selectedCell.to.name
      );
    }
    if (!isEmptyArray(selectedColumnNames)) {
      return expenses.filter((expense) => selectedColumnNames.includes(expense.to.name));
    }
    if (selectedRowName !== "") {
      return expenses.filter((expense) => expense.from.name === selectedRowName);
    }
    return expenses;
  }, [expenses, selectedState]);

  const uniqueDestinations = useMemo(
    () => [
      ...new Set([
        ...selectedCloudTrafficExpenses.map((expense) => expense.from.name),
        ...selectedCloudTrafficExpenses.map((expense) => expense.to.name)
      ])
    ],
    [selectedCloudTrafficExpenses]
  );

  const uniqueToDestinations = useMemo(
    () => [...new Set([...selectedCloudTrafficExpenses.map((expense) => expense.to.name)])],
    [selectedCloudTrafficExpenses]
  );

  const externalLocationNames = useMemo(
    () =>
      expenses.reduce((resultArray, expense) => {
        if (
          !(expense.to.latitude && expense.to.longitude) &&
          expense.to.name !== INTER_REGION_NAME &&
          !resultArray.includes(expense.to.name)
        ) {
          return [...resultArray, expense.to.name];
        }
        return [...resultArray];
      }, []),
    [expenses]
  );

  const markers = useMemo(
    () => getMarkers(selectedCloudTrafficExpenses, uniqueDestinations),
    [selectedCloudTrafficExpenses, uniqueDestinations]
  );

  const selectColumns = (names) => setSelectedState({ selectedRowName: "", selectedCell: null, selectedColumnNames: names });

  const selectRow = (name) => setSelectedState({ selectedColumnNames: [], selectedRowName: name, selectedCell: null });

  const selectCell = (cellData) => setSelectedState({ selectedRowName: "", selectedColumnNames: [], selectedCell: cellData });

  const onMapClick = (object) => {
    if (object.type === EXPENSES_MAP_OBJECT_TYPES.LOCATION) {
      if (object.totals.outgoingCount) {
        selectRow(object.name);
      } else {
        selectColumns([object.name]);
      }
    }
    if (object.type === EXPENSES_MAP_OBJECT_TYPES.EXTERNAL_MARKER) {
      selectColumns(externalLocationNames);
    }
    if (object.type === EXPENSES_MAP_OBJECT_TYPES.INTER_REGION_MARKER) {
      selectColumns([INTER_REGION_NAME]);
    }
    if (object.type === EXPENSES_MAP_OBJECT_TYPES.FLOW) {
      selectCell({ from: { name: object.flow.origin }, to: { name: object.flow.dest } });
    }
  };

  const tableData = useMemo(
    () => getTableData(selectedCloudTrafficExpenses, uniqueDestinations),
    [selectedCloudTrafficExpenses, uniqueDestinations]
  );

  const columns = useMemo(() => {
    const onColumnHeaderClick = (name) => {
      selectColumns([name]);
    };

    const onRowHeaderClick = (name) => {
      selectRow(name);
    };

    const onCellClick = (expense) => {
      selectCell(expense);
    };

    return getColumns({ uniqueToDestinations, onColumnHeaderClick, onRowHeaderClick, onCellClick, selectedState, tableData });
  }, [selectedState, uniqueToDestinations, tableData]);

  const onFilterClear = useCallback(() => {
    setSelectedState(DEFAULT_SELECTION_STATE);
  }, [setSelectedState]);

  const tableSelectionState = useTableSelectionState(selectedState);

  return {
    markers,
    defaultZoom: 0,
    defaultCenter: { lat: 0, lng: 0 },
    onMapClick,
    tableData,
    columns,
    tableSelectionState,
    onFilterClear
  };
};
