import React from "react";
import PropTypes from "prop-types";
import { useToggle } from "hooks/useToggle";
import { PROVIDE_DATA_STEPS } from "utils/constants";
import DataSourceUsageAnalysis from "./DataSourceUsageAnalysis";
import PlanSubmission from "./PlanSubmission";
import ProvideDataStepper from "./ProvideDataStepper";
import SourceCodeStateReportContainer from "./SourceCodeStateReportContainer";
import SubmitApplicationContainer from "./SubmitApplicationContainer";
import Survey from "./Survey";

const ProvideData = ({ onNext, dataSources, hasDataSourcesInProcessing, isLoadingProps = {} }) => {
  const [connectedDataSources, setConnectedDataSources] = useToggle(false);
  const [uploadedCodeReport, setUploadedCodeReport] = useToggle(false);
  const [completedSurvey, setCompletedSurvey] = useToggle(false);

  const confirmation = { connectedDataSources, uploadedCodeReport, completedSurvey };

  const steps = [
    {
      id: PROVIDE_DATA_STEPS.PLAN,
      title: "technicalAudit.planSubmissionTitle",
      description: "technicalAudit.planSubmissionStepDescription",
      getNode: () => <PlanSubmission />,
      dataTestId: "btn_tab_plan"
    },
    {
      id: PROVIDE_DATA_STEPS.INFRASTRUCTURE,
      title: "technicalAudit.dataSourceUsageAnalysisTitle",
      description: "technicalAudit.dataSourceUsageAnalysisStepDescription",
      getNode: () => (
        <DataSourceUsageAnalysis
          isLoadingProps={isLoadingProps}
          dataSources={dataSources}
          onConfirm={setConnectedDataSources}
          isConfirmed={connectedDataSources}
        />
      ),
      dataTestId: "btn_tab_infrastructure"
    },
    {
      id: PROVIDE_DATA_STEPS.CODE,
      title: "technicalAudit.sourceCodeStateReportTitle",
      getNode: () => (
        <SourceCodeStateReportContainer
          isLoadingProps={isLoadingProps}
          isConfirmed={uploadedCodeReport}
          onConfirm={setUploadedCodeReport}
          onUploadCallback={onNext}
        />
      ),
      dataTestId: "btn_tab_code"
    },
    {
      id: PROVIDE_DATA_STEPS.SURVEY,
      title: "technicalAudit.surveyTitle",
      getNode: () => <Survey isConfirmed={completedSurvey} onConfirm={setCompletedSurvey} />,
      dataTestId: "btn_tab_survey"
    },
    {
      id: PROVIDE_DATA_STEPS.REVIEW_AND_SUBMIT,
      title: "technicalAudit.submitApplicationTitle",
      description: "technicalAudit.submitApplicationStepDescription",
      getNode: (selectCustomStep) => (
        <SubmitApplicationContainer
          onSubmit={onNext}
          hasDataSourcesInProcessing={hasDataSourcesInProcessing}
          isLoadingProps={isLoadingProps}
          confirmation={confirmation}
          setActiveStep={selectCustomStep}
        />
      ),
      dataTestId: "btn_tab_review_and_submit"
    }
  ];

  return <ProvideDataStepper steps={steps} />;
};

ProvideData.propTypes = {
  onNext: PropTypes.func.isRequired,
  dataSources: PropTypes.array,
  hasDataSourcesInProcessing: PropTypes.bool,
  isLoadingProps: PropTypes.object
};

export default ProvideData;
