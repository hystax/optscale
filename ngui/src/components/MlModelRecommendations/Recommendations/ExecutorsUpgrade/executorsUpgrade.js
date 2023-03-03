import React from "react";
import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabel from "components/IconLabel";
import { lastUsed, mlExecutor, mlExecutorLocation, recommendedSize, size } from "utils/columns";
import { RECOMMENDATION_EXECUTORS_UPGRADE, RECOMMENDATION_EXECUTORS_UPGRADE_TYPE } from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class ExecutorsUpgrade extends RecommendationFactory {
  type = RECOMMENDATION_EXECUTORS_UPGRADE;

  moduleName = RECOMMENDATION_EXECUTORS_UPGRADE_TYPE;

  messageId = "executorsUpgrade";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      descriptionMessageId: "executorsUpgradeDescription",
      emptyMessageId: "noExecutorsUpgrade"
    };
  }

  static getListItem(item) {
    const {
      id,
      cloud_type: cloudType,
      cloud_resource_id: cloudResourceId,
      recommended_size: recommendedSizeRaw,
      size: sizeRaw
    } = item;
    return (
      <div style={{ display: "flex" }}>
        <IconLabel
          icon={<CloudTypeIcon type={cloudType} hasRightMargin />}
          label={<CloudResourceId resourceId={cloudResourceId} cloudResourceIdentifier={id} />}
        />
        &nbsp;| {sizeRaw}&nbsp;&rarr;&nbsp;{recommendedSizeRaw}
      </div>
    );
  }

  static configureColumns() {
    return [
      mlExecutor(),
      lastUsed({
        defaultSort: "desc"
      }),
      mlExecutorLocation(),
      size({
        accessorKey: "size"
      }),
      recommendedSize({
        accessorKey: "recommended_size"
      })
    ];
  }
}

export default new ExecutorsUpgrade();
