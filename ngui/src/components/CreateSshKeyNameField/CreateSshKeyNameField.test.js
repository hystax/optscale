import React from "react";
import ReactDOM from "react-dom";
import { FormProvider, useForm } from "react-hook-form";
import TestProvider from "tests/TestProvider";
import CreateSshKeyNameField from "./CreateSshKeyNameField";

const Form = () => {
  const methods = useForm({
    defaultValues: {
      name: ""
    }
  });
  return (
    <FormProvider {...methods}>
      <CreateSshKeyNameField fieldId="name" />
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
