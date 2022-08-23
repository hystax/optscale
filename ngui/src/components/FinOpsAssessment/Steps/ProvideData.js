import React from "react";
import PropTypes from "prop-types";
import ButtonLoader from "components/ButtonLoader";
import { useToggle } from "hooks/useToggle";
import { PROVIDE_DATA_STEPS } from "utils/constants";
import BePreparedForAssessment from "./BePreparedForAssessment";
import DataSourceUsageAnalysis from "./DataSourceUsageAnalysis";
import ProvideDataStepper from "./ProvideDataStepper";
import SubmitApplicationContainer from "./SubmitApplicationContainer";
import Survey from "./Survey";

const ProvideData = ({ onNext, dataSources, hasDataSourcesInProcessing, isLoadingProps = {}, onCancelAssignment }) => {
  const [connectedDataSources, setConnectedDataSources] = useToggle(false);
  const [completedSurvey, setCompletedSurvey] = useToggle(false);

  const confirmation = { connectedDataSources, completedSurvey };

  const cancelButton = (
    <ButtonLoader
      isLoading={Object.values(isLoadingProps).some(Boolean)}
      messageId="finOpsAssessment.cancelAssignment"
      onClick={onCancelAssignment}
      dataTestId="btn_cancel_application"
      variant="outlined"
    />
  );

  const steps = [
    {
      id: PROVIDE_DATA_STEPS.PLAN,
      title: "finOpsAssessment.bePreparedForAssessmentTitle",
      description: "finOpsAssessment.bePreparedForAssessmentDescription",
      getNode: () => <BePreparedForAssessment />,
      dataTestId: "btn_tab_be_prepared"
    },
    {
      id: PROVIDE_DATA_STEPS.INFRASTRUCTURE,
      title: "finOpsAssessment.dataSourceUsageAnalysisTitle",
      description: "finOpsAssessment.dataSourceUsageAnalysisStepDescription",
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
      id: PROVIDE_DATA_STEPS.SURVEY,
      title: "finOpsAssessment.surveyTitle",
      getNode: () => <Survey isConfirmed={completedSurvey} onConfirm={setCompletedSurvey} />,
      dataTestId: "btn_tab_survey"
    },
    {
      id: PROVIDE_DATA_STEPS.REVIEW_AND_SUBMIT,
      title: "finOpsAssessment.submitApplicationTitle",
      description: "finOpsAssessment.submitApplicationStepDescription",
      getNode: (selectCustomStep) => (
        <SubmitApplicationContainer
          onSubmit={onNext}
          hasDataSourcesInProcessing={hasDataSourcesInProcessing}
          isLoadingProps={isLoadingProps}
          confirmation={confirmation}
          setActiveStep={selectCustomStep}
          cancelButton={cancelButton}
        />
      ),
      dataTestId: "btn_tab_review_and_submit"
    }
  ];

  return <ProvideDataStepper steps={steps} cancelButton={cancelButton} />;
};

ProvideData.propTypes = {
  onNext: PropTypes.func.isRequired,
  dataSources: PropTypes.array,
  hasDataSourcesInProcessing: PropTypes.bool,
  isLoadingProps: PropTypes.object,
  onCancelAssignment: PropTypes.func
};

export default ProvideData;
