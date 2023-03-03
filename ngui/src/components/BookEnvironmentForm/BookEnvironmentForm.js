import React, { useEffect } from "react";
import { Box } from "@mui/material";
import PropTypes from "prop-types";
import { FormProvider, useForm } from "react-hook-form";
import { useIntl } from "react-intl";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import EnvironmentSshKey from "components/EnvironmentSshKey";
import FormButtonsWrapper from "components/FormButtonsWrapper";

import SelectorLoader from "components/SelectorLoader";
import {
  secondsToMilliseconds,
  areIntervalsOverlapping,
  addYears,
  getNYearsFromToday,
  millisecondsToSeconds,
  roundTimeToInterval,
  INTERVAL_ENVIRONMENT
} from "utils/datetime";
import useStyles from "./BookEnvironmentForm.styles";
import BookEnvironmentFormBookDateTimePicker from "./Fields/BookEnvironmentFormBookDateTimePicker";
import BookEnvironmentFormBookingOwnerReadOnlyInput from "./Fields/BookEnvironmentFormBookingOwnerReadOnlyInput";
import BookEnvironmentFormBookingOwnerSelector from "./Fields/BookEnvironmentFormBookingOwnerSelector";

const BOOKING_OWNER = "bookingOwnerId";
const BOOK_SINCE_PICKER_NAME = "bookSince";
const BOOK_UNTIL_PICKER_NAME = "bookUntil";

// This date will be used to validate «0» released_at and «undefined» bookUntil timestamps
// 0 and undefined mean that resource is booked forever
const DISTANT_FUTURE_DATE = addYears(new Date(), 50);

const maxPickerDate = getNYearsFromToday(5);

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
}) => {
  const { classes } = useStyles();
  const intl = useIntl();

  const methods = useForm({
    defaultValues: {
      [BOOKING_OWNER]: "",
      [BOOK_SINCE_PICKER_NAME]: isEnvironmentAvailable ? undefined : roundTimeToInterval(+new Date(), INTERVAL_ENVIRONMENT),
      [BOOK_UNTIL_PICKER_NAME]: undefined
    },
    shouldUnregister: true
  });

  const { handleSubmit, reset, watch } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      [BOOKING_OWNER]: defaultBookingOwner?.id || ""
    }));
  }, [defaultBookingOwner?.id, reset]);

  const watchBookingOwner = watch(BOOKING_OWNER);
  const isBookingForMyself = watchBookingOwner === defaultBookingOwner?.id;

  const {
    isBookEnvironmentLoading = false,
    isGetAuthorizedEmployeesLoading = false,
    isCreateSshKeyLoading = false
  } = isLoadingProps;

  const renderBookingOwnerField = () =>
    canSetBookingOwner ? (
      <BookEnvironmentFormBookingOwnerSelector
        fieldName={BOOKING_OWNER}
        owners={owners}
        isLoading={isGetAuthorizedEmployeesLoading}
        currentEmployeeId={defaultBookingOwner?.id}
        isSshRequired={isSshRequired}
      />
    ) : (
      <BookEnvironmentFormBookingOwnerReadOnlyInput value={defaultBookingOwner?.name} />
    );

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit((formData) =>
          onSubmit({
            ...formData,
            bookSince: millisecondsToSeconds(formData[BOOK_SINCE_PICKER_NAME]),
            bookUntil: formData[BOOK_UNTIL_PICKER_NAME] ? millisecondsToSeconds(formData[BOOK_UNTIL_PICKER_NAME]) : undefined
          })
        )}
        noValidate
      >
        {/* To make fields fullWidth. Perhaps is should be resolved in the scope of IntervalTimePicker level (in the Popover)  */}
        <Box display="grid" className={classes.fieldsWrapper}>
          {isGetAuthorizedEmployeesLoading ? (
            <SelectorLoader fullWidth labelId="bookingOwner" isRequired />
          ) : (
            renderBookingOwnerField()
          )}
          <BookEnvironmentFormBookDateTimePicker
            intervalMinutes={INTERVAL_ENVIRONMENT}
            maxDate={maxPickerDate}
            name={BOOK_SINCE_PICKER_NAME}
            notSetMessageId="now"
            required
            quickValues={{
              values: ["now", "3h", "1d", "3d"]
            }}
            rules={{
              validate: {
                unique: (sinceTimestamp, formValues) => {
                  if (sinceTimestamp === undefined) {
                    return true;
                  }
                  return (
                    sinceTimestamp !== formValues[BOOK_UNTIL_PICKER_NAME] ||
                    intl.formatMessage({ id: "startDateShouldNotBeEqualToEndDate" })
                  );
                },
                isLessThanEndDate: (value, formValues) => {
                  const bookUntil = formValues[BOOK_UNTIL_PICKER_NAME];

                  if (!(bookUntil && value)) {
                    return true;
                  }

                  return value <= bookUntil || intl.formatMessage({ id: "startDateShouldNotBeGreaterThanEndTime" });
                },
                isNotBooked: (sinceTimestamp, formValues) => {
                  const overlappingInterval = findOverlappingInterval(
                    sinceTimestamp,
                    formValues[BOOK_UNTIL_PICKER_NAME],
                    allBookings
                  );

                  return !overlappingInterval || intl.formatMessage({ id: "selectedIntervalIsOverlappingWithExistedBooking" });
                }
              }
            }}
          />
          <BookEnvironmentFormBookDateTimePicker
            intervalMinutes={INTERVAL_ENVIRONMENT}
            maxDate={maxPickerDate}
            name={BOOK_UNTIL_PICKER_NAME}
            required
            quickValues={{
              values: ["3h", "1d", "3d"],
              orValues: ["noLimit"]
            }}
            notSetMessageId="notLimited"
            rules={{
              validate: {
                unique: (untilTimestamp, formValues) => {
                  if (untilTimestamp === undefined) {
                    return true;
                  }
                  return (
                    untilTimestamp !== formValues[BOOK_SINCE_PICKER_NAME] ||
                    intl.formatMessage({ id: "endDateShouldNotBeEqualToStartDate" })
                  );
                },
                isGreaterThanStartDate: (value, formValues) => {
                  const bookSince = formValues[BOOK_SINCE_PICKER_NAME];
                  if (!(bookSince && value)) {
                    return true;
                  }
                  return value >= bookSince || intl.formatMessage({ id: "endDateShouldBeGreaterThanStartTime" });
                },
                isNotBooked: (untilTimestamp, formValues) => {
                  const overlappingInterval = findOverlappingInterval(
                    formValues[BOOK_SINCE_PICKER_NAME],
                    untilTimestamp,
                    allBookings
                  );

                  return !overlappingInterval || intl.formatMessage({ id: "selectedIntervalIsOverlappingWithExistedBooking" });
                }
              }
            }}
          />
          {isSshRequired && isBookingForMyself ? (
            <EnvironmentSshKey
              sshKeys={currentEmployeeSshKeys}
              isGetSshKeysReady={isGetSshKeysReady}
              defaultKeyId={defaultBookingOwner?.default_ssh_key_id}
            />
          ) : null}
        </Box>
        <FormButtonsWrapper>
          <ButtonLoader
            dataTestId="bnt_add"
            isLoading={isBookEnvironmentLoading || isGetAuthorizedEmployeesLoading || isCreateSshKeyLoading}
            variant="contained"
            color="primary"
            messageId="book"
            type="submit"
          />
          <Button dataTestId="bnt_cancel" messageId="cancel" variant="outlined" onClick={onCancel} />
        </FormButtonsWrapper>
      </form>
    </FormProvider>
  );
};

BookEnvironmentForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isEnvironmentAvailable: PropTypes.bool.isRequired,
  allBookings: PropTypes.array.isRequired,
  owners: PropTypes.array.isRequired,
  defaultBookingOwner: PropTypes.object,
  canSetBookingOwner: PropTypes.bool,
  isLoadingProps: PropTypes.shape({
    isBookEnvironmentLoading: PropTypes.bool,
    isGetAuthorizedEmployeesLoading: PropTypes.bool,
    isCreateSshKeyLoading: PropTypes.bool
  }),
  onCancel: PropTypes.func,
  isSshRequired: PropTypes.bool,
  currentEmployeeSshKeys: PropTypes.array,
  isGetSshKeysReady: PropTypes.bool
};

export default BookEnvironmentForm;
