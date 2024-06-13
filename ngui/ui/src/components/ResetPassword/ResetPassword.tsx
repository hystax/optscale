import ResetPasswordForm from "components/forms/ResetPasswordForm";
import Greeter from "components/Greeter";

const ResetPassword = ({ onSubmit, isLoading, sendState }) => (
  <Greeter form={<ResetPasswordForm onSubmit={onSubmit} isLoading={isLoading} sendState={sendState} />} />
);

export default ResetPassword;
