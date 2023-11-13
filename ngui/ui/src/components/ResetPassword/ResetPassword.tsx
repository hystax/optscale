import Greeter from "components/Greeter";
import ResetPasswordForm from "components/ResetPasswordForm";

const ResetPassword = ({ onSubmit, isLoading, sendState }) => (
  <Greeter form={<ResetPasswordForm onSubmit={onSubmit} isLoading={isLoading} sendState={sendState} />} />
);

export default ResetPassword;
