import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import { Stack } from "@mui/system";
import { GET_ML_DATASETS } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import MlDatasetsTable from "components/MlDatasetsTable";
import PageContentWrapper from "components/PageContentWrapper";
import TableLoader from "components/TableLoader";
import { useRefetchApis } from "hooks/useRefetchApis";
import { SPACING_2 } from "utils/layouts";

const PageActionBar = () => {
  const refetch = useRefetchApis();

  const actionBarDefinition = {
    title: {
      messageId: "datasets",
      dataTestId: "lbl_ml_datasets"
    },
    items: [
      {
        key: "btn-refresh",
        icon: <RefreshOutlinedIcon fontSize="small" />,
        messageId: "refresh",
        dataTestId: "btn_refresh",
        type: "button",
        action: () => refetch([GET_ML_DATASETS])
      }
    ]
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
