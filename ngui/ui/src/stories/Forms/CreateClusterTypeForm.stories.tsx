import CreateClusterTypeForm from "components/CreateClusterTypeForm";
import { KINDS } from "stories";

export default {
  title: `${KINDS.FORMS}/CreateClusterTypeForm`,
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
