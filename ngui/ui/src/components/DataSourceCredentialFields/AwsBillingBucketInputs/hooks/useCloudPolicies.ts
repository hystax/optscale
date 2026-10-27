import { useState } from "react";
import { useCloudPoliciesLazyQuery } from "graphql/__generated__/hooks/restapi";

const useCloudPolicies = () => {
  const [lastRequestedBucket, setLastRequestedBucket] = useState<string | undefined>();
  const [lastRequestedExternalId, setLastRequestedExternalId] = useState<string | undefined>();

  const [getPolicies, { data, loading }] = useCloudPoliciesLazyQuery({
    fetchPolicy: "no-cache",
  });

  const fetchPolicies = (variables: {
    organizationId: string;
    params: { bucket_name: string; cloud_type: string; external_id?: string };
  }) => {
    const { bucket_name: bucket, external_id: externalId } = variables.params;

    if (lastRequestedBucket === bucket && lastRequestedExternalId === externalId) {
      return Promise.resolve({ data });
    }

    setLastRequestedBucket(bucket);
    setLastRequestedExternalId(externalId);
    return getPolicies({ variables });
  };

  return {
    cloudPolicies: data?.cloudPolicies,
    isLoading: loading,
    lastRequestedBucket,
    lastRequestedExternalId,
    fetchPolicies,
  };
};

export default useCloudPolicies;
