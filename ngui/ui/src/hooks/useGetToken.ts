import { useSelector } from "react-redux";
import { INITIAL } from "containers/InitializeContainer/redux";

export const useGetToken = () => {
  const userId = useSelector((state) => state[INITIAL]?.user_id);
  const token = useSelector((state) => state[INITIAL]?.token);
  const userEmail = useSelector((state) => state[INITIAL]?.user_email);
  const caveats = useSelector((state) => state[INITIAL]?.caveats);

  return {
    userId,
    token,
    userEmail,
    caveats,
  };
};
