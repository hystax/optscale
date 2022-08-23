import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getUser } from "api";
import { GET_TOKEN, GET_USER } from "api/auth/actionTypes";
import ProfileMenu from "components/ProfileMenu";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

const ProfileMenuContainer = () => {
  const {
    apiData: { userId }
  } = useApiData(GET_TOKEN);
  const {
    apiData: { name = "", email = "" }
  } = useApiData(GET_USER);

  const { isLoading, shouldInvoke } = useApiState(GET_USER);

  const dispatch = useDispatch();

  useEffect(() => {
    if (userId && shouldInvoke) {
      dispatch(getUser(userId));
    }
  }, [userId, dispatch, shouldInvoke]);

  return <ProfileMenu name={name} email={email} isLoading={isLoading} />;
};

export default ProfileMenuContainer;
