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

const Tabs = ({ taskId, candidateDetails, leaderboard }) => {
  const qualifiedRunIds = useMemo(() => candidateDetails.qual_runs, [candidateDetails.qual_runs]);
  const otherDatasetRunIds = useMemo(
    () => getDifference(candidateDetails.run_ids, candidateDetails.qual_runs),
    [candidateDetails.qual_runs, candidateDetails.run_ids]
  );

  const tabs = [
    {
      title: TABS.RUNS,
      dataTestId: "tab_runs",
      node: (
        <RunsTabContainer
          taskId={taskId}
          candidateDetails={candidateDetails}
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
          leaderboard={leaderboard}
          candidateDetails={candidateDetails}
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
        name: "candidate-details-tabs",
        queryTabName: "candidateDetailsTab"
      }}
    />
  );
};

export default Tabs;
