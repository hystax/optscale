import { useState } from "react";
import CreateOutlinedIcon from "@mui/icons-material/CreateOutlined";
import Box from "@mui/material/Box";
import FormattedOrganizationCurrency from "components/FormattedOrganizationCurrency";
import IconButton from "components/IconButton";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import EditOrganizationCurrencyFormContainer from "containers/EditOrganizationCurrencyFormContainer";
import { useAllDataSources } from "hooks/coreData/useAllDataSources";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ENVIRONMENT } from "utils/constants";

const OrganizationCurrency = () => {
  const { currency: currencyCode } = useOrganizationInfo();

  const dataSources = useAllDataSources();

  const [isEditMode, setIsEditMode] = useState(false);
  const enableEditMode = () => setIsEditMode(true);
  const disableEditMode = () => setIsEditMode(false);

  const isEditAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  return isEditMode ? (
    <EditOrganizationCurrencyFormContainer onCancel={disableEditMode} onSuccess={disableEditMode} />
  ) : (
    <Box display="flex" alignItems="center">
      <KeyValueLabel
        keyMessageId="currency"
        value={<FormattedOrganizationCurrency currencyCode={currencyCode} />}
        sx={{ marginRight: 1 }}
      />
      {isEditAllowed && dataSources.filter(({ type }) => type !== ENVIRONMENT).length === 0 ? (
        <IconButton
          icon={<CreateOutlinedIcon />}
          onClick={enableEditMode}
          tooltip={{
            show: true,
            messageId: "edit",
          }}
        />
      ) : null}
    </Box>
  );
};

export default OrganizationCurrency;
