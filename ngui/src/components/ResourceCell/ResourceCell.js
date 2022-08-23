import React from "react";
import PriorityHighOutlinedIcon from "@mui/icons-material/PriorityHighOutlined";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import CircleLabel from "components/CircleLabel";
import IconLabel from "components/IconLabel";
import ResourceLabel from "components/ResourceLabel";
import { getResourceUrl } from "urls";
import { sliceByLimitWithEllipsis } from "utils/strings";

const NAME_SIZE_LIMIT = 32;

const getCaptionedCellProps = ({ resourceName, resourceId, cloudResourceId, showIsActive, showIsConstraintViolated }) => {
  const resourceNameString = resourceName ?? "";

  const captionSettings = [
    {
      key: resourceId,
      caption:
        resourceNameString.length <= NAME_SIZE_LIMIT
          ? resourceNameString
          : sliceByLimitWithEllipsis(resourceNameString, NAME_SIZE_LIMIT),
      tooltipText: resourceNameString.length <= NAME_SIZE_LIMIT ? "" : resourceNameString,
      show: resourceNameString !== cloudResourceId
    },
    {
      key: `isActive-${resourceId}`,
      node: (
        <CircleLabel
          figureColor="success"
          label={
            <Typography variant="caption">
              <FormattedMessage id="active" />
            </Typography>
          }
          textFirst={false}
        />
      ),
      show: showIsActive
    },
    {
      key: `isConstraintViolated-${resourceId}`,
      node: (
        <IconLabel
          icon={<PriorityHighOutlinedIcon fontSize="inherit" color="error" />}
          label={
            <Link to={`${getResourceUrl(resourceId)}?tab=constraints`} component={RouterLink}>
              <Typography variant="caption">
                <FormattedMessage id="constraintViolations" />
              </Typography>
            </Link>
          }
          component={RouterLink}
        />
      ),
      show: showIsConstraintViolated
    }
  ].filter(({ show }) => Boolean(show));

  return captionSettings;
};

const ResourceCell = ({ rowData, disableActivityIcon, disableConstraintViolationIcon, dataTestIds = {} }) => {
  const {
    resource_id: resourceId,
    cloud_resource_id: cloudResourceId,
    resource_name: resourceName,
    active: isActive = false,
    constraint_violated: isConstraintViolated = false
  } = rowData;

  const { labelIds: labelDataTestIds } = dataTestIds;

  return (
    <CaptionedCell
      caption={getCaptionedCellProps({
        resourceName,
        resourceId,
        cloudResourceId,
        showIsActive: isActive && !disableActivityIcon,
        showIsConstraintViolated: isConstraintViolated && !disableConstraintViolationIcon
      })}
    >
      <ResourceLabel resourceId={resourceId} cloudResourceId={cloudResourceId} dataTestIds={labelDataTestIds} />
    </CaptionedCell>
  );
};

ResourceCell.propTypes = {
  rowData: PropTypes.object.isRequired,
  labelDataTestId: PropTypes.string,
  disableActivityIcon: PropTypes.bool,
  disableConstraintViolationIcon: PropTypes.bool,
  dataTestIds: PropTypes.shape({
    labelIds: PropTypes.object
  })
};

export default ResourceCell;
