import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import SnackbarAlert from "./SnackbarAlert";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider
      state={{
        api: { latestErrorLabel: "" }
      }}
    >
      <SnackbarAlert text="test" openState={false} handleClose={(e) => console.log(e)} />
    </TestProvider>
  );
  root.unmount();
});
