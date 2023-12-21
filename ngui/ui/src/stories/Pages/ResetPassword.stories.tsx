import ResetPassword from "components/ResetPassword";

export default {
  component: ResetPassword,
  argTypes: {
    isLoading: { name: "Loading", control: "boolean", defaultValue: false }
  }
};

export const basic = (args) => (
  <ResetPassword isLoading={args.isLoading} onSubmit={() => console.log("submit")} sendState="SUCCESS" />
);
