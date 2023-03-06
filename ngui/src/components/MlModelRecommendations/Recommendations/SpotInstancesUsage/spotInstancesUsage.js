import React from "react";
import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabel from "components/IconLabel";
import { useFormatDuration } from "hooks/useFormatDuration";
import { mlRunsCount, size, mlExecutorLocation, mlAverageLifetime, mlExecutor } from "utils/columns";
import { SPOT_INSTANCES_USAGE, SPOT_INSTANCES_USAGE_TYPE } from "utils/constants";
import { secondsToMilliseconds } from "utils/datetime";
import RecommendationFactory from "utils/recommendations";

const FormattedApproximateAverageLifetime = ({ lifetime }) => {
  const time = useFormatDuration(secondsToMilliseconds(lifetime), 1);

  return `~${time}`;
};

class SpotInstancesUsage extends RecommendationFactory {
  type = SPOT_INSTANCES_USAGE;

  moduleName = SPOT_INSTANCES_USAGE_TYPE;

  messageId = "spotPreemptibleInstancesUsage";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      descriptionMessageId: "spotPreemptibleInstancesUsageDescription",
      emptyMessageId: "noSpotPreemptibleOnstancesUsage"
    };
  }

  static getListItem(item) {
    const { id, cloud_type: cloudType, cloud_resource_id: cloudResourceId } = item;

    return (
      <div style={{ display: "flex" }}>
        <IconLabel
          icon={<CloudTypeIcon type={cloudType} hasRightMargin />}
          label={<CloudResourceId resourceId={cloudResourceId} cloudResourceIdentifier={id} />}
        />
        &nbsp;|&nbsp;
        <strong>
          <FormattedApproximateAverageLifetime lifetime={item.average_lifetime} />
        </strong>
      </div>
    );
  }

  static configureColumns() {
    return [
      mlExecutor(),
      mlExecutorLocation(),
      size({
        accessorKey: "size"
      }),
      mlRunsCount(),
      mlAverageLifetime()
    ];
  }
}

export default new SpotInstancesUsage();
