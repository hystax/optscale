import PasswordRecovery from "components/PasswordRecovery";

export default {
  component: PasswordRecovery,
  argTypes: {
    isLoading: { name: "Loading", control: "boolean", defaultValue: false }
  }
};

export const basic = (args) => (
  <PasswordRecovery isLoading={args.isLoading} onSubmit={() => console.log("submit")} sendState="SUCCESS" />
);
