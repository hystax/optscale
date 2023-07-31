import React from "react";
import { Box } from "@mui/material";
import PropTypes from "prop-types";
import { FormProvider, useForm } from "react-hook-form";
import { TAGS_RELATED_FILTERS } from "components/Filters/constants";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { ANOMALY_TYPES, EXPIRING_BUDGET_POLICY, QUOTA_POLICY, RECURRING_BUDGET_POLICY, TAGGING_POLICY } from "utils/constants";
import { CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES } from "./constants";
import {
  NameInput,
  TypeSelector,
  EvaluationPeriodInput,
  ThresholdInput,
  CancelButton,
  Filters,
  SubmitButton,
  MonthlyBudgetInput,
  TotalBudgetInput,
  MaxValueInput,
  StartDatePicker,
  TagsInputs,
  TYPE_REQUIRED
} from "./FormElements";

const CreateOrganizationConstraintForm = ({ onSubmit, types, navigateAway }) => {
  const methods = useForm({
    defaultValues: {
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.FILTERS]: {},
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.EVALUATION_PERIOD]: "",
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.NAME]: "",
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.THRESHOLD]: "",
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.TYPE]: types.length === 1 ? types[0] : "",
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.MAX_VALUE]: "",
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.MONTHLY_BUDGET]: "",
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.TOTAL_BUDGET]: "",
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.START_DATE]: +new Date(),
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.TAGS_BAR]: TYPE_REQUIRED,
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.REQUIRED_TAG]: "",
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.PROHIBITED_TAG]: "",
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.CORRELATION_TAG_1]: "",
      [CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.CORRELATION_TAG_2]: ""
    }
  });
  const { handleSubmit, watch } = methods;

  const typeSelected = watch(CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.TYPE);

  return (
    <Box sx={{ width: { md: "50%" } }}>
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <NameInput />
          {types.length > 1 && <TypeSelector types={types} />}
          {ANOMALY_TYPES[typeSelected] && (
            <>
              <EvaluationPeriodInput />
              <ThresholdInput />
            </>
          )}
          {typeSelected === RECURRING_BUDGET_POLICY && <MonthlyBudgetInput />}
          {typeSelected === EXPIRING_BUDGET_POLICY && <TotalBudgetInput />}
          {(typeSelected === EXPIRING_BUDGET_POLICY || typeSelected === TAGGING_POLICY) && <StartDatePicker />}
          {typeSelected === QUOTA_POLICY && <MaxValueInput />}
          {typeSelected === TAGGING_POLICY && <TagsInputs />}
          <Filters exceptions={typeSelected === TAGGING_POLICY ? TAGS_RELATED_FILTERS : undefined} />
          <FormButtonsWrapper>
            <SubmitButton />
            <CancelButton navigateAway={navigateAway} />
          </FormButtonsWrapper>
        </form>
      </FormProvider>
    </Box>
  );
};

CreateOrganizationConstraintForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  types: PropTypes.array.isRequired,
  navigateAway: PropTypes.func.isRequired
};

export default CreateOrganizationConstraintForm;
