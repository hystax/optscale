import SendVerificationCodeForm from "components/forms/SendVerificationCodeForm";

export default {
  component: SendVerificationCodeForm,
  argTypes: {
    isLoading: { name: "Loading", control: "boolean", defaultValue: false },
    sendState: { name: "Send state", control: "text", defaultValue: "unknown" }
  }
};

export const basic = (args) => (
  <SendVerificationCodeForm isLoading={args.isLoading} onSubmit={() => console.log("submit")} sendState={args.sendState} />
);
