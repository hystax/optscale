import React from "react";
import { FormattedMessage, FormattedNumber } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";

const mlGpuMemoryUsage = ({ headerDataTestId = "lbl_gpu_memory_usage", accessorKey = "gpu_memory_usage" } = {}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="gpuMemoryUsage" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ cell }) => <FormattedNumber value={cell.getValue()} format="percentage" />
});

export default mlGpuMemoryUsage;
