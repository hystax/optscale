import { useMemo } from "react";
import TabsWrapper from "components/TabsWrapper";
import { getDifference } from "utils/arrays";
import CoverageTabContainer from "./CoverageTabContainer";
import DiscussionTab from "./DiscussionTab";
import RunsTabContainer from "./RunsTabContainer";

const TABS = Object.freeze({
  RUNS: "runs",
  COVERAGE: "coverage",
  DISCUSSION: "discussion"
});

const Tabs = ({ taskId, groupDetails, leaderboardDataset }) => {
  const qualifiedRunIds = useMemo(() => groupDetails.qual_runs, [groupDetails.qual_runs]);
  const otherDatasetRunIds = useMemo(
    () => getDifference(groupDetails.run_ids, groupDetails.qual_runs),
    [groupDetails.qual_runs, groupDetails.run_ids]
  );

  const tabs = [
    {
      title: TABS.RUNS,
      dataTestId: "tab_runs",
      node: (
        <RunsTabContainer
          taskId={taskId}
          groupDetails={groupDetails}
          qualifiedRunIds={qualifiedRunIds}
          otherDatasetRunIds={otherDatasetRunIds}
        />
      )
    },
    {
      title: TABS.COVERAGE,
      dataTestId: "tab_coverage",
      node: (
        <CoverageTabContainer
          taskId={taskId}
          qualifiedRunIds={qualifiedRunIds}
          leaderboardDataset={leaderboardDataset}
          groupDetails={groupDetails}
        />
      )
    },
    {
      title: TABS.DISCUSSION,
      dataTestId: "tab_discussion",
      node: <DiscussionTab />
    }
  ];

  return (
    <TabsWrapper
      tabsProps={{
        tabs,
        defaultTab: TABS.RUNS,
        name: "run-group",
        queryTabName: "runGroupTab"
      }}
    />
  );
};

export default Tabs;
