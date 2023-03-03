import React from "react";
import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabel from "components/IconLabel";
import { size, mlExecutor, mlExecutorLocation, mlGpuMemoryUsage } from "utils/columns";
import { GPU_MEMORY, GPU_MEMORY_TYPE } from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class GpuMemory extends RecommendationFactory {
  type = GPU_MEMORY;

  moduleName = GPU_MEMORY_TYPE;

  messageId = "gpuMemory";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      descriptionMessageId: "gpuMemoryDescription",
      emptyMessageId: "noRecommendations"
    };
  }

  static getListItem(item) {
    const { id, cloud_type: cloudType, cloud_resource_id: cloudResourceId, gpu_memory_usage: gpuMemoryUsage } = item;
    return (
      <div style={{ display: "flex" }}>
        <IconLabel
          icon={<CloudTypeIcon type={cloudType} hasRightMargin />}
          label={<CloudResourceId resourceId={cloudResourceId} cloudResourceIdentifier={id} />}
        />
        &nbsp;|&nbsp;<strong>{mlGpuMemoryUsage().cell({ cell: { getValue: () => gpuMemoryUsage } })}</strong>
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
      mlGpuMemoryUsage()
    ];
  }
}

export default new GpuMemory();
