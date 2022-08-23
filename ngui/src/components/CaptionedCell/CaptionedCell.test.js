import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CaptionedCell from "./CaptionedCell";

it("renders without crashing without caption", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CaptionedCell>main</CaptionedCell>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

it("renders without crashing with array caption", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CaptionedCell
        caption={[
          { caption: "caption", key: "key1" },
          { node: <div>test</div>, key: "key2" }
        ]}
      >
        main
      </CaptionedCell>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

it("renders without crashing with object caption", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CaptionedCell caption={{ node: <div>test</div>, key: "key2" }}>main</CaptionedCell>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});

it("renders without crashing with string caption", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CaptionedCell caption="caption">main</CaptionedCell>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
