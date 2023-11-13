import { createRoot } from "react-dom/client";
import { PRODUCT_TOUR } from "components/Tour";
import TestProvider from "tests/TestProvider";
import Mocked from "./Mocked";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider
      state={{
        [PRODUCT_TOUR]: { isOpen: false, isFinished: false }
      }}
    >
      <Mocked mock={<div>Mock</div>}>
        <div>Component</div>
      </Mocked>
    </TestProvider>
  );
  root.unmount();
});
