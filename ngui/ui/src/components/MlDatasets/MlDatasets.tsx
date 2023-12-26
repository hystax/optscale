import React from "react";
import { Stack } from "@mui/system";
import ActionBar from "components/ActionBar";
import MlDatasetsTable from "components/MlDatasetsTable";
import PageContentWrapper from "components/PageContentWrapper";
import TableLoader from "components/TableLoader";
import { SPACING_2 } from "utils/layouts";

const PageActionBar = () => {
  const actionBarDefinition = {
    title: {
      messageId: "datasets",
      dataTestId: "lbl_ml_datasets"
    }
  };

  return <ActionBar data={actionBarDefinition} />;
};

const MlDatasets = ({ datasets, isLoading }) => (
  <>
    <PageActionBar />
    <PageContentWrapper>
      <Stack spacing={SPACING_2}>
        <div>{isLoading ? <TableLoader showHeader /> : <MlDatasetsTable datasets={datasets} />}</div>
      </Stack>
    </PageContentWrapper>
  </>
);

export default MlDatasets;
