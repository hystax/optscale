import { FormattedMessage, useIntl } from "react-intl";
import FormattedDigitalUnit, { SI_UNITS } from "components/FormattedDigitalUnit";
import { STATUS } from "components/S3DuplicateFinderCheck/utils";
import TextWithDataTestId from "components/TextWithDataTestId";
import { CELL_EMPTY_VALUE } from "utils/tables";

const Stats = ({ stats }) => {
  const intl = useIntl();

  const {
    total_objects: totalObjects,
    duplicated_objects: duplicatedObjects,
    total_size: totalSize,
    duplicates_size: duplicatesSize
  } = stats;

  const getObjectsCountLabel = () => {
    const valueLabel = intl.formatMessage({ id: "value / value" }, { value1: duplicatedObjects, value2: totalObjects });
    const sizeLabel = intl.formatMessage({ id: "objects" }).toLocaleLowerCase();

    return `${valueLabel} ${sizeLabel}`;
  };

  return (
    <>
      <div>{getObjectsCountLabel()}</div>
      <div>
        <FormattedMessage
          id="value / value"
          values={{
            value1: <FormattedDigitalUnit value={duplicatesSize} baseUnit={SI_UNITS.BYTE} />,
            value2: <FormattedDigitalUnit value={totalSize} baseUnit={SI_UNITS.BYTE} />
          }}
        />
      </div>
    </>
  );
};

const duplicates = () => ({
  header: (
    <TextWithDataTestId dataTestId="duplicates">
      <FormattedMessage id="duplicates" />
    </TextWithDataTestId>
  ),
  id: "duplicates",
  cell: ({
    row: {
      original: { stats, status }
    }
  }) => (status === STATUS.SUCCESS ? <Stats stats={stats} /> : CELL_EMPTY_VALUE)
});

export default duplicates;
