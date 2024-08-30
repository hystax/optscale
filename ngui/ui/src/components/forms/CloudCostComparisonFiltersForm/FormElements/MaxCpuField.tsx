import { useEffect } from "react";
import { useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import { NumberInput } from "components/forms/common/fields";
import { isWholeNumber } from "utils/validation";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.MAX_CPU;
const MIN_CPU_FIELD_NAME = FIELD_NAMES.MIN_CPU;

const MaxCpuField = () => {
  const {
    formState: { isSubmitted },
    watch,
    trigger
  } = useFormContext();

  const intl = useIntl();

  const minCpu = watch(MIN_CPU_FIELD_NAME);

  useEffect(() => {
    if (isSubmitted) {
      trigger(FIELD_NAME);
    }
  }, [isSubmitted, minCpu, trigger]);

  return (
    <NumberInput
      name={FIELD_NAME}
      label={<FormattedMessage id="maxCpu" />}
      required
      min={0}
      validate={{
        whole: (value) => (isWholeNumber(value) ? intl.formatMessage({ id: "wholeNumber" }) : true),
        moreThanMinCpu: (value) =>
          minCpu.trim() === "" || value.trim() === "" || Number(value) >= Number(minCpu)
            ? true
            : intl.formatMessage(
                { id: "fieldMoreThanOrEqualToField" },
                {
                  fieldName1: intl.formatMessage({ id: "maxCpu" }),
                  fieldName2: intl.formatMessage({ id: "minCpu" })
                }
              )
      }}
    />
  );
};

export default MaxCpuField;
