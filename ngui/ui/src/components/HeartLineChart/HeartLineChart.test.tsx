import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import HeartLineChart from "./HeartLineChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <HeartLineChart
        values={[1, 2, 3]}
        width={100}
        height={100}
        thresholdArea={{
          start: 2,
          end: 2
        }}
      />
    </TestProvider>
  );
  root.unmount();
});
