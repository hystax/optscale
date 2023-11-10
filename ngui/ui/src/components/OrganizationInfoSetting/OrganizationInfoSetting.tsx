import { useState } from "react";
import CreateOutlinedIcon from "@mui/icons-material/CreateOutlined";
import { Stack, Typography } from "@mui/material";
import Box from "@mui/material/Box";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import CopyText from "components/CopyText";
import IconButton from "components/IconButton";
import KeyValueLabel from "components/KeyValueLabel";
import EditOrganizationFormContainer from "containers/EditOrganizationFormContainer";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { SPACING_1 } from "utils/layouts";
import OrganizationCurrency from "./OrganizationCurrency";

const OrganizationId = ({ id }) => (
  <KeyValueLabel
    messageId="id"
    value={
      <CopyText variant="inherit" text={id}>
        {id}
      </CopyText>
    }
  />
);

const OrganizationName = ({ name }) => {
  const theme = useTheme();

  const [isEditMode, setIsEditMode] = useState(false);
  const enableEditMode = () => setIsEditMode(true);
  const disableEditMode = () => setIsEditMode(false);

  const isEditAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  return isEditMode ? (
    <EditOrganizationFormContainer onCancel={disableEditMode} onSuccess={disableEditMode} />
  ) : (
    <Box display="flex">
      <KeyValueLabel messageId="name" value={name} typographyProps={{ style: { marginRight: theme.spacing(1) } }} />
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
