import React from "react";
import ErrorOutlineOutlinedIcon from "@mui/icons-material/ErrorOutlineOutlined";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import Circle from "components/Circle";
import IconLabel from "components/IconLabel";
import OnScheduleLabel from "components/OnScheduleLabel";
import ResourceLabel from "components/ResourceLabel";
import ResourceName from "components/ResourceName";
import { getResourceUrl } from "urls";
import { getCloudResourceIdentifier } from "utils/resources";

const ResourceCell = ({ rowData, disableActivityIcon, disableConstraintViolationIcon, dataTestIds = {} }) => {
  const {
    resource_id: resourceId,
    resource_name: resourceName,
    active: isActive = false,
    constraint_violated: isConstraintViolated = false,
    power_schedule: powerScheduleId,
  } = rowData;

  const { labelIds: labelDataTestIds } = dataTestIds;

  return (
    <>
      <ResourceLabel
        resourceId={resourceId}
        cloudResourceIdentifier={getCloudResourceIdentifier(rowData)}
        dataTestIds={labelDataTestIds}
      />
      {resourceName && resourceName !== getCloudResourceIdentifier(rowData) ? (
        <div>
          <ResourceName name={resourceName} />
        </div>
      ) : null}
      {isActive && !disableActivityIcon ? (
        <IconLabel
          icon={<Circle color="success" />}
          display="flex"
          label={
            <Typography variant="caption" noWrap>
              <FormattedMessage id="active" />
            </Typography>
          }
        />
      ) : null}
      {powerScheduleId ? <OnScheduleLabel powerScheduleId={powerScheduleId} display="flex" /> : null}
      {isConstraintViolated && !disableConstraintViolationIcon ? (
        <IconLabel
          icon={<ErrorOutlineOutlinedIcon fontSize="inherit" color="error" />}
          display="flex"
          label={
            <Link
              to={`${getResourceUrl(resourceId)}?tab=constraints`}
              component={RouterLink}
              variant="caption"
              sx={{
                fontWeight: "normal",
                whiteSpace: "nowrap",
              }}
            >
              <FormattedMessage id="constraintViolations" />
            </Link>
          }
        />
      ) : null}
    </>
  );
};

export default ResourceCell;
