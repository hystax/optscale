import React, { useEffect } from "react";
import AddchartOutlinedIcon from "@mui/icons-material/AddchartOutlined";
import AssessmentOutlinedIcon from "@mui/icons-material/AssessmentOutlined";
import GroupWorkOutlinedIcon from "@mui/icons-material/GroupWorkOutlined";
import LinkOutlinedIcon from "@mui/icons-material/LinkOutlined";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import ActionBar from "components/ActionBar";
import CopyText from "components/CopyText";
import { getBasicRangesSet } from "components/DateRangePicker/defaults";
import ExpensesFilters from "components/ExpensesFilters";
import LinearSelector from "components/LinearSelector";
import PageContentWrapper from "components/PageContentWrapper";
import { ApplyResourcePerspectiveModal, CreateResourcePerspectiveModal } from "components/SideModalManager/SideModals";
import TypographyLoader from "components/TypographyLoader";
import CleanExpensesBreakdownContainer from "containers/CleanExpensesBreakdownContainer";
import ExpensesSummaryContainer from "containers/ExpensesSummaryContainer";
import RangePickerFormContainer from "containers/RangePickerFormContainer";
import ResourceCountBreakdownContainer from "containers/ResourceCountBreakdownContainer";
import TagsBreakdownContainer from "containers/TagsBreakdownContainer";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useResourceFilters } from "hooks/useResourceFilters";
import {
  CLUSTER_TYPES,
  DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME,
  DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME,
  getResourcesExpensesUrl,
  RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME,
  RESOURCES_PERSPECTIVE_PARAMETER_NAME
} from "urls";
import {
  BREAKDOWN_LINEAR_SELECTOR_ITEMS,
  CLEAN_EXPENSES_BREAKDOWN_TYPES,
  CLEAN_EXPENSES_BREAKDOWN_TYPES_LIST,
  DATE_RANGE_TYPE
} from "utils/constants";
import { SPACING_2 } from "utils/layouts";
import { getQueryParams, updateQueryParams } from "utils/network";
import { isEmpty as isEmptyObject } from "utils/objects";

const BreakdownLinearSelector = ({ value, onChange }) => {
  useEffect(() => {
    updateQueryParams({ [RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME]: value.name });
  }, [value.name]);

  return (
    <LinearSelector
      value={value}
      label={<FormattedMessage id="breakdownBy" />}
      onChange={onChange}
      items={BREAKDOWN_LINEAR_SELECTOR_ITEMS}
    />
  );
};

const SelectedPerspectiveTitle = ({ perspectiveName }) => {
  const intl = useIntl();

  const { organizationId } = useOrganizationInfo();

  const copyUrl = [
    window.location.origin,
    getResourcesExpensesUrl({
      [RESOURCES_PERSPECTIVE_PARAMETER_NAME]: perspectiveName,
      organizationId
    })
  ].join("");

  return (
    <CopyText text={copyUrl} variant="h6" Icon={LinkOutlinedIcon} copyMessageId="copyUrl">
      {intl.formatMessage(
        { id: "value - value" },
        { value1: intl.formatMessage({ id: "resources" }), value2: perspectiveName }
      )}
    </CopyText>
  );
};

const Resources = ({
  startDateTimestamp,
  endDateTimestamp,
  filters,
  filterValues,
  onApply,
  onFilterAdd,
  onFilterDelete,
  onFiltersDelete,
  requestParams,
  activeBreakdown,
  selectedPerspectiveName,
  perspectives,
  onBreakdownChange,
  onPerspectiveApply,
  isFilterValuesLoading = false
}) => {
  const openSideModal = useOpenSideModal();

  const intl = useIntl();

  const isPerspectiveSelected = selectedPerspectiveName !== undefined;

  const resourceFilters = useResourceFilters(filterValues, filters);

  const items = resourceFilters.getFilterSelectors();
  const appliedValues = resourceFilters.getAppliedValues();

  const actionBarDefinition = {
    title: {
      text: selectedPerspectiveName ? (
        <SelectedPerspectiveTitle perspectiveName={selectedPerspectiveName} />
      ) : (
        intl.formatMessage({ id: "resources" })
      ),
      dataTestId: "lbl_resources"
    },
    items: [
      ...(isEmptyObject(perspectives)
        ? []
        : [
            {
              key: "perspectives",
              icon: <AssessmentOutlinedIcon fontSize="small" />,
              messageId: "perspectivesTitle",
              type: "button",
              action: () => {
                openSideModal(ApplyResourcePerspectiveModal, {
                  perspectives,
                  appliedPerspectiveName: selectedPerspectiveName,
                  onApply: onPerspectiveApply
                });
              }
            }
          ]),
      {
        key: "savePerspectiveTitle",
        icon: <AddchartOutlinedIcon fontSize="small" />,
        messageId: "savePerspectiveTitle",
        disabled: isPerspectiveSelected,
        type: "button",
        action: () => {
          const getBreakdownData = () => {
            const searchParams = getQueryParams();

            if (activeBreakdown.name === CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES) {
              return {
                breakdownBy: searchParams[DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME],
                groupBy: {
                  groupBy: searchParams.groupBy,
                  groupType: searchParams.groupType
                }
              };
            }
            if (activeBreakdown.name === CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT) {
              return {
                breakdownBy: searchParams[DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME]
              };
            }
            return {};
          };

          openSideModal(CreateResourcePerspectiveModal, {
            filters: resourceFilters,
            breakdownBy: activeBreakdown.name,
            breakdownData: getBreakdownData()
          });
        },
        requiredActions: ["EDIT_PARTNER"],
        dataTestId: "btn_create_perspective"
      },
      {
        key: "configureClusterTypes",
        icon: <GroupWorkOutlinedIcon fontSize="small" />,
        messageId: "configureClusterTypes",
        type: "button",
        link: CLUSTER_TYPES,
        dataTestId: "btn_configure_cluster_types"
      }
    ]
  };

  const renderExpensesBreakdown = () => <CleanExpensesBreakdownContainer requestParams={requestParams} />;

  const renderResourcesCountBreakdown = () => <ResourceCountBreakdownContainer requestParams={requestParams} />;

  const renderTagsBreakdown = () => <TagsBreakdownContainer requestParams={requestParams} />;

  const renderContent = {
    [CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES]: renderExpensesBreakdown,
    [CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT]: renderResourcesCountBreakdown,
    [CLEAN_EXPENSES_BREAKDOWN_TYPES.TAGS]: renderTagsBreakdown
  }[activeBreakdown.name];

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid direction="row" container spacing={SPACING_2} justifyContent="space-between">
          <Grid item>
            <ExpensesSummaryContainer requestParams={requestParams} />
          </Grid>
          <Grid item>
            <RangePickerFormContainer
              onApply={(dateRange) => onApply(dateRange)}
              initialStartDateValue={startDateTimestamp}
              initialEndDateValue={endDateTimestamp}
              rangeType={DATE_RANGE_TYPE.RESOURCES}
              definedRanges={getBasicRangesSet()}
            />
          </Grid>
          <Grid xs={12} item>
            {isFilterValuesLoading ? (
              <TypographyLoader linesCount={1} />
            ) : (
              <ExpensesFilters
                items={items}
                appliedValues={appliedValues}
                onFilterDelete={onFilterDelete}
                onFiltersDelete={onFiltersDelete}
                onFilterAdd={onFilterAdd}
              />
            )}
          </Grid>
          <Grid xs={12} item>
            <BreakdownLinearSelector value={activeBreakdown} onChange={onBreakdownChange} />
          </Grid>
          <Grid xs={12} item>
            {typeof renderContent === "function" ? renderContent() : null}
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

Resources.propTypes = {
  startDateTimestamp: PropTypes.number.isRequired,
  endDateTimestamp: PropTypes.number.isRequired,
  filters: PropTypes.object.isRequired,
  filterValues: PropTypes.object.isRequired,
  onApply: PropTypes.func.isRequired,
  onFilterAdd: PropTypes.func.isRequired,
  onFilterDelete: PropTypes.func.isRequired,
  onFiltersDelete: PropTypes.func.isRequired,
  requestParams: PropTypes.object.isRequired,
  activeBreakdown: PropTypes.shape({
    name: PropTypes.oneOf(CLEAN_EXPENSES_BREAKDOWN_TYPES_LIST).isRequired,
    value: PropTypes.oneOf(["expenses", "resource_type", "tags"]).isRequired
  }).isRequired,
  selectedPerspectiveName: PropTypes.string,
  perspectives: PropTypes.object.isRequired,
  onBreakdownChange: PropTypes.func.isRequired,
  onPerspectiveApply: PropTypes.func.isRequired,
  isFilterValuesLoading: PropTypes.bool
};

export default Resources;
