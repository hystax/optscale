import { GET_TOKEN } from "api/auth/actionTypes";
import ProfileMenu from "components/ProfileMenu";
import { useApiData } from "hooks/useApiData";
import UserService from "services/UserService";

const ProfileMenuContainer = () => {
  const {
    apiData: { userId }
  } = useApiData(GET_TOKEN);

  const { useGet } = UserService();
  const {
    isDataReady,
    user: { name = "", email = "" }
  } = useGet(userId);

  return <ProfileMenu name={name} email={email} isLoading={!isDataReady} />;
};

export default ProfileMenuContainer;
