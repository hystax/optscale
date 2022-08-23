import React from "react";
import PropTypes from "prop-types";
import { useFormContext, Controller } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";
import { sortObjectsAlphabetically } from "utils/arrays";

const buildSelectorData = (data) => ({
  items: data.map((obj) => ({
    name: obj.name,
    value: obj.id
  }))
});

const sortOwnersAlphabeticallyByName = (owners) => sortObjectsAlphabetically({ array: owners, field: "name" });

const BookEnvironmentFormBookingOwnerSelector = ({ fieldName, isLoading, owners, currentEmployeeId, isSshRequired }) => {
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
      render={({ field: { onChange, ...restControlledFields } }) => {
        const data = buildSelectorData(sortedOwners);
        return isLoading ? (
          <SelectorLoader fullWidth labelId="bookingOwner" isRequired />
        ) : (
          <Selector
            required
            error={!!errors[fieldName]}
            helperText={errors[fieldName] ? errors[fieldName].message : hintDefaultSshWillBeUsed}
            data={data}
            dataTestId="selector_booking_owner"
            labelId="bookingOwner"
            fullWidth
            onChange={(...args) => {
              onChange(...args);
              trigger();
            }}
            {...restControlledFields}
          />
        );
      }}
    />
  );
};
BookEnvironmentFormBookingOwnerSelector.propTypes = {
  fieldName: PropTypes.string.isRequired,
  owners: PropTypes.array.isRequired,
  isLoading: PropTypes.bool,
  currentEmployeeId: PropTypes.string,
  isSshRequired: PropTypes.bool
};

export default BookEnvironmentFormBookingOwnerSelector;
