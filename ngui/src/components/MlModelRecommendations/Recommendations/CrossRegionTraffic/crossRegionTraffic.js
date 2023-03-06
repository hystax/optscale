import React from "react";
import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import FormattedDigitalUnit from "components/FormattedDigitalUnit";
import FormattedMoney from "components/FormattedMoney";
import IconLabel from "components/IconLabel";
import { mlExecutor, mlComputeLocation, mlDataLocation, mlDataTransferred, estimatedExpenses } from "utils/columns";
import { CROSS_REGION_TRAFFIC, CROSS_REGION_TRAFFIC_TYPE } from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class CrossRegionTraffic extends RecommendationFactory {
  type = CROSS_REGION_TRAFFIC;

  moduleName = CROSS_REGION_TRAFFIC_TYPE;

  messageId = "crossRegionTraffic";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      descriptionMessageId: "crossRegionTrafficDescription",
      emptyMessageId: "noCrossRegionTraffic"
    };
  }

  static getListItem(item) {
    const {
      id,
      cloud_type: cloudType,
      cloud_resource_id: cloudResourceId,
      data_transferred: dataTransferred,
      estimated_expenses: estimatedExpences
    } = item;
    return (
      <div style={{ display: "flex" }}>
        <IconLabel
          icon={<CloudTypeIcon type={cloudType} hasRightMargin />}
          label={<CloudResourceId resourceId={cloudResourceId} cloudResourceIdentifier={id} />}
        />
        &nbsp;| <FormattedDigitalUnit value={dataTransferred} />
        &nbsp;|&nbsp;
        <strong>
          <FormattedMoney value={estimatedExpences} />
        </strong>
      </div>
    );
  }

  static configureColumns() {
    return [mlExecutor(), mlComputeLocation(), mlDataLocation(), mlDataTransferred(), estimatedExpenses()];
  }
}

export default new CrossRegionTraffic();
