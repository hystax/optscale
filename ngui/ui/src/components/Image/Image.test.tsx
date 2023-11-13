import { createRoot } from "react-dom/client";
import awsLogo from "assets/clouds/aws.svg";
import TestProvider from "tests/TestProvider";
import Image from "./Image";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <Image src={awsLogo} alt="altText" />
    </TestProvider>
  );
  root.unmount();
});
