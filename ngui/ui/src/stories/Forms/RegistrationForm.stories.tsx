import RegistrationForm from "components/RegistrationForm";

export default {
  component: RegistrationForm,
  argTypes: {
    isLoading: { name: "Loading", control: "boolean", defaultValue: false },
    sendState: { name: "Send state", control: "text", defaultValue: "unknown" }
  }
};

export const basic = (args) => (
  <RegistrationForm isLoading={args.isLoading} onSubmit={() => console.log("submit")} sendState={args.sendState} />
);
