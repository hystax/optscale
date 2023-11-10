import { createRoot } from "react-dom/client";
import { useForm } from "react-hook-form";
import TestProvider from "tests/TestProvider";
import SwitchField from "./SwitchField";

const Component = () => {
  const { control } = useForm();
  return <SwitchField name="name" defaultValue labelMessageId="name" control={control} />;
};

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Component />
    </TestProvider>
  );
  root.unmount();
});
