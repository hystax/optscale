import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import S3DuplicateFinderChecksTable from "./S3DuplicateFinderChecksTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <S3DuplicateFinderChecksTable />
    </TestProvider>
  );
  root.unmount();
});
