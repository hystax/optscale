import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { GOALS_FILTER_TYPES } from "utils/constants";
import MlRunHistoryChart from "./MlRunHistoryChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlRunHistoryChart history={[]} targetValue={0} tendency={GOALS_FILTER_TYPES.LESS_IS_BETTER} />
    </TestProvider>
  );
  root.unmount();
});
