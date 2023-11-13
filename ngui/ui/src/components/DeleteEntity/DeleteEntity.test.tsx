import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import DeleteEntity from "./DeleteEntity";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <DeleteEntity
        message={{ messageId: "deleteResourcesQuestion", values: { count: 1 } }}
        deleteButtonProps={{
          onDelete: () => vi.fn
        }}
        onCancel={() => vi.fn}
      />
    </TestProvider>
  );
  root.unmount();
});
