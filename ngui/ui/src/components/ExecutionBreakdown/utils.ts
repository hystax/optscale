import { createGroupsObjectFromArray } from "utils/arrays";

export const getMilestoneTuplesGroupedByTime = (milestones) => {
  const milestonesGroupedByTime = createGroupsObjectFromArray(milestones, (milestone) => milestone.time);

  const milestonesTuplesGroupedByTime = Object.entries(milestonesGroupedByTime).map((el) => [
    Number(el[0]),
    el[1].map(({ milestone }) => milestone)
  ]);

  return milestonesTuplesGroupedByTime;
};
