import { FormattedMessage } from "react-intl";
import FormattedDigitalUnit from "components/FormattedDigitalUnit";
import TextWithDataTestId from "components/TextWithDataTestId";

const mlIOPSCap = ({ headerDataTestId = "lbl_IOPS_cap", ioAccessor = "io", rwAccessor = "rw" } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="IOPSCap" />
    </TextWithDataTestId>
  ),
  id: "IOPSCap",
  style: {
    whiteSpace: "nowrap"
  },
  cell: ({ row: { original } }) => {
    const inOut = original[ioAccessor];
    const readWrite = original[rwAccessor];

    return (
      <FormattedMessage
        id="value / value"
        values={{
          value1: <FormattedMessage id="xIops" values={{ x: inOut }} />,
          value2: (
            <FormattedMessage
              id="valuePerSec"
              values={{
                value: <FormattedDigitalUnit value={readWrite} />
              }}
            />
          )
        }}
      />
    );
  }
});

export default mlIOPSCap;
