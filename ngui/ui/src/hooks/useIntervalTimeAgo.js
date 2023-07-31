import { useFormatIntervalTimeAgo } from "./useFormatIntervalTimeAgo";

export const useIntervalTimeAgo = (agoSecondsTimestamp, precision) => {
  const format = useFormatIntervalTimeAgo();

  return format(agoSecondsTimestamp, precision);
};
