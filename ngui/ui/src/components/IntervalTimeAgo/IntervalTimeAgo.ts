import { useIntervalTimeAgo } from "hooks/useIntervalTimeAgo";

const IntervalTimeAgo = ({ secondsTimestamp, precision }) => {
  const timeAgo = useIntervalTimeAgo(secondsTimestamp, precision);

  return timeAgo;
};

export default IntervalTimeAgo;
