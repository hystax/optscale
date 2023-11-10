import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import GroupedTables from "./GroupedTables";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <GroupedTables
        groupedResources={[
          [
            "groupValue",
            {
              displayedGroupName: "displayedGroupName",
              count: 0,
              totalExpenses: 0,
              expenses: []
            }
          ]
        ]}
      />
    </TestProvider>
  );
  root.unmount();
});
