import React, { ReactNode, useState } from "react";
import { Stack } from "@mui/material";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import ButtonGroup from "components/ButtonGroup";
import {
  AUTHENTICATION_TYPES,
  authenticationTypes,
  awsConnectionAssumedRoleDescriptions,
  awsConnectionKeyAccessDescriptions,
} from "./constants";
import { AuthenticationType, AuthenticationTypeSelectorType, AwsTypeDescriptionProps } from "./types";

export const AwsTypeDescription = ({
  messageId,
  linkUrl,
  linkDisplayBlock = false,
  type = "paragraph",
}: AwsTypeDescriptionProps) => {
  const content = (
    <Typography>
      <FormattedMessage
        id={messageId}
        values={{
          link: (chunks: ReactNode[]) => {
            const linkText = chunks.length > 0 ? chunks : linkUrl;
            return (
              <Link
                data-test-id="link_guide"
                sx={{ display: linkDisplayBlock ? "inline" : "block" }}
                href={linkUrl}
                target="_blank"
                rel="noopener"
              >
                {linkText}
              </Link>
            );
          },
          strong: (chunks: ReactNode) => <strong>{chunks}</strong>,
        }}
      />
    </Typography>
  );

  if (type === "warning") {
    return (
      <Alert severity="warning" sx={{ mt: 1, mb: 1 }}>
        {content}
      </Alert>
    );
  }

  return (
    <Box key={messageId} sx={{ mt: 1, mb: 1 }}>
      {content}
    </Box>
  );
};

export const useAuthenticationType = () => {
  const [authenticationType, setAuthenticationType] = useState<AuthenticationType>(() => AUTHENTICATION_TYPES.ASSUMED_ROLE);
  return { authenticationType, setAuthenticationType };
};

export const AuthenticationTypeSelector = ({ authenticationType, setAuthenticationType }: AuthenticationTypeSelectorType) => (
  <Stack direction="row" alignItems="center" spacing={2} mb={2}>
    <Typography>
      <FormattedMessage id="authentication" />{" "}
    </Typography>
    <ButtonGroup
      buttons={authenticationTypes.map((subtype) => ({
        id: subtype.authenticationType,
        messageId: subtype.messageId,
        dataTestId: `btn_${subtype.messageId}`,
        action: () => setAuthenticationType(subtype.authenticationType),
      }))}
      activeButtonId={authenticationType}
      activeButtonIndex={undefined}
      fullWidth={false}
    />
  </Stack>
);

export const getAwsConnectionTypeDescriptions = (authenticationType: AuthenticationType) =>
  authenticationType === AUTHENTICATION_TYPES.ASSUMED_ROLE
    ? awsConnectionAssumedRoleDescriptions
    : awsConnectionKeyAccessDescriptions;
