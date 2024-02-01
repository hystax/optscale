import { Stack } from "@mui/material";
import ActionBar from "components/ActionBar";
import CloudCostComparisonFiltersForm from "components/CloudCostComparisonFiltersForm";
import CloudCostComparisonTable from "components/CloudCostComparisonTable";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import PageContentWrapper from "components/PageContentWrapper";
import TableLoader from "components/TableLoader";
import { SPACING_1 } from "utils/layouts";

const actionBarDefinition = {
  title: {
    text: "Cloud Cost Comparison",
    dataTestId: "lbl_cloud_cost_comparison"
  }
};

const CloudCostComparison = ({ isLoading, relevantSizes, defaultFormValues, onFiltersApply, cloudProviders, errors }) => (
  <>
    <ActionBar data={actionBarDefinition} />
    <PageContentWrapper>
      <Stack spacing={SPACING_1}>
        <div>
          <InlineSeverityAlert messageId="cloudCostComparisonDescription" messageValues={{ br: <br /> }} />
        </div>
        <div>
          <CloudCostComparisonFiltersForm onSubmit={onFiltersApply} defaultValues={defaultFormValues} />
        </div>
        <div>
          {isLoading ? (
            <TableLoader />
          ) : (
            <CloudCostComparisonTable relevantSizes={relevantSizes} cloudProviders={cloudProviders} errors={errors} />
          )}
        </div>
      </Stack>
    </PageContentWrapper>
  </>
);

export default CloudCostComparison;
