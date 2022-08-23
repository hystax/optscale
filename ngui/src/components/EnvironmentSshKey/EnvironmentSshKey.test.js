import React from "react";
import ReactDOM from "react-dom";
import { useForm, FormProvider } from "react-hook-form";
import TestProvider from "tests/TestProvider";
import EnvironmentSshKey from "./EnvironmentSshKey";

const WrapWithFormProvider = (props) => {
  const methods = useForm();
  return <FormProvider {...methods}>{props.children}</FormProvider>;
};

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <WrapWithFormProvider>
        <EnvironmentSshKey />
      </WrapWithFormProvider>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
