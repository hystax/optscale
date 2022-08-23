import React from "react";
import ResourceMetrics from "components/ResourceMetrics";
import { boolean, object } from "@storybook/addon-knobs";

export default {
  title: "Components/ResourceMetrics"
};

const cpuData = [
  {
    date: 1630173600,
    value: 1.1201120068629582
  },
  {
    date: 1630216800,
    value: 1.102341835697492
  },
  {
    date: 1630260000,
    value: 1.1368501608570416
  },
  {
    date: 1630303200,
    value: 1.1711093087991078
  },
  {
    date: 1630346400,
    value: 1.135535742925561
  }
];
const ramData = [
  { date: 1627797600, value: 0 },
  { date: 1627840800, value: 0.23007638889049606708 },
  { date: 1628143200, value: 0 },
  { date: 1628575200, value: 0.123 },
  { date: 1628704800, value: 0.4569126063336928 }
];
const diskReadIoData = [
  { date: 1627797600, value: 0 },
  { date: 1627840800, value: 0.23007638889049606708 },
  { date: 1628143200, value: 0 },
  { date: 1628575200, value: 0.123 },
  { date: 1628704800, value: 0.4569126063336928 }
];
const diskWriteIoData = [
  { date: 1627797600, value: 0.3305999754617612 },
  { date: 1627840800, value: 0.3357913065701723 },
  { date: 1628056800, value: 0.255905126221478 },
  { date: 1628143200, value: 0.39486554202934104 },
  { date: 1628186400, value: 0.4847914256776373 },
  { date: 1628575200, value: 0.4485174637908737 },
  { date: 1628704800, value: 1.4569126063336928 }
];
const networkInIoData = [
  { date: 1627797600, value: 0.3305999754617612 },
  { date: 1627840800, value: 0.3357913065701723 },
  { date: 1628056800, value: 0.255905126221478 },
  { date: 1628143200, value: 0.39486554202934104 },
  { date: 1628186400, value: 0.4847914256776373 }
];
const networkOutIoData = [
  { date: 1627797600, value: 0.1305999754617612 },
  { date: 1627840800, value: 0.5357913065701723 },
  { date: 1628056800, value: 0.155905126221478 },
  { date: 1628143200, value: 0.69486554202934104 },
  { date: 1628186400, value: 0.2847914256776373 }
];

export const noData = () => <ResourceMetrics metrics={{}} />;

export const withData = () => (
  <ResourceMetrics
    metrics={{
      cpu: cpuData,
      ram: ramData,
      disk_read_io: diskReadIoData,
      disk_write_io: diskWriteIoData,
      network_in_io: networkInIoData,
      network_out_io: networkOutIoData
    }}
  />
);

const WithKnobsLayout = ({ children }) => (
  <div>
    <p>Open knobs to be able to edit data</p>
    {children}
  </div>
);

export const dynamicCpu = () => (
  <WithKnobsLayout>
    <ResourceMetrics
      metrics={{
        cpu: object("metric data", cpuData)
      }}
    />
  </WithKnobsLayout>
);

export const dynamicMemory = () => (
  <WithKnobsLayout>
    <ResourceMetrics
      metrics={{
        ram: object("metric data", ramData)
      }}
    />
  </WithKnobsLayout>
);

export const dynamicDiskIO = () => (
  <WithKnobsLayout>
    <ResourceMetrics
      metrics={{
        disk_read_io: object("disk_read_io data", diskReadIoData),
        disk_write_io: object("disk_write_io data", diskWriteIoData)
      }}
    />
  </WithKnobsLayout>
);

export const dynamicNetwork = () => (
  <WithKnobsLayout>
    <ResourceMetrics
      metrics={{
        network_in_io: object("network_in_io data", networkInIoData),
        network_out_io: object("network_out_io data", networkOutIoData)
      }}
    />
  </WithKnobsLayout>
);

export const loading = () => <ResourceMetrics metrics={{}} isLoading />;
