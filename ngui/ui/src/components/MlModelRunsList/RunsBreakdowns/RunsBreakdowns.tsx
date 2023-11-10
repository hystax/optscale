import Breakdown from "./Breakdown";
import Layout from "./Layout";

const RunsBreakdowns = ({ runs, isLoading }) => {
  if (isLoading) {
    return <Layout isLoading />;
  }

  return <Breakdown runs={runs} />;
};

export default RunsBreakdowns;
