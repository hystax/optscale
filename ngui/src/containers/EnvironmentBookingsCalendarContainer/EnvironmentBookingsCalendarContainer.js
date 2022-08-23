import React from "react";
import PropTypes from "prop-types";
import BookingsCalendar from "components/BookingsCalendar";
import EnvironmentBookingsService from "services/EnvironmentBookingsService";

const EnvironmentBookingsCalendarContainer = ({
  resourceId,
  resourceType,
  resourceName,
  cloudResourceId,
  poolId,
  poolName,
  poolType
}) => {
  const { useGet } = EnvironmentBookingsService();

  const { bookings, isGetEnvironmentBookingsLoading, isGetResourceAllowedActionsLoading } = useGet(resourceId);

  // TODO: update BookingsCalendar interface, should receive array of bookings
  return (
    <BookingsCalendar
      environments={
        isGetEnvironmentBookingsLoading && isGetResourceAllowedActionsLoading
          ? []
          : [
              {
                name: resourceName,
                cloud_resource_id: cloudResourceId,
                resource_type: resourceType,
                pool_id: poolId,
                pool_name: poolName,
                pool_purpose: poolType,
                shareable_bookings: bookings
              }
            ]
      }
      eventProps={{ linkedTitle: false }}
    />
  );
};

EnvironmentBookingsCalendarContainer.propTypes = {
  resourceId: PropTypes.string.isRequired,
  resourceType: PropTypes.string.isRequired,
  cloudResourceId: PropTypes.string.isRequired,
  poolId: PropTypes.string.isRequired,
  poolName: PropTypes.string.isRequired,
  poolType: PropTypes.string.isRequired,
  resourceName: PropTypes.string
};

export default EnvironmentBookingsCalendarContainer;
