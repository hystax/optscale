import React from "react";
import ReactDOM from "react-dom";
import { useForm } from "react-hook-form";
import TestProvider from "tests/TestProvider";
import SwitchField from "./SwitchField";

const Component = () => {
  const { control } = useForm();
  return <SwitchField name="name" defaultValue labelMessageId="name" control={control} />;
};

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Component />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
