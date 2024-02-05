import { useFormContext, Controller } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContent } from "components/Selector";
import { sortObjectsAlphabetically } from "utils/arrays";

const sortOwnersAlphabeticallyByName = (owners) => sortObjectsAlphabetically({ array: owners, field: "name" });

const BookEnvironmentFormBookingOwnerSelector = ({
  fieldName,
  isLoading = false,
  owners,
  currentEmployeeId = "",
  isSshRequired,
  readOnly = false
}) => {
  const {
    control,
    trigger,
    watch,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  const sortedOwners = sortOwnersAlphabeticallyByName(owners);

  const watchValue = watch(fieldName);
  const hintDefaultSshWillBeUsed =
    isSshRequired && currentEmployeeId !== watchValue && watchValue !== ""
      ? intl.formatMessage({ id: "defaultSshKeyWillBeUsed" })
      : null;

  return (
    <Controller
      name={fieldName}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        validate: {
          hasDefaultSshKey: (value) => {
            const isCurrentUser = currentEmployeeId === value;
            const hasDefaultSshKey =
              (owners.find(({ id }) => id === value) || { default_ssh_key_id: null }).default_ssh_key_id !== null;
            return !isSshRequired || isCurrentUser || hasDefaultSshKey || intl.formatMessage({ id: "userHasNoDefaultSshKey" });
          }
        }
      }}
      render={({ field: { onChange, ...restControlledFields } }) => (
        <Selector
          id="booking-owner-selector"
          fullWidth
          required
          error={!!errors[fieldName]}
          helperText={errors[fieldName] ? errors[fieldName].message : hintDefaultSshWillBeUsed}
          labelMessageId="bookingOwner"
          onChange={(...args) => {
            onChange(...args);
            trigger();
          }}
          readOnly={readOnly}
          isLoading={isLoading}
          {...restControlledFields}
        >
          {sortedOwners.map(({ id, name }) => (
            <Item key={id} value={id}>
              <ItemContent>{name}</ItemContent>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default BookEnvironmentFormBookingOwnerSelector;
