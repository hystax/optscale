import { useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import { Selector } from "components/forms/common/fields";
import { ItemContent } from "components/Selector";
import { FIELD_NAMES } from "../constants";
import { BookingOwnerSelectorProps } from "../types";
import { sortOwnersAlphabeticallyByName } from "../utils";

const FIELD_NAME = FIELD_NAMES.BOOKING_OWNER;

const BookingOwnerSelector = ({
  owners,
  currentEmployeeId = "",
  isSshRequired = false,
  isLoading = false,
  readOnly = false
}: BookingOwnerSelectorProps) => {
  const { trigger, watch } = useFormContext();

  const intl = useIntl();

  const sortedOwners = sortOwnersAlphabeticallyByName(owners);

  const watchValue = watch(FIELD_NAME);
  const hintDefaultSshWillBeUsed =
    isSshRequired && currentEmployeeId !== watchValue && watchValue !== ""
      ? intl.formatMessage({ id: "defaultSshKeyWillBeUsed" })
      : null;

  return (
    <Selector
      name={FIELD_NAME}
      required
      validate={{
        hasDefaultSshKey: (value) => {
          const isCurrentUser = currentEmployeeId === value;
          const hasDefaultSshKey =
            (owners.find(({ id }) => id === value) || { default_ssh_key_id: null }).default_ssh_key_id !== null;
          return !isSshRequired || isCurrentUser || hasDefaultSshKey || intl.formatMessage({ id: "userHasNoDefaultSshKey" });
        }
      }}
      id="booking-owner-selector"
      fullWidth
      labelMessageId="bookingOwner"
      helperText={hintDefaultSshWillBeUsed}
      onChange={() => {
        trigger();
      }}
      readOnly={readOnly}
      isLoading={isLoading}
      items={sortedOwners.map(({ id, name }) => ({
        value: id,
        content: <ItemContent>{name}</ItemContent>
      }))}
    />
  );
};

export default BookingOwnerSelector;
