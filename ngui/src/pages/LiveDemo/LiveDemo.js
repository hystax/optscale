import React, { useEffect } from "react";
import LiveDemoContainer from "containers/LiveDemoContainer";
import { tag as tagHotjar } from "utils/hotjar";

const LiveDemo = () => {
  useEffect(() => {
    tagHotjar(["live_demo"]);
  }, []);

  return <LiveDemoContainer />;
};

export default LiveDemo;
