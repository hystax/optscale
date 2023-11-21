import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useRecommendationServices } from "hooks/useRecommendationServices";

const Cell = ({ cell }) => {
  const services = useRecommendationServices();

  return (cell.getValue() || [])
    .filter((service) => !!services[service])
    .sort()
    .map((service) => {
      const { name, type } = services[service];
      return type ? (
        <CloudLabel key={name} name={<FormattedMessage id={name} />} type={type} disableLink />
      ) : (
        <FormattedMessage key={name} id={name} />
      );
    });
};

const services = ({ headerDataTestId, accessorKey }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="applicableServices" />
    </TextWithDataTestId>
  ),
  accessorKey,
  enableSorting: false,
  cell: Cell
});

export default services;
