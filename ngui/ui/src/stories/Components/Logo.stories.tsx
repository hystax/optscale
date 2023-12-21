import Logo from "components/Logo";

export default {
  component: Logo,
  argTypes: {
    size: {
      name: "Size",
      control: "select",
      options: ["small", "medium"],
      defaultValue: "small"
    },
    active: { name: "Active", control: "boolean", defaultValue: false },
    white: { name: "White", control: "boolean", defaultValue: false }
  }
};

export const basic = () => <Logo />;

export const withKnobs = (args) => <Logo active={args.active} white={args.white} size={args.size} />;
