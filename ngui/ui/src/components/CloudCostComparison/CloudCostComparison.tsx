import { Stack } from "@mui/material";
import ActionBar from "components/ActionBar";
import CloudCostComparisonTable from "components/CloudCostComparisonTable";
import CloudCostComparisonFiltersForm from "components/forms/CloudCostComparisonFiltersForm";
import PageContentDescription from "components/PageContentDescription/PageContentDescription";
import PageContentWrapper from "components/PageContentWrapper";
import TableLoader from "components/TableLoader";
import { SPACING_1 } from "utils/layouts";

const actionBarDefinition = {
  title: {
    messageId: "cloudCostComparisonTitle",
    dataTestId: "lbl_cloud_cost_comparison",
  },
};

const CloudCostComparison = ({ relevantSizes, onFiltersApply, errors, isLoading = false }) => {
  const renderContent = () => {
    if (isLoading) {
      return (
        <div>
          <TableLoader />
        </div>
      );
    }

    // undefined - when the user has not applied any filters yet
    if (relevantSizes === undefined) {
      return null;
    }

    return (
      <div>
        <CloudCostComparisonTable relevantSizes={relevantSizes} errors={errors} />
      </div>
    );
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <PageContentDescription
          position="top"
          alertProps={{
            messageId: "cloudCostComparisonDescription",
            messageValues: { br: <br /> },
          }}
        />
        <Stack spacing={SPACING_1}>
          <div>
            <CloudCostComparisonFiltersForm onSubmit={onFiltersApply} isLoading={isLoading} />
          </div>
          {renderContent()}
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default CloudCostComparison;
