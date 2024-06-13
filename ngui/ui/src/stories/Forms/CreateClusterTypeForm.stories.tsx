import CreateClusterTypeForm from "components/forms/CreateClusterTypeForm";

export default {
  component: CreateClusterTypeForm,
  argTypes: {
    isSubmitLoading: { name: "Submit loading", control: "boolean", defaultValue: false }
  }
};

export const basic = (args) => (
  <CreateClusterTypeForm
    onSubmit={() => console.log("On submit")}
    onCancel={() => console.log("On submit")}
    isSubmitLoading={args.isSubmitLoading}
  />
);
