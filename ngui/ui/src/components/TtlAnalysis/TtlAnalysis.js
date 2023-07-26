import React from "react";
import CreateOutlinedIcon from "@mui/icons-material/CreateOutlined";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import ChipFiltersWrapper from "components/ChipFiltersWrapper";
import PoolLabel from "components/PoolLabel";
import TtlAnalysisForm from "components/TtlAnalysisForm";
import TtlAnalysisReport from "components/TtlAnalysisReport";
import { TTL_ANALYSIS_TOP_SECTION_TYPES } from "utils/constants";
import { unixTimestampToDateTime } from "utils/datetime";
import { SPACING_4 } from "utils/layouts";

const renderFilterChips = ({ chips, buttonsDefinition }) => (
  <ChipFiltersWrapper chips={chips} buttonsDefinition={buttonsDefinition} />
);

const TtlAnalysis = ({
  topSectionComponent,
  onEdit,
  shouldRenderReportLayout,
  TtlAnalysisFormProps,
  TtlAnalysisReportProps
}) => {
  const { type: topSectionComponentType, payload: topSectionComponentPayload = {} } = topSectionComponent;

  const getTopPageSectionRenderer = () =>
    ({
      [TTL_ANALYSIS_TOP_SECTION_TYPES.FORM]: () => <TtlAnalysisForm {...TtlAnalysisFormProps} />,
      [TTL_ANALYSIS_TOP_SECTION_TYPES.APPLIED_FILTERS]: () =>
        renderFilterChips({
          chips: [
            {
              messageId: "pool",
              filterValue: (
                <PoolLabel
                  name={topSectionComponentPayload.poolName}
                  type={topSectionComponentPayload.poolType}
                  id={topSectionComponentPayload.poolId}
                />
              )
            },
            {
              messageId: "ttl",
              filterValue: <FormattedMessage id="hour" values={{ value: topSectionComponentPayload.ttl }} />
            },
            {
              messageId: "dateRange",
              filterValue: `${unixTimestampToDateTime(topSectionComponentPayload.startDate)} - ${unixTimestampToDateTime(
                topSectionComponentPayload.endDate
              )}`
            }
          ],
          buttonsDefinition: [
            {
              component: Button,
              props: {
                key: "edit",
                dashedBorder: true,
                startIcon: <CreateOutlinedIcon />,
                onClick: onEdit,
                messageId: "edit",
                color: "primary"
              }
            }
          ]
        })
    }[topSectionComponentType]);

  const renderTopPageSection = getTopPageSectionRenderer();

  return (
    <Grid container spacing={SPACING_4}>
      <Grid item xs={12}>
        {renderTopPageSection()}
      </Grid>
      {shouldRenderReportLayout && (
        <Grid item xs={12}>
          <TtlAnalysisReport {...TtlAnalysisReportProps} />
        </Grid>
      )}
    </Grid>
  );
};

TtlAnalysis.propTypes = {
  topSectionComponent: PropTypes.shape({
    type: PropTypes.string.isRequired,
    payload: PropTypes.object
  }).isRequired,
  onEdit: PropTypes.func.isRequired,
  shouldRenderReportLayout: PropTypes.bool.isRequired,
  TtlAnalysisFormProps: PropTypes.shape({
    onSubmit: PropTypes.func.isRequired,
    pools: PropTypes.array.isRequired,
    defaultValues: PropTypes.object.isRequired,
    isLoading: PropTypes.bool,
    isPoolSelectorReadOnly: PropTypes.bool
  }).isRequired,
  TtlAnalysisReportProps: PropTypes.shape({
    resourcesTracked: PropTypes.number,
    resourcesOutsideOfTtl: PropTypes.number,
    totalExpenses: PropTypes.number,
    expensesOutsideOfTtl: PropTypes.number,
    resources: PropTypes.array,
    isLoading: PropTypes.bool
  }).isRequired
};

export default TtlAnalysis;
