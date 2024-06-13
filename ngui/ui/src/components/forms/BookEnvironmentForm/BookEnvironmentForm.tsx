import { useEffect } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { useIntl } from "react-intl";
import {
  secondsToMilliseconds,
  areIntervalsOverlapping,
  addYears,
  roundTimeToInterval,
  INTERVAL_ENVIRONMENT
} from "utils/datetime";
import { FIELD_NAMES } from "./constants";
import {
  BookSinceTimePicker,
  BookUntilTimePicker,
  BookingOwnerSelector,
  EnvironmentSshKeyField,
  FormButtons
} from "./FormElements";
import { BookEnvironmentFormProps, FormValues } from "./types";
import { getDefaultValues } from "./utils";

// This date will be used to validate «0» released_at and «undefined» bookUntil timestamps
// 0 and undefined mean that resource is booked forever
const DISTANT_FUTURE_DATE = addYears(new Date(), 50);

const findOverlappingInterval = (sinceTimestamp, untilTimestamp, allBookings) => {
  // Handle "undefined" until timestamp (which means that resource is booked forever)
  const untilTimestampSafe = untilTimestamp ? new Date(untilTimestamp) : DISTANT_FUTURE_DATE;
  // Handle "undefined" since timestamp (which means that resource is booked from that exact moment)
  const sinceTimestampSafe = new Date(sinceTimestamp || 0);

  return allBookings.find(({ acquired_since: acquiredSince, released_at: acquiredUntil }) =>
    areIntervalsOverlapping(
      {
        start: new Date(secondsToMilliseconds(acquiredSince)),
        // Handle "0" until timestamp (which means that resource is booked forever)
        end: acquiredUntil === 0 ? DISTANT_FUTURE_DATE : new Date(secondsToMilliseconds(acquiredUntil))
      },
      {
        start: sinceTimestampSafe,
        end: untilTimestampSafe
      }
    )
  );
};

const BookEnvironmentForm = ({
  isLoadingProps,
  onSubmit,
  isEnvironmentAvailable,
  allBookings,
  onCancel,
  owners,
  defaultBookingOwner,
  canSetBookingOwner,
  isSshRequired,
  currentEmployeeSshKeys,
  isGetSshKeysReady
}: BookEnvironmentFormProps) => {
  const intl = useIntl();

  const methods = useForm<FormValues>({
    defaultValues: getDefaultValues({
      bookSince: isEnvironmentAvailable ? undefined : roundTimeToInterval(+new Date(), INTERVAL_ENVIRONMENT)
    })
  });

  const { handleSubmit, reset, watch } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      [FIELD_NAMES.BOOKING_OWNER]: defaultBookingOwner?.id || ""
    }));
  }, [defaultBookingOwner?.id, reset]);

  const watchBookingOwner = watch(FIELD_NAMES.BOOKING_OWNER);
  const isBookingForMyself = watchBookingOwner === defaultBookingOwner?.id;

  const {
    isBookEnvironmentLoading = false,
    isGetAuthorizedEmployeesLoading = false,
    isCreateSshKeyLoading = false
  } = isLoadingProps;

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <BookingOwnerSelector
          owners={owners}
          currentEmployeeId={defaultBookingOwner?.id}
          isSshRequired={isSshRequired}
          isLoading={isGetAuthorizedEmployeesLoading}
          readOnly={!canSetBookingOwner}
        />
        <BookSinceTimePicker
          validate={{
            startDateMustNotBeEqualToEndDate: (sinceTimestamp, formValues) => {
              if (sinceTimestamp === undefined) {
                return true;
              }
              return (
                sinceTimestamp !== formValues[FIELD_NAMES.BOOK_UNTIL] ||
                intl.formatMessage({ id: "startDateMustNotBeEqualToEndDate" })
              );
            },
            isLessThanEndDate: (value, formValues) => {
              const bookUntil = formValues[FIELD_NAMES.BOOK_UNTIL];

              if (!(bookUntil && value)) {
                return true;
              }

              return value <= bookUntil || intl.formatMessage({ id: "startDateMustNotBeGreaterThanEndTime" });
            },
            isNotBooked: (sinceTimestamp, formValues) => {
              const overlappingInterval = findOverlappingInterval(
                sinceTimestamp,
                formValues[FIELD_NAMES.BOOK_UNTIL],
                allBookings
              );

              return !overlappingInterval || intl.formatMessage({ id: "selectedIntervalIsOverlappingWithExistedBooking" });
            }
          }}
        />
        <BookUntilTimePicker
          validate={{
            endDateMustNotBeEqualToStartDate: (untilTimestamp, formValues) => {
              if (untilTimestamp === undefined) {
                return true;
              }
              return (
                untilTimestamp !== formValues[FIELD_NAMES.BOOK_SINCE] ||
                intl.formatMessage({ id: "endDateMustNotBeEqualToStartDate" })
              );
            },
            isGreaterThanStartDate: (value, formValues) => {
              const bookSince = formValues[FIELD_NAMES.BOOK_SINCE];
              if (!(bookSince && value)) {
                return true;
              }
              return value >= bookSince || intl.formatMessage({ id: "endDateMustBeGreaterThanStartTime" });
            },
            isNotBooked: (untilTimestamp, formValues) => {
              const overlappingInterval = findOverlappingInterval(
                formValues[FIELD_NAMES.BOOK_SINCE],
                untilTimestamp,
                allBookings
              );

              return !overlappingInterval || intl.formatMessage({ id: "selectedIntervalIsOverlappingWithExistedBooking" });
            }
          }}
        />
        {isSshRequired && isBookingForMyself ? (
          <EnvironmentSshKeyField
            sshKeys={currentEmployeeSshKeys}
            isGetSshKeysReady={isGetSshKeysReady}
            defaultKeyId={defaultBookingOwner?.default_ssh_key_id}
          />
        ) : null}
        <FormButtons
          isLoading={isBookEnvironmentLoading || isGetAuthorizedEmployeesLoading || isCreateSshKeyLoading}
          onCancel={onCancel}
        />
      </form>
    </FormProvider>
  );
};

export default BookEnvironmentForm;
