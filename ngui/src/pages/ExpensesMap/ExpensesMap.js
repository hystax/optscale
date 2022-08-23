import React, { useState } from "react";
import ActionBar from "components/ActionBar";
import Mocked from "components/Mocked";
import { RegionExpensesMocked } from "components/RegionExpenses";
import { TrafficExpensesMocked } from "components/TrafficExpenses";
import TrafficExpensesContainer from "components/TrafficExpensesContainer";
import RegionExpensesContainer from "containers/RegionExpensesContainer";
import { EXPENSES_MAP_TYPES } from "utils/constants";
import { getQueryParams, updateQueryParams } from "utils/network";

const ExpensesMap = () => {
  const { type } = getQueryParams();

  const [costMapType, setCostMapType] = useState(type || EXPENSES_MAP_TYPES.REGION);

  const handleButtonGroupChange = (mapType) => {
    updateQueryParams({ type: mapType });
    setCostMapType(mapType);
  };

  const actionBarDefinition = {
    hideItemsOnSmallScreens: false,
    title: {
      messageId: "costMapTitle"
    },
    items: [
      {
        key: "switch",
        type: "buttonGroup",
        activeButtonId: costMapType,
        buttons: [
          {
            id: EXPENSES_MAP_TYPES.REGION,
            messageId: EXPENSES_MAP_TYPES.REGION,
            action: () => handleButtonGroupChange(EXPENSES_MAP_TYPES.REGION),
            dataTestId: "region_map"
          },
          {
            id: EXPENSES_MAP_TYPES.TRAFFIC,
            messageId: EXPENSES_MAP_TYPES.TRAFFIC,
            action: () => handleButtonGroupChange(EXPENSES_MAP_TYPES.TRAFFIC),
            dataTestId: "traffic_map"
          }
        ]
      }
    ]
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      {costMapType === EXPENSES_MAP_TYPES.REGION && (
        <Mocked mock={<RegionExpensesMocked />}>
          <RegionExpensesContainer />
        </Mocked>
      )}
      {costMapType === EXPENSES_MAP_TYPES.TRAFFIC && (
        <Mocked mock={<TrafficExpensesMocked />}>
          <TrafficExpensesContainer />
        </Mocked>
      )}
    </>
  );
};

export default ExpensesMap;
