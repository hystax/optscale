import React from "react";
import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useFormatProtocolPortAppLabel } from "hooks/useFormatProtocolPortAppLabel";
import { INSECURE_PORTS_MAP } from "utils/constants";

const openPorts = ({ headerDataTestId, accessor = "insecure_ports", disableSortBy = false }) => ({
  Header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="openPorts" />
    </TextWithDataTestId>
  ),
  accessor,
  Cell: ({
    row: {
      original: { insecure_ports: insecurePorts = [] }
    }
  }) => {
    const formatProtocolPortAppLabel = useFormatProtocolPortAppLabel();
    const ports = insecurePorts.filter(({ port }) => port !== "*");
    const shouldRenderAllPortsLabel = insecurePorts.some(({ port }) => port === "*");

    return (
      <Typography component="div">
        {shouldRenderAllPortsLabel && <FormattedMessage id="all" />}
        {ports.map(({ port, protocol }) => (
          <div key={port}>
            {formatProtocolPortAppLabel({
              protocol,
              port,
              app: INSECURE_PORTS_MAP[port]
            })}
          </div>
        ))}
      </Typography>
    );
  },
  disableSortBy
});

export default openPorts;
