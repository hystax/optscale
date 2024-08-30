import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import TypographySettingsForm from "./TypographySettingsForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <TypographySettingsForm variant="body1" options={{}} onUpdate={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});
