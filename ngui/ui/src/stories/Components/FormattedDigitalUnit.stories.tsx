import FormattedDigitalUnit, { IEC_UNITS, SI_UNITS } from "components/FormattedDigitalUnit";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/FormattedDigitalUnit`,
  argTypes: {
    iec: {
      name: "IEC units",
      control: "select",
      options: Object.values(IEC_UNITS)
    },
    si: {
      name: "SI units",
      control: "select",
      options: Object.values(SI_UNITS)
    },
    value: { name: "Value", control: "number", defaultValue: 0 }
  }
};

export const iecDigitalUnitWithKnobs = (args) => <FormattedDigitalUnit value={args.value} baseUnit={args.iec} />;

export const siDigitalUnitWithKnobs = (args) => <FormattedDigitalUnit value={args.value} baseUnit={args.si} />;
