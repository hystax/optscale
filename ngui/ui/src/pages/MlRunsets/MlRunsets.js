import React from "react";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import { Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { GET_ML_RUNSET_TEMPLATES } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import MlRunsetTemplatesContainer from "containers/MlRunsetTemplatesContainer";
import { useRefetchApis } from "hooks/useRefetchApis";
import { SPACING_2 } from "utils/layouts";

const MlRunsets = () => {
  const refetch = useRefetchApis();

  const actionBarDefinition = {
    title: {
      messageId: "runsetTemplatesTitle",
      dataTestId: "lbl_ml_runset_templates"
    },
    items: [
      {
        key: "btn-refresh",
        icon: <RefreshOutlinedIcon fontSize="small" />,
        messageId: "refresh",
        dataTestId: "btn_refresh",
        type: "button",
        action: () => refetch([GET_ML_RUNSET_TEMPLATES])
      }
    ]
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          <div>
            <Typography>
              <FormattedMessage id="mlRunsetsDescription" />
            </Typography>
          </div>
          <div>
            <MlRunsetTemplatesContainer />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default MlRunsets;
