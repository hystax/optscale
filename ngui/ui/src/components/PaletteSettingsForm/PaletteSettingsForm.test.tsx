import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import PaletteSettingsForm from "./PaletteSettingsForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <PaletteSettingsForm color="primary" options={{}} onUpdate={vi.fn} />
    </TestProvider>
  );
  root.unmount();
});
