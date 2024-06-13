import { FIELD_NAMES } from "./constants";

export type FormValues = {
  [FIELD_NAMES.NAME]: string;
};

export type RenameMlRunChartFormProps = {
  chartName: string;
  onRename: (name: string) => void;
};
