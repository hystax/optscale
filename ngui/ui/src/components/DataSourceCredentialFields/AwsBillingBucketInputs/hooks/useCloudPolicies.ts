import { useState } from "react";
import { useCloudPoliciesLazyQuery } from "graphql/__generated__/hooks/restapi";

const useCloudPolicies = () => {
  const [lastRequestedBucket, setLastRequestedBucket] = useState<string | undefined>();

  const [getPolicies, { data, loading }] = useCloudPoliciesLazyQuery({
    fetchPolicy: "no-cache",
  });

  const fetchPolicies = (variables: { organizationId: string; params: { bucket_name: string; cloud_type: string } }) => {
    const bucket = variables.params.bucket_name;

    if (lastRequestedBucket === bucket) {
      return Promise.resolve({ data });
    }

    setLastRequestedBucket(bucket);
    return getPolicies({ variables });
  };

  return {
    cloudPolicies: data?.cloudPolicies,
    isLoading: loading,
    lastRequestedBucket,
    fetchPolicies,
  };
};

export default useCloudPolicies;
