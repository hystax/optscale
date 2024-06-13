import { FIELD_NAMES } from "./constants";
import { FormValues } from "./types";

export const getDefaultValues = ({ cpuHour, memoryMbHour }: { cpuHour: number; memoryMbHour: number }): FormValues => ({
  [FIELD_NAMES.CPU_PER_HOUR]: cpuHour ? String(cpuHour) : "0",
  [FIELD_NAMES.MEMORY_PER_HOUR]: memoryMbHour ? String(memoryMbHour) : "0"
});
