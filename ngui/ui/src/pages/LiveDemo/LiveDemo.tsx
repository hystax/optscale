import { useEffect } from "react";
import LiveDemoComponent from "components/LiveDemo";
import { tag as tagHotjar } from "utils/hotjar";

const LiveDemo = () => {
  useEffect(() => {
    tagHotjar(["live_demo"]);
  }, []);

  return <LiveDemoComponent />;
};

export default LiveDemo;
