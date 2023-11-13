import { createRoot } from "react-dom/client";
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
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Form />
    </TestProvider>
  );
  root.unmount();
});
