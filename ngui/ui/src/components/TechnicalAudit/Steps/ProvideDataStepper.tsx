import { useEffect, useState } from "react";
import { Step, StepContent, StepLabel, Stepper, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import SubTitle from "components/SubTitle";
import { getQueryParams, updateQueryParams } from "utils/network";

const STEP_QUERY_PARAM = "provideData";

const NavigationButtons = ({ index, lastStepIndex, handleNext, handleBack }) =>
  index !== lastStepIndex ? (
    <FormButtonsWrapper mt={0}>
      {index !== 0 && <Button messageId="back" onClick={handleBack} variant="outlined" />}
      <Button messageId="next" onClick={handleNext} variant="contained" color="primary" />
    </FormButtonsWrapper>
  ) : null;

const ProvideDataStepper = ({ steps }) => {
  const findStepIndexById = (stepId) => {
    const foundIndex = steps.findIndex(({ id }) => id === stepId);
    return foundIndex === -1 ? 0 : foundIndex;
  };

  const { [STEP_QUERY_PARAM]: queryStep } = getQueryParams();

  const [activeStep, setActiveStep] = useState(findStepIndexById(queryStep));

  useEffect(() => {
    updateQueryParams({ [STEP_QUERY_PARAM]: steps[activeStep].id });
  }, [activeStep, steps]);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const selectCustomStep = (stepId) => {
    setActiveStep(findStepIndexById(stepId));
  };

  return (
    <Stepper activeStep={activeStep} orientation="vertical">
      {steps.map(({ id, description, title, getNode }, index) => (
        <Step key={id}>
          <StepLabel
            sx={{
              cursor: "pointer",
              "& .Mui-disabled": {
                cursor: "pointer"
              }
            }}
            onClick={() => setActiveStep(index)}
            StepIconProps={{ active: true, completed: false }}
            optional={
              description ? (
                <Typography>
                  <FormattedMessage id={description} />
                </Typography>
              ) : null
            }
          >
            <SubTitle>
              <FormattedMessage id={title} />
            </SubTitle>
          </StepLabel>
          <StepContent>
            {getNode(selectCustomStep)}
            <NavigationButtons index={index} lastStepIndex={steps.length - 1} handleBack={handleBack} handleNext={handleNext} />
          </StepContent>
        </Step>
      ))}
    </Stepper>
  );
};

export default ProvideDataStepper;
