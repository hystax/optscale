import Box from "@mui/material/Box";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ExpensesBreakdownLayoutWrapper from "./ExpensesBreakdownLayoutWrapper";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ExpensesBreakdownLayoutWrapper
        top={<Box>Child 1</Box>}
        center={{
          left: <Box>Child 2</Box>,
          right: <Box>Child 3</Box>
        }}
        bottom={<Box>Child 4</Box>}
      />
    </TestProvider>
  );
  root.unmount();
});
