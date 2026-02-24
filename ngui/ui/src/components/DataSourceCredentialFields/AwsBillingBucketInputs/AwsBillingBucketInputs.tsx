import { useMemo } from "react";
import { Box, CircularProgress, FormControl } from "@mui/material";
import { useFormContext } from "react-hook-form";
import CodeBlock from "components/CodeBlock";
import { AwsAssumedRoleCredentialsModal } from "components/SideModalManager/SideModals";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { AWS_CNR } from "utils/constants";
import AwsBillingBucket, { FIELD_NAMES as AWS_BILLING_BUCKET_FIELD_NAMES } from "../AwsBillingBucket";
import useCloudPolicies from "./hooks/useCloudPolicies";

const CODE_BLOCK_HEIGHT = "300px";

const AwsBillingBucketInputs = ({ showAssumedRoleCredentialsInModal = false }) => {
  const { watch } = useFormContext();
  const { organizationId } = useOrganizationInfo();
  const { cloudPolicies, lastRequestedBucket, isLoading, fetchPolicies } = useCloudPolicies();

  const openSideModal = useOpenSideModal();

  const bucketName = watch(AWS_BILLING_BUCKET_FIELD_NAMES.BUCKET_NAME);

  const text = useMemo(() => (cloudPolicies ? JSON.stringify(cloudPolicies, null, 2) : ""), [cloudPolicies]);

  const handleClick = async () => {
    try {
      const { data } = await fetchPolicies({
        organizationId,
        params: { bucket_name: bucketName, cloud_type: AWS_CNR },
      });

      if (showAssumedRoleCredentialsInModal) {
        openSideModal(AwsAssumedRoleCredentialsModal, {
          name: bucketName,
          text: JSON.stringify(data?.cloudPolicies, null, 2),
        });
      }
    } catch (error) {
      console.error("Error while loading cloudPolicies:", error);
    }
  };

  const canShowResult = (isLoading || !!cloudPolicies) && bucketName === lastRequestedBucket;

  return (
    <>
      <AwsBillingBucket showRoleButton={{ onClick: handleClick, isDisabled: !bucketName, isLoading }} />
      <Box>
        {canShowResult && !showAssumedRoleCredentialsInModal && (
          <FormControl fullWidth>
            {isLoading ? (
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  height: CODE_BLOCK_HEIGHT,
                  backgroundColor: (theme) => theme.palette.background.default,
                }}
              >
                <CircularProgress />
              </Box>
            ) : (
              <CodeBlock text={text} height={CODE_BLOCK_HEIGHT} />
            )}
          </FormControl>
        )}
      </Box>
    </>
  );
};

export default AwsBillingBucketInputs;
