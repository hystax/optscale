import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import { FormattedMessage } from "react-intl";
import { GET_ML_MODELS } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import MlModelsContainer from "containers/MlModelsContainer";
import { useRefetchApis } from "hooks/useRefetchApis";

const MlModels = () => {
  const refetch = useRefetchApis();

  const actionBarDefinition = {
    title: {
      text: <FormattedMessage id="models" />,
      dataTestId: "lbl_models"
    },
    items: [
      {
        key: "btn-refresh",
        icon: <RefreshOutlinedIcon fontSize="small" />,
        messageId: "refresh",
        dataTestId: "btn_refresh",
        type: "button",
        action: () => refetch([GET_ML_MODELS])
      }
    ]
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <MlModelsContainer />
      </PageContentWrapper>
    </>
  );
};

export default MlModels;
