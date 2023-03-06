import React from "react";
import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabel from "components/IconLabel";
import { size, mlExecutor, mlExecutorLocation, mlIOPSCap, mlLocalStorageBottleneckDuration } from "utils/columns";
import { LOCAL_STORAGE_BOTTLENECK, LOCAL_STORAGE_BOTTLENECK_TYPE } from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class LocalStorageBottleneck extends RecommendationFactory {
  type = LOCAL_STORAGE_BOTTLENECK;

  moduleName = LOCAL_STORAGE_BOTTLENECK_TYPE;

  messageId = "localStorageBottleneck";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      descriptionMessageId: "localStorageBottleneckDescription",
      emptyMessageId: "noLocalStorageBottlenecks"
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
        <strong>{mlIOPSCap().cell({ row: { original: item } })}</strong>
      </div>
    );
  }

  static configureColumns() {
    return [
      mlExecutor({ showRunInspect: true }),
      mlExecutorLocation(),
      size({
        accessorKey: "size"
      }),
      mlIOPSCap(),
      mlLocalStorageBottleneckDuration()
    ];
  }
}

export default new LocalStorageBottleneck();
