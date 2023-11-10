import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import CloudTypeIcon from "components/CloudTypeIcon";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";

export const FIELD_NAME = "instanceType";

const LABEL_ID = "instanceType";

const InstanceTypeField = ({ instanceTypes, isLoading }) => {
  const intl = useIntl();

  const {
    control,
    formState: { errors }
  } = useFormContext();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field: { onChange, ...rest } }) =>
        isLoading ? (
          <SelectorLoader readOnly fullWidth labelId={LABEL_ID} isRequired />
        ) : (
          <Selector
            dataTestId="selector_instance_type"
            fullWidth
            required
            menuItemIcon={{
              component: CloudTypeIcon,
              getComponentProps: (itemInfo) => ({
                type: itemInfo.type
              })
            }}
            error={!!errors[FIELD_NAME]}
            helperText={errors?.[FIELD_NAME]?.message}
            data={{
              items: instanceTypes.map(({ name, cloud_type: dataSourceType }) => ({
                name,
                value: name,
                type: dataSourceType
              }))
            }}
            labelId={LABEL_ID}
            onChange={onChange}
            {...rest}
          />
        )
      }
    />
  );
};

export default InstanceTypeField;
