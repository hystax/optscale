import { useUserAssignment } from "./useUserAssignment";

export const useIsUserConnectedToOptscale = () => {
  const { loading, error, data: userAssignmentData, refetch } = useUserAssignment();

  const getIsConnected = () => {
    if (!userAssignmentData) {
      return null;
    }
    return { isConnected: !!userAssignmentData.auth_user_id };
  };

  return {
    loading,
    refetch,
    error,
    data: getIsConnected()
  };
};
