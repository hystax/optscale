import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import { FormattedMessage } from "react-intl";
import { GET_ML_ARTIFACTS } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import ArtifactsTable from "components/ArtifactsTable";
import PageContentWrapper from "components/PageContentWrapper";
import MlArtifactsContainer from "containers/MlArtifactsContainer";
import { useRefetchApis } from "hooks/useRefetchApis";

const MlArtifacts = () => {
  const refetch = useRefetchApis();

  const actionBarDefinition = {
    title: {
      text: <FormattedMessage id="artifacts" />,
      dataTestId: "lbl_artifacts"
    },
    items: [
      {
        key: "btn-refresh",
        icon: <RefreshOutlinedIcon fontSize="small" />,
        messageId: "refresh",
        dataTestId: "btn_refresh",
        type: "button",
        action: () => refetch([GET_ML_ARTIFACTS])
      }
    ]
  };
  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <MlArtifactsContainer
          renderTable={({ artifacts, pagination, search, rangeFilter }) => (
            <ArtifactsTable artifacts={artifacts} pagination={pagination} search={search} rangeFilter={rangeFilter} />
          )}
        />
      </PageContentWrapper>
    </>
  );
};

export default MlArtifacts;
