import { createRoot } from "react-dom/client";
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
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Form />
    </TestProvider>
  );
  root.unmount();
});
