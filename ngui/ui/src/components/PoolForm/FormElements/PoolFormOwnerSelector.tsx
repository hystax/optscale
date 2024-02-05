import { useFormContext, Controller } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContent } from "components/Selector";

const PoolFormOwnerSelector = ({ owners, isLoading = false, isReadOnly = false }) => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Controller
      name="defaultOwnerId"
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field }) => (
        <Selector
          id="pool-owner-selector"
          error={!!errors.defaultOwnerId}
          helperText={errors.defaultOwnerId && errors.defaultOwnerId.message}
          labelMessageId="defaultResourceOwner"
          fullWidth
          isLoading={isLoading}
          readOnly={isReadOnly}
          {...field}
        >
          {owners.map((owner) => (
            <Item key={owner.id} value={owner.id}>
              <ItemContent>{owner.name}</ItemContent>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default PoolFormOwnerSelector;
