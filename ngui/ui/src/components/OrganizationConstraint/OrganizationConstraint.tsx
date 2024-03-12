import { useState } from "react";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { Skeleton, Stack, Typography } from "@mui/material";
import { Box } from "@mui/system";
import { FormattedMessage, FormattedNumber } from "react-intl";
import ActionBar from "components/ActionBar";
import AnomaliesFilters from "components/AnomaliesFilters";
import DetectedConstraintsHistory from "components/DetectedConstraintsHistory";
import FormattedMoney from "components/FormattedMoney";
import IconButton from "components/IconButton";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import PageContentWrapper from "components/PageContentWrapper";
import { DeleteOrganizationConstraintModal } from "components/SideModalManager/SideModals";
import SubTitle from "components/SubTitle";
import EditOrganizationConstraintNameFormContainer from "containers/EditOrganizationConstraintNameFormContainer";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import {
  ANOMALY_TYPES,
  EXPIRING_BUDGET_POLICY,
  QUOTAS_AND_BUDGETS_TYPES,
  QUOTA_POLICY,
  RECURRING_BUDGET_POLICY,
  TAGGING_POLICY,
  TAGGING_POLICY_TYPES
} from "utils/constants";
import { EN_FULL_FORMAT, format, secondsToMilliseconds } from "utils/datetime";
import { SPACING_1 } from "utils/layouts";
import { isEmpty as isEmptyObject } from "utils/objects";
import SlicedText from "../SlicedText";
import TaggingPolicyDescriptionShort from "./TaggingPolicyDescriptionShort";

const ConstraintName = ({ id, name }) => {
  const [isEditMode, setIsEditMode] = useState(false);
  const openEditMode = () => setIsEditMode(true);
  const closeEditMode = () => setIsEditMode(false);

  const isAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  return isEditMode ? (
    <EditOrganizationConstraintNameFormContainer id={id} name={name} onSuccess={closeEditMode} onCancel={closeEditMode} />
  ) : (
    <Box display="flex" alignItems="center">
      <KeyValueLabel
        keyMessageId="name"
        value={<SlicedText limit={80} text={name} />}
        sx={{
          marginRight: 1
        }}
      />
      {id && name && isAllowed ? (
        <IconButton
          key="edit"
          icon={<EditOutlinedIcon />}
          onClick={openEditMode}
          tooltip={{
            show: true,
            messageId: "edit"
          }}
        />
      ) : null}
    </Box>
  );
};

const ConstraintProperties = ({ id, name, type, definition = {} }) => {
  if (!type) {
    // Means constraint is not loaded: parent component using "isLoading" (using isDataReady leads to old data flickering)
    // TODO: Convenient loading strategy
    return null;
  }

  const {
    threshold_days: evaluationPeriod,
    threshold,
    max_value: maxValue,
    monthly_budget: monthlyBudget,
    total_budget: totalBudget,
    start_date: startDate,
    conditions
  } = definition;

  return (
    <>
      <ConstraintName id={id} name={name} />
      {!TAGGING_POLICY_TYPES[type] && (
        <KeyValueLabel
          keyMessageId="type"
          value={<FormattedMessage id={ANOMALY_TYPES[type] || QUOTAS_AND_BUDGETS_TYPES[type]} />}
          gutterBottom
        />
      )}
      {ANOMALY_TYPES[type] && (
        <KeyValueLabel
          keyMessageId="evaluationPeriod"
          value={<FormattedMessage id="xDays" values={{ x: evaluationPeriod }} />}
          gutterBottom
        />
      )}
      {ANOMALY_TYPES[type] && (
        <KeyValueLabel
          keyMessageId="threshold"
          value={<FormattedNumber value={threshold / 100} format="percentage" />}
          gutterBottom
        />
      )}
      {type === QUOTA_POLICY && (
        <KeyValueLabel keyMessageId="quotaPolicyMaxValue" value={<FormattedNumber value={maxValue} />} gutterBottom />
      )}
      {type === RECURRING_BUDGET_POLICY && (
        <KeyValueLabel
          keyMessageId="recurringBudgetPolicyMonthlyBudget"
          value={<FormattedMoney value={monthlyBudget} />}
          gutterBottom
        />
      )}
      {(type === EXPIRING_BUDGET_POLICY || type === TAGGING_POLICY) && (
        <KeyValueLabel keyMessageId="startDate" value={format(secondsToMilliseconds(startDate), EN_FULL_FORMAT)} gutterBottom />
      )}
      {type === EXPIRING_BUDGET_POLICY && (
        <KeyValueLabel keyMessageId="budget" value={<FormattedMoney value={totalBudget} />} gutterBottom />
      )}
      {type === TAGGING_POLICY && (
        <Typography>
          <TaggingPolicyDescriptionShort conditions={conditions} />
        </Typography>
      )}
    </>
  );
};

const FiltersSection = ({ filters = {}, isLoading = false }) => (
  <>
    <SubTitle>
      <FormattedMessage id="filters" />
    </SubTitle>
    {isLoading ? <Skeleton height={80} /> : <AnomaliesFilters filters={filters} showAll />}
  </>
);

const OrganizationConstraint = ({
  actionBarBreadcrumbsDefinition,
  actionBarTitleDefinition,
  constraint,
  limitHits,
  isLoadingProps = {}
}) => {
  const openSideModal = useOpenSideModal();

  const { isGetConstraintLoading = false, isGetLimitHitsLoading = false } = isLoadingProps;

  const isAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  const { id, name, type, definition, filters = {} } = constraint;

  const actionBarDefinition = {
    breadcrumbs: actionBarBreadcrumbsDefinition,
    title: actionBarTitleDefinition,
    items: [
      {
        key: "delete",
        icon: <DeleteOutlinedIcon fontSize="small" />,
        messageId: "delete",
        type: "button",
        isLoading: isGetConstraintLoading,
        show: isAllowed,
        dataTestId: "btn_delete",
        action: () => openSideModal(DeleteOrganizationConstraintModal, { id, name, type })
      }
    ]
  };

  const renderFiltersSection = () => {
    if (isGetConstraintLoading) {
      return <FiltersSection isLoading />;
    }
    if (isEmptyObject(filters)) {
      return null;
    }
    return <FiltersSection filters={filters} />;
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_1}>
          <div>
            {isGetConstraintLoading ? (
              <Skeleton width="100%">
                <ConstraintProperties />
              </Skeleton>
            ) : (
              <ConstraintProperties id={id} name={name} type={type} definition={definition} />
            )}
          </div>
          <div>{renderFiltersSection()}</div>
          <DetectedConstraintsHistory
            constraint={constraint}
            limitHits={limitHits}
            isLoading={isGetConstraintLoading || isGetLimitHitsLoading}
          />
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default OrganizationConstraint;
