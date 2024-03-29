import { Stack } from "@mui/material";
import MlBreakdownCheckboxes from "components/MlBreakdownCheckboxes";
import Chart from "./Chart";

const Layout = ({
  isLoading,
  selectedBreakdowns,
  colorsMap,
  breakdownConfig,
  addBreakdown,
  removeBreakdown,
  runs,
  getRunNameByNumber,
  colors
}) => (
  <Stack>
    <div>
      <MlBreakdownCheckboxes
        isLoading={isLoading}
        selectedBreakdowns={selectedBreakdowns}
        colorsMap={colorsMap}
        breakdownConfig={breakdownConfig}
        onAddBreakdown={addBreakdown}
        onRemoveBreakdown={removeBreakdown}
      />
    </div>
    <div>
      <Chart
        runs={runs}
        breakdownConfig={breakdownConfig}
        selectedBreakdowns={selectedBreakdowns}
        getRunNameByNumber={getRunNameByNumber}
        colors={colors}
        isLoading={isLoading}
      />
    </div>
  </Stack>
);

export default Layout;
