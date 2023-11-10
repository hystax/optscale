import LatestEvents from "components/LatestEvents";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/LatestEvents`
};

export const basic = () => <LatestEvents count={0} />;

export const withCount = () => <LatestEvents count={1} />;

export const withLargeCount = () => <LatestEvents count={99999} />;
