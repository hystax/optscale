import React from "react";
import PropTypes from "prop-types";
import DataUnderProcessing from "./Steps/DataUnderProcessing";
import ProvideData from "./Steps/ProvideData";
import RunReport from "./Steps/RunReport";

const FinOpsAssessment = ({
  step,
  dataSources,
  hasDataSourcesInProcessing,
  onUpdateReport,
  isLoadingProps = {},
  onCancelAssignment
}) =>
  ({
    0: <RunReport onRunReport={onUpdateReport} isLoadingProps={isLoadingProps} />,
    1: (
      <ProvideData
        onNext={onUpdateReport}
        isLoadingProps={isLoadingProps}
        dataSources={dataSources}
        hasDataSourcesInProcessing={hasDataSourcesInProcessing}
        onCancelAssignment={onCancelAssignment}
      />
    ),
    2: <DataUnderProcessing />
    // TODO: handle loading when step is still empty on refresh)
  }[step] ?? <RunReport onRunReport={onUpdateReport} isLoadingProps={isLoadingProps} />);

FinOpsAssessment.propTypes = {
  step: PropTypes.number,
  dataSources: PropTypes.array,
  hasDataSourcesInProcessing: PropTypes.bool,
  onCancelAssignment: PropTypes.func,
  onUpdateReport: PropTypes.func,
  isLoadingProps: PropTypes.shape({
    isGetFinOpsAssessmentLoading: PropTypes.bool,
    isUpdateFinOpsAssessmentLoading: PropTypes.bool,
    isGetDataSourceLoading: PropTypes.bool
  })
};

export default FinOpsAssessment;
