import { isEmpty as isEmptyObject } from "utils/objects";

export const getData = ({ breakdown = {}, milestones = [], stages = [] }) => {
  if (isEmptyObject(breakdown)) {
    return {
      breakdown: {},
      milestones: [],
      stages: []
    };
  }

  const breakdownEntries = Object.entries(breakdown);

  const firstTimestamp = breakdownEntries[0][0];
  const timestampToSeconds = (timestamp) => timestamp - firstTimestamp;

  return {
    breakdown: Object.fromEntries(
      Object.entries(breakdown)
        .filter(([, { data = {}, metrics = {} }]) => !isEmptyObject(data) || !isEmptyObject(metrics))
        .map(([timestamp, data]) => [timestampToSeconds(timestamp), data])
    ),
    milestones: milestones.map((milestone) => {
      const { timestamp } = milestone;
      return {
        ...milestone,
        time: timestampToSeconds(timestamp)
      };
    }),
    stages: stages.map((stage) => {
      const { start, end } = stage;

      return {
        ...stage,
        startTimestamp: start,
        endTimestamp: end,
        start: timestampToSeconds(start),
        end: end ? timestampToSeconds(end) : null
      };
    })
  };
};
