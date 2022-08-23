import React from "react";
import PropTypes from "prop-types";
import { useNavigate } from "react-router-dom";
import CreateOrganizationConstraintForm from "components/CreateOrganizationConstraintForm";
import { CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES } from "components/CreateOrganizationConstraintForm/constants";
import { TYPE_CORRELATION, TYPE_PROHIBITED, TYPE_REQUIRED } from "components/CreateOrganizationConstraintForm/FormElements";
import { mapAvailableFilterKeys } from "services/AvailableFiltersService";
import OrganizationConstraintsService from "services/OrganizationConstraintsService";
import {
  ACTIVE_FILTER,
  AVAILABLE_SAVINGS_FILTER,
  CONSTRAINT_VIOLATED_FILTER,
  EMPTY_UUID,
  EXPENSE_ANOMALY,
  EXPIRING_BUDGET_POLICY,
  QUOTA_POLICY,
  RECURRING_BUDGET_POLICY,
  RESOURCE_COUNT_ANOMALY,
  TAGGING_POLICY
} from "utils/constants";
import { millisecondsToSeconds } from "utils/datetime";

// This is temporary. The following filters must be send as plain values without putting them into an array. Will be changed.
const PLAIN_FILTERS = [ACTIVE_FILTER, CONSTRAINT_VIOLATED_FILTER, AVAILABLE_SAVINGS_FILTER];

const transformFilterValuesToObject = (filters) =>
  Object.fromEntries(
    Object.entries(filters).map(([key, value]) => {
      const arrayOrPlainValue = PLAIN_FILTERS.includes(key) ? value : [value];
      const arrayValue = Array.isArray(value) ? value : arrayOrPlainValue;

      return [key, arrayValue];
    })
  );

const getTaggingConditions = (formData) => {
  const tagsStrategyType = formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.TAGS_BAR];
  const prohibitedTag = formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.PROHIBITED_TAG];
  const requiredTag = formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.REQUIRED_TAG];
  const correlationTag1 = formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.CORRELATION_TAG_1];
  const correlationTag2 = formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.CORRELATION_TAG_2];

  // corner case, user can leave required tag field empty, and we should use data structure for prohibited tag with EMPTY_UUID
  if (tagsStrategyType === TYPE_REQUIRED && requiredTag === "") {
    return { tag: EMPTY_UUID };
  }

  return {
    [TYPE_REQUIRED]: {
      without_tag: requiredTag
    },
    [TYPE_PROHIBITED]: {
      tag: prohibitedTag
    },
    [TYPE_CORRELATION]: {
      tag: correlationTag1,
      without_tag: correlationTag2
    }
  }[tagsStrategyType];
};

const getDefinition = (type, formData) =>
  ({
    [RESOURCE_COUNT_ANOMALY]: {
      threshold_days: Number(formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.EVALUATION_PERIOD]),
      threshold: Number(formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.THRESHOLD])
    },
    [EXPENSE_ANOMALY]: {
      threshold_days: Number(formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.EVALUATION_PERIOD]),
      threshold: Number(formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.THRESHOLD])
    },
    [QUOTA_POLICY]: {
      max_value: Number(formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.MAX_VALUE])
    },
    [EXPIRING_BUDGET_POLICY]: {
      total_budget: Number(formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.TOTAL_BUDGET]),
      start_date: millisecondsToSeconds(Number(formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.START_DATE]))
    },
    [RECURRING_BUDGET_POLICY]: {
      monthly_budget: Number(formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.MONTHLY_BUDGET])
    },
    [TAGGING_POLICY]: {
      start_date: millisecondsToSeconds(Number(formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.START_DATE])),
      conditions: getTaggingConditions(formData)
    }
  }[type]);

const CreateOrganizationConstraintFormContainer = ({ navigateAwayLink, types }) => {
  const navigate = useNavigate();
  const navigateAway = () => navigate(navigateAwayLink);

  const { useCreate } = OrganizationConstraintsService();

  const { create } = useCreate();

  return (
    <CreateOrganizationConstraintForm
      types={types}
      navigateAway={navigateAway}
      onSubmit={(formData) => {
        const type = formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.TYPE];
        const params = {
          name: formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.NAME],
          type,
          definition: getDefinition(type, formData),
          filters: mapAvailableFilterKeys(
            transformFilterValuesToObject(formData[CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.FILTERS])
          )
        };
        create({ params, onSuccess: navigateAway });
      }}
    />
  );
};

CreateOrganizationConstraintFormContainer.propTypes = {
  navigateAwayLink: PropTypes.string.isRequired,
  types: PropTypes.array.isRequired
};

export default CreateOrganizationConstraintFormContainer;
