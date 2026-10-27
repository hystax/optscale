import { useCallback, useEffect } from "react";
import { Box, CircularProgress, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import MailTo from "components/MailTo";
import { useCreateOrganizationMutation } from "graphql/__generated__/hooks/restapi";
import { useSignOut } from "hooks/useSignOut";
import { EMAIL_SUPPORT } from "urls";
import { Title } from "../../common";

type SetupOrganizationProps = {
  userEmail: string;
  refetchOrganizations: () => void;
};

const getOrganizationName = (userEmail: string) => `${userEmail}'s Organization`;

const SetupOrganization = ({ userEmail, refetchOrganizations }: SetupOrganizationProps) => {
  const signOut = useSignOut();

  const [createOrganization, { error: createOrganizationError }] = useCreateOrganizationMutation();
  const setupOrganization = useCallback(async () => {
    const { data } = await createOrganization({
      variables: {
        organizationName: getOrganizationName(userEmail),
      },
    });

    const organization = data?.createOrganization;

    if (!organization?.id) {
      throw new Error("Organization creation failed: no ID returned");
    }

    await refetchOrganizations();
  }, [userEmail, createOrganization, refetchOrganizations]);

  useEffect(() => {
    const initialize = async () => {
      try {
        await setupOrganization();
      } catch (err) {
        console.error("Error while setup organization: ", err);
      }
    };

    initialize();
  }, [setupOrganization]);

  if (createOrganizationError) {
    return (
      <>
        <Box>
          <Title dataTestId="p_organization_creation_failed" messageId="organizationCreationFailed" />
          <Typography align="center" variant="body2" px={2}>
            <FormattedMessage
              id="pleaseSignInAgainAndIfTheProblemPersists"
              values={{
                email: <MailTo email={EMAIL_SUPPORT} text={EMAIL_SUPPORT} dataTestId="p_organization_creation_failed_email" />,
              }}
            />
          </Typography>
        </Box>
        <Box height={60} display="flex" alignItems="center" gap={2}>
          <Button size="medium" messageId="signOut" color="primary" onClick={signOut} />
        </Box>
      </>
    );
  }

  return (
    <>
      <Title dataTestId="p_creating_organization" messageId="creatingOrganization" />
      <Box height={60}>
        <CircularProgress data-test-id="svg_loading" />
      </Box>
    </>
  );
};

export default SetupOrganization;
