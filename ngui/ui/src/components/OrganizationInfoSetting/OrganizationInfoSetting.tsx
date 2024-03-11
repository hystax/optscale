import { useState } from "react";
import CreateOutlinedIcon from "@mui/icons-material/CreateOutlined";
import { Stack, Typography } from "@mui/material";
import Box from "@mui/material/Box";
import { FormattedMessage } from "react-intl";
import CopyText from "components/CopyText";
import IconButton from "components/IconButton";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import EditOrganizationFormContainer from "containers/EditOrganizationFormContainer";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { SPACING_1 } from "utils/layouts";
import OrganizationCurrency from "./OrganizationCurrency";

const OrganizationId = ({ id }) => (
  <KeyValueLabel
    keyMessageId="id"
    value={
      <CopyText
        variant="inherit"
        text={id}
        sx={{
          fontWeight: "inherit"
        }}
      >
        {id}
      </CopyText>
    }
  />
);

const OrganizationName = ({ name }) => {
  const [isEditMode, setIsEditMode] = useState(false);
  const enableEditMode = () => setIsEditMode(true);
  const disableEditMode = () => setIsEditMode(false);

  const isEditAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  return isEditMode ? (
    <EditOrganizationFormContainer onCancel={disableEditMode} onSuccess={disableEditMode} />
  ) : (
    <Box display="flex" alignItems="center">
      <KeyValueLabel keyMessageId="name" value={name} sx={{ marginRight: 1 }} />
      {isEditAllowed && (
        <IconButton
          icon={<CreateOutlinedIcon />}
          onClick={enableEditMode}
          tooltip={{
            show: true,
            messageId: "edit"
          }}
        />
      )}
    </Box>
  );
};

const OrganizationInfoSetting = () => {
  const { name: organizationName, organizationId, currency } = useOrganizationInfo();

  return (
    <Stack spacing={SPACING_1}>
      <Box>
        <OrganizationId id={organizationId} />
      </Box>
      <Box display="flex">
        <OrganizationName name={organizationName} />
      </Box>
      <Box>
        <Typography>
          <FormattedMessage id="organizationCurrencyDescription" />
        </Typography>
      </Box>
      <Box>
        <OrganizationCurrency currencyCode={currency} />
      </Box>
    </Stack>
  );
};

export default OrganizationInfoSetting;
