import { useGet } from "./useGet";

export const useUserAssignment = () => {
  const { loading, error, data, refetch } = useGet("/jira_bus/v2/user_assignment");

  const userIsNotFound = error?.error_code === "OJ0008";

  return {
    loading,
    error: userIsNotFound ? null : error,
    data: userIsNotFound ? {} : data,
    refetch
  };
};
