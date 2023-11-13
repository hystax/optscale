import { useDispatch } from "react-redux";
import { resetPassword } from "api";
import { RESET_PASSWORD } from "api/auth/actionTypes";
import ResetPassword from "components/ResetPassword";
import { useApiSendState } from "hooks/useApiSendState";
import { useApiState } from "hooks/useApiState";

const ResetPasswordContainer = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(RESET_PASSWORD);

  const { sendState, onSubmit } = useApiSendState(RESET_PASSWORD, (data) => dispatch(resetPassword(data.email)));

  return <ResetPassword onSubmit={onSubmit} isLoading={isLoading} sendState={sendState} />;
};

export default ResetPasswordContainer;
