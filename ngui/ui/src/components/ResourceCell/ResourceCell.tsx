import ErrorOutlineOutlinedIcon from "@mui/icons-material/ErrorOutlineOutlined";
import { Box } from "@mui/material";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import Circle from "components/Circle";
import IconLabel from "components/IconLabel";
import OnScheduleLabel from "components/OnScheduleLabel";
import ResourceLabel from "components/ResourceLabel";
import ResourceName from "components/ResourceName";
import { getResourceUrl } from "urls";
import { getCloudResourceIdentifier } from "utils/resources";

const getCaptionedCellProps = ({
  resourceName,
  resourceId,
  cloudResourceIdentifier,
  showIsActive,
  showIsConstraintViolated,
  powerScheduleId
}) => {
  const resourceNameString = resourceName ?? "";

  const captionSettings = [
    {
      key: resourceId,
      node: <ResourceName name={resourceNameString} />,
      show: resourceNameString !== cloudResourceIdentifier
    },
    {
      key: `statuses-${resourceId}`,
      node: (
        <Box display="flex" gap={1}>
          {showIsActive && (
            <IconLabel
              icon={<Circle color="success" mr={0.5} />}
              label={
                <Typography variant="caption" noWrap>
                  <FormattedMessage id="active" />
                </Typography>
              }
            />
          )}
          {powerScheduleId && <OnScheduleLabel powerScheduleId={powerScheduleId} />}
          {showIsConstraintViolated && (
            <IconLabel
              icon={
                <ErrorOutlineOutlinedIcon
                  fontSize="inherit"
                  color="error"
                  sx={{
                    mr: 0.5
                  }}
                />
              }
              label={
                <Link to={`${getResourceUrl(resourceId)}?tab=constraints`} component={RouterLink}>
                  <Typography variant="caption">
                    <FormattedMessage id="constraintViolations" />
                  </Typography>
                </Link>
              }
              component={RouterLink}
            />
          )}
        </Box>
      ),
      show: showIsActive || powerScheduleId || showIsConstraintViolated
    }
  ].filter(({ show }) => Boolean(show));

  return captionSettings;
};

const ResourceCell = ({ rowData, disableActivityIcon, disableConstraintViolationIcon, dataTestIds = {} }) => {
  const {
    resource_id: resourceId,
    resource_name: resourceName,
    active: isActive = false,
    constraint_violated: isConstraintViolated = false,
    power_schedule: powerScheduleId
  } = rowData;

  const { labelIds: labelDataTestIds } = dataTestIds;

  return (
    <CaptionedCell
      caption={getCaptionedCellProps({
        resourceName,
        resourceId,
        cloudResourceIdentifier: getCloudResourceIdentifier(rowData),
        showIsActive: isActive && !disableActivityIcon,
        showIsConstraintViolated: isConstraintViolated && !disableConstraintViolationIcon,
        powerScheduleId
      })}
    >
      <ResourceLabel
        resourceId={resourceId}
        cloudResourceIdentifier={getCloudResourceIdentifier(rowData)}
        dataTestIds={labelDataTestIds}
      />
    </CaptionedCell>
  );
};

export default ResourceCell;
