import Percent from "components/Percent";

export default {
  component: Percent,
  argTypes: {
    value: { name: "Value", control: "number", defaultValue: 4.2 }
  }
};

export const basic = () => <Percent value={5} />;

export const withKnobs = (args) => <Percent value={args.value} minimumFractionDigits={2} />;
