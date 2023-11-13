import ResetPasswordForm from "components/ResetPasswordForm";
import { KINDS } from "stories";

export default {
  title: `${KINDS.FORMS}/ResetPasswordForm`,
  argTypes: {
    isLoading: { name: "Loading", control: "boolean", defaultValue: false },
    sendState: { name: "Send state", control: "text", defaultValue: "unknown" }
  }
};

export const basic = (args) => (
  <ResetPasswordForm isLoading={args.isLoading} onSubmit={() => console.log("submit")} sendState={args.sendState} />
);
