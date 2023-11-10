import { createRoot } from "react-dom/client";
import CircleLabel from "./CircleLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(<CircleLabel />);
  root.unmount();
});
