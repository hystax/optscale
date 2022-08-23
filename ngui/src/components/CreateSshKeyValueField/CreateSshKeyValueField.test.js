import React from "react";
import ReactDOM from "react-dom";
import { FormProvider, useForm } from "react-hook-form";
import TestProvider from "tests/TestProvider";
import CreateSshKeyValueField from "./CreateSshKeyValueField";

const Form = () => {
  const methods = useForm({
    defaultValues: {
      key: ""
    }
  });
  return (
    <FormProvider {...methods}>
      <CreateSshKeyValueField fieldId="key" />
    </FormProvider>
  );
};

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Form />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
