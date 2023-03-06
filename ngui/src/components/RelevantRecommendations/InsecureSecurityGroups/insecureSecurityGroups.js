import React from "react";
import { FormattedMessage } from "react-intl";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, openPorts, resource, resourceLocation } from "utils/columns";
import { RECOMMENDATION_INSECURE_SECURITY_GROUPS, INSECURE_SECURITY_GROUPS_TYPE } from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class InsecureSecurityGroupsRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_INSECURE_SECURITY_GROUPS;

  moduleName = INSECURE_SECURITY_GROUPS_TYPE;

  withExclusions = true;

  withInsecurePorts = true;

  messageId = "instancesHaveInsecureSGSettingsTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      withInsecurePorts: this.withInsecurePorts,
      descriptionMessageId: "insecureSecurityGroupsDescription",
      emptyMessageId: "noSGOpened",
      dataTestIds: {
        listTestId: "sp_security_groups",
        textTestId: "p_security_groups",
        buttonTestIds: ["btn_sg_download"]
      }
    };
  }

  static configureColumns() {
    return [
      resource({
        headerDataTestId: "lbl_sg_resource"
      }),
      resourceLocation({
        headerDataTestId: "lbl_sg_location"
      }),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_sg_security_groups">
            <FormattedMessage id="securityGroup" />
          </TextWithDataTestId>
        ),
        accessorKey: "security_group_name"
      },
      openPorts({
        accessorKey: "insecure_ports",
        headerDataTestId: "lbl_sg_open_ports"
      }),
      detectedAt({ headerDataTestId: "lbl_sg_detected_at" })
    ];
  }
}

export default new InsecureSecurityGroupsRecommendation();
