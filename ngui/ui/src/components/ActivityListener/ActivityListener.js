import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { GET_TOKEN } from "api/auth/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { dropUserIdentificationIfUniqueIdChanged, identify, initializeHotjar, trackPage } from "utils/analytics";

const ActivityListener = () => {
  const {
    apiData: { userId }
  } = useApiData(GET_TOKEN);
  const { isDemo, organizationId } = useOrganizationInfo();

  // hotjar init
  useEffect(() => {
    initializeHotjar();
  }, []);

  // just uid tracker, to drop user data if uid changed
  useEffect(() => {
    if (userId && !isDemo) {
      dropUserIdentificationIfUniqueIdChanged(userId);
    }
  }, [userId, isDemo]);

  // uid and organization id tracker
  useEffect(() => {
    if (userId && !isDemo && !!organizationId) {
      identify(userId, { userId, organizationId });
    }
  }, [userId, isDemo, organizationId]);

  // page tracker
  const location = useLocation();

  useEffect(() => {
    trackPage();
  }, [location]);

  return null;
};

export default ActivityListener;
