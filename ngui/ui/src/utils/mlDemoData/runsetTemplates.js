import { activationFunctionsDatasetsRunsets, awsGpuInstancesRunsets, priceSpeedBalanceRunsets } from "./runsets";

const getRunsetsId = (runsets) => runsets.map(({ id }) => id);

const runsetTemplates = [
  {
    id: "826f8381-9a12-4854-8274-9ca421b19856",
    name: "AWS GPU Instances",
    applications: [
      "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
      "2e0815a2-72d2-418b-afad-bedc99a5e9d2",
      "3e0815a2-72d2-418b-afad-bedc99a5e9d2"
    ],
    runsets: getRunsetsId(awsGpuInstancesRunsets)
  },
  {
    id: "ac2adbf7-0793-475d-932c-6a899ceb9c30",
    name: "Activation functions/Datasets",
    total_cost: 82523,
    runs_count: 53,
    applications: [
      "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
      "2e0815a2-72d2-418b-afad-bedc99a5e9d2",
      "3e0815a2-72d2-418b-afad-bedc99a5e9d2"
    ],
    runsets: getRunsetsId(activationFunctionsDatasetsRunsets)
  },
  {
    id: "5c7b5a5a-866e-4916-adc4-b56a1f1adb0a",
    name: "Price/Speed balance",
    total_cost: 14717,
    runs_count: 42,
    applications: [
      "1e0815a2-72d2-418b-afad-bedc99a5e9d2",
      "2e0815a2-72d2-418b-afad-bedc99a5e9d2",
      "4e0815a2-72d2-418b-afad-bedc99a5e9d2"
    ],
    runsets: getRunsetsId(priceSpeedBalanceRunsets)
  }
];

export { runsetTemplates };
