import TypographyLoader from "components/TypographyLoader";

export default {
  component: TypographyLoader,
  argTypes: {
    variant: {
      name: "Color",
      control: "select",
      options: ["h1", "h2", "h3", "h4", "h5", "h6", "subtitle1", "subtitle2", "body1", "body2", "caption"],
      defaultValue: "body1"
    },
    lineCount: { name: "Line count", control: "number", defaultValue: 5 }
  }
};

export const basic = () => <TypographyLoader variant="body1" linesCount={1} />;

export const withKnobs = (args) => <TypographyLoader variant={args.variant} linesCount={args.lineCount} />;
