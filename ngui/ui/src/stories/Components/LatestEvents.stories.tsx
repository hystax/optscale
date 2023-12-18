import LatestEvents from "components/LatestEvents";

export default {
  component: LatestEvents
};

export const basic = () => <LatestEvents count={0} />;

export const withCount = () => <LatestEvents count={1} />;

export const withLargeCount = () => <LatestEvents count={99999} />;
