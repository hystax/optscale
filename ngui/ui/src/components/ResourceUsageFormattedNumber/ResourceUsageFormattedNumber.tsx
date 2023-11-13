import { FormattedNumber } from "react-intl";

const ResourceUsageFormattedNumber = ({ usage, unit }) => (
  <span>
    <FormattedNumber value={usage} maximumFractionDigits={2} /> {unit}
  </span>
);

export default ResourceUsageFormattedNumber;
