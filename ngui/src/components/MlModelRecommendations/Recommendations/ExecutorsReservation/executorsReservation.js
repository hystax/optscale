import React from "react";
import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabel from "components/IconLabel";
import { firstSeen, lastUsed, size, mlExecutorLocation, mlExecutor } from "utils/columns";
import { RECOMMENDATION_EXECUTORS_RESERVATION, RECOMMENDATION_EXECUTORS_RESERVATION_TYPE } from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class ExecutorsReservation extends RecommendationFactory {
  type = RECOMMENDATION_EXECUTORS_RESERVATION;

  moduleName = RECOMMENDATION_EXECUTORS_RESERVATION_TYPE;

  messageId = "reservationsForExecutors";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      descriptionMessageId: "reservationsForExecutorsDescription",
      emptyMessageId: "noExecutorsUpgrade"
    };
  }

  static getListItem(item) {
    const { id, cloud_type: cloudType, cloud_resource_id: cloudResourceId } = item;
    return (
      <IconLabel
        icon={<CloudTypeIcon type={cloudType} hasRightMargin />}
        label={<CloudResourceId resourceId={cloudResourceId} cloudResourceIdentifier={id} />}
      />
    );
  }

  static configureColumns() {
    return [
      mlExecutor(),
      lastUsed({
        defaultSort: "desc"
      }),
      firstSeen(),
      mlExecutorLocation(),
      size({
        accessorKey: "size"
      })
    ];
  }
}

export default new ExecutorsReservation();
