import CriticalInput, { FIELD_NAME as CRITICAL_FIELD_NAME } from "./CriticalInput";
import FormButtons from "./FormButtons";
import RequiringAttentionInput, { FIELD_NAME as REQUIRING_ATTENTION_FIELD_NAME } from "./RequiringAttentionInput";

const FIELD_NAMES = Object.freeze({
  CRITICAL_FIELD_NAME,
  REQUIRING_ATTENTION_FIELD_NAME
});

export { CriticalInput, RequiringAttentionInput, FormButtons, FIELD_NAMES };
