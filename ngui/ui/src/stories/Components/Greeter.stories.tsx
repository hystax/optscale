import Greeter from "components/Greeter";

export default {
  component: Greeter
};

export const basic = () => <Greeter form={<div>Form</div>} />;
