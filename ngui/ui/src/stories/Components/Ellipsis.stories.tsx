import Ellipsis from "components/Ellipsis";

export default {
  component: Ellipsis,
  argTypes: {
    variant: {
      name: "Variant",
      control: "select",
      options: [
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "subtitle1",
        "subtitle2",
        "body1",
        "body2",
        "caption",
        "button",
        "overline",
        "inherit"
      ],
      defaultValue: "body2"
    },
    component: {
      name: "Component",
      control: "select",
      options: ["p", "div", "span"],
      defaultValue: "span"
    },
    className: {
      name: "Class name",
      control: "select",
      options: ["insideBrackets", "default"],
      defaultValue: "default"
    }
  }
};

export const basic = () => <Ellipsis />;

export const withKnobs = (args) => <Ellipsis variant={args.variant} component={args.component} className={args.className} />;
