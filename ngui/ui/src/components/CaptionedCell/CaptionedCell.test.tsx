import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CaptionedCell from "./CaptionedCell";

it("renders without crashing without caption", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CaptionedCell>main</CaptionedCell>
    </TestProvider>
  );
  root.unmount();
});

it("renders without crashing with array caption", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CaptionedCell
        caption={[
          { caption: "caption", key: "key1" },
          { node: <div>test</div>, key: "key2" }
        ]}
      >
        main
      </CaptionedCell>
    </TestProvider>
  );
  root.unmount();
});

it("renders without crashing with object caption", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CaptionedCell caption={{ node: <div>test</div>, key: "key2" }}>main</CaptionedCell>
    </TestProvider>
  );
  root.unmount();
});

it("renders without crashing with string caption", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CaptionedCell caption="caption">main</CaptionedCell>
    </TestProvider>
  );
  root.unmount();
});
