import ProfileMenu from "components/ProfileMenu";
import { useGetToken } from "hooks/useGetToken";
import UserService from "services/UserService";

const ProfileMenuContainer = () => {
  const { userId } = useGetToken();

  const { useGet } = UserService();
  const {
    isDataReady,
    user: { name = "", email = "" },
  } = useGet(userId);

  return <ProfileMenu name={name} email={email} isLoading={!isDataReady} />;
};

export default ProfileMenuContainer;
