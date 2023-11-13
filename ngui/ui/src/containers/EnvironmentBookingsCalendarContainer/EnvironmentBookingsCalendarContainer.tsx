import BookingsCalendar from "components/BookingsCalendar";
import EnvironmentBookingsService from "services/EnvironmentBookingsService";

const EnvironmentBookingsCalendarContainer = ({ resourceId, resourceType, resourceName, poolId, poolName, poolType }) => {
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

export default EnvironmentBookingsCalendarContainer;
