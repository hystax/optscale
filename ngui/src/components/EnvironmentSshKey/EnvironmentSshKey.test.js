import React from "react";
import { createRoot } from "react-dom/client";
import { useForm, FormProvider } from "react-hook-form";
import TestProvider from "tests/TestProvider";
import EnvironmentSshKey from "./EnvironmentSshKey";

const WrapWithFormProvider = (props) => {
  const methods = useForm();
  return <FormProvider {...methods}>{props.children}</FormProvider>;
};

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <WrapWithFormProvider>
        <EnvironmentSshKey />
      </WrapWithFormProvider>
    </TestProvider>
  );
  root.unmount();
});
