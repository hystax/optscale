import { useState } from "react";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { Skeleton, Stack, Typography } from "@mui/material";
import { Box } from "@mui/system";
import { FormattedMessage, FormattedNumber } from "react-intl";
import ActionBar from "components/ActionBar";
import AnomaliesFilters from "components/AnomaliesFilters";
import FormattedMoney from "components/FormattedMoney";
import IconButton from "components/IconButton";
import KeyValueLabel from "components/KeyValueLabel";
import PageContentWrapper from "components/PageContentWrapper";
import { DeleteOrganizationConstraintModal } from "components/SideModalManager/SideModals";
import SubTitle from "components/SubTitle";
import DetectedConstraintsHistoryContainer from "containers/DetectedConstraintsHistoryContainer";
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
    <Box sx={{ display: "flex" }}>
      <KeyValueLabel
        value={<SlicedText limit={80} text={name} />}
        messageId="name"
        typographyProps={{
          sx: {
            marginRight: (theme) => theme.spacing(1)
          }
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
    // means constraint is not loaded: parent component using "isLoading" (using isDataReady leads to old data flickering)
    // todo: convinient loading strategy
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
          typographyProps={{ gutterBottom: true }}
          value={<FormattedMessage id={ANOMALY_TYPES[type] || QUOTAS_AND_BUDGETS_TYPES[type]} />}
          messageId="type"
        />
      )}
      {ANOMALY_TYPES[type] && (
        <KeyValueLabel
          typographyProps={{ gutterBottom: true }}
          value={<FormattedMessage id="xDays" values={{ x: evaluationPeriod }} />}
          messageId="evaluationPeriod"
        />
      )}
      {ANOMALY_TYPES[type] && (
        <KeyValueLabel
          typographyProps={{ gutterBottom: true }}
          value={<FormattedNumber value={threshold / 100} format="percentage" />}
          messageId="threshold"
        />
      )}
      {type === QUOTA_POLICY && (
        <KeyValueLabel
          typographyProps={{ gutterBottom: true }}
          value={<FormattedNumber value={maxValue} />}
          messageId="quotaPolicyMaxValue"
        />
      )}
      {type === RECURRING_BUDGET_POLICY && (
        <KeyValueLabel
          typographyProps={{ gutterBottom: true }}
          value={<FormattedMoney value={monthlyBudget} />}
          messageId="recurringBudgetPolicyMonthlyBudget"
        />
      )}
      {(type === EXPIRING_BUDGET_POLICY || type === TAGGING_POLICY) && (
        <KeyValueLabel
          typographyProps={{ gutterBottom: true }}
          value={format(secondsToMilliseconds(startDate), EN_FULL_FORMAT)}
          messageId="startDate"
        />
      )}
      {type === EXPIRING_BUDGET_POLICY && (
        <KeyValueLabel
          typographyProps={{ gutterBottom: true }}
          value={<FormattedMoney value={totalBudget} />}
          messageId="budget"
        />
      )}
      {type === TAGGING_POLICY && (
        <Typography>
          <TaggingPolicyDescriptionShort conditions={conditions} />
        </Typography>
      )}
    </>
  );
};

const FiltersSection = ({ filters = {}, isLoading }) => (
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
  isLoading = false
}) => {
  const openSideModal = useOpenSideModal();

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
        isLoading,
        show: isAllowed,
        dataTestId: "btn_delete",
        action: () => openSideModal(DeleteOrganizationConstraintModal, { id, name, type })
      }
    ]
  };

  const renderFiltersSection = () => {
    if (isLoading) {
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
            {isLoading ? (
              <Skeleton width="100%">
                <ConstraintProperties />
              </Skeleton>
            ) : (
              <ConstraintProperties id={id} name={name} type={type} definition={definition} />
            )}
          </div>
          <div>{renderFiltersSection()}</div>
          <DetectedConstraintsHistoryContainer constraint={constraint} isGetConstraintLoading={isLoading} />
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default OrganizationConstraint;
