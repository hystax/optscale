import ExitToAppOutlinedIcon from "@mui/icons-material/ExitToAppOutlined";
import { Box, Stack, Typography } from "@mui/material";
import List from "@mui/material/List";
import ListItemText from "@mui/material/ListItemText";
import MenuItem from "@mui/material/MenuItem";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import CloudLabel from "components/CloudLabel";
import CloudResourceId from "components/CloudResourceId";
import CloudTypeIcon from "components/CloudTypeIcon";
import DashedTypography from "components/DashedTypography";
import FormattedMoney from "components/FormattedMoney";
import IconButton from "components/IconButton";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import Popover from "components/Popover";
import ResourceTypeLabel from "components/ResourceTypeLabel";
import TableLoader from "components/TableLoader";
import TitleValue from "components/TitleValue";
import Tooltip from "components/Tooltip";
import WrapperCard from "components/WrapperCard";
import { useOrganizationPerspectives } from "hooks/useOrganizationPerspectives";
import { getLast30DaysResourcesUrl, getResourcesExpensesUrl, RESOURCE_PERSPECTIVES } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { percentXofY } from "utils/math";
import { getCloudResourceIdentifier } from "utils/resources";
import { sliceByLimitWithEllipsis } from "utils/strings";
import useStyles from "./TopResourcesExpensesCard.styles";

const PERSPECTIVE_NAME_SLICE_THRESHOLD = 30;

const PerspectiveMenuItem = ({ perspectiveName }) => {
  const navigate = useNavigate();

  const onClick = () => navigate(getResourcesExpensesUrl({ perspective: perspectiveName }));

  return perspectiveName.length > PERSPECTIVE_NAME_SLICE_THRESHOLD ? (
    <Tooltip key={perspectiveName} title={perspectiveName}>
      <MenuItem onClick={onClick}>
        <ListItemText primary={sliceByLimitWithEllipsis(perspectiveName, PERSPECTIVE_NAME_SLICE_THRESHOLD)} />
      </MenuItem>
    </Tooltip>
  ) : (
    <MenuItem key={perspectiveName} onClick={onClick}>
      <ListItemText primary={perspectiveName} />
    </MenuItem>
  );
};

const Property = ({ messageId, value }) => (
  <Typography component="div">
    <strong>
      <FormattedMessage id={messageId} />
    </strong>
    &#58;&nbsp;
    {value}
  </Typography>
);

const TopResourcesView = ({ data }) => {
  const { classes, cx } = useStyles();
  if (!data.length) {
    return null;
  }
  const maxValue = data[0].cost;
  return data.map((original) => {
    const {
      id,
      cost,
      cloud_account_type: cloudType,
      resource_type: resourceType,
      cluster_type_id: clusterTypeId,
      is_environment: isEnvironment,
      resource_id: resourceId,
      shareable,
      cloud_account_id: cloudId,
      cloud_account_name: cloudName
    } = original;
    return (
      <Tooltip
        key={id}
        title={
          <Stack spacing={SPACING_1}>
            <Property messageId="id" value={getCloudResourceIdentifier(original)} />
            {!!original.resource_name && <Property messageId="name" value={original.resource_name} />}
            <Property
              messageId="type"
              value={<ResourceTypeLabel resourceInfo={{ shareable, resourceId, isEnvironment, clusterTypeId, resourceType }} />}
            />
            {/* Clusters do not have cloud type */}
            {!!cloudType && (
              <KeyValueLabel
                isBoldValue={false}
                keyText={
                  <Typography fontWeight="bold">
                    <FormattedMessage id="location" />
                  </Typography>
                }
                value={
                  <CloudLabel dataTestId={`resource_location_${resourceId}`} id={cloudId} name={cloudName} type={cloudType} />
                }
              />
            )}
          </Stack>
        }
      >
        <Typography component="div" className={classes.item}>
          <div className={classes.bar} style={{ width: `${percentXofY(cost, maxValue) * 100}%` }} />
          <div className={cx(classes.flexRow, classes.itemContent)}>
            <div className={classes.flexRow}>
              <CloudTypeIcon type={cloudType} hasRightMargin />
              <CloudResourceId
                disableFullNameTooltip
                resourceId={resourceId}
                cloudResourceIdentifier={getCloudResourceIdentifier(original)}
              />
            </div>
            <TitleValue>
              <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cost} />
            </TitleValue>
          </div>
        </Typography>
      </Tooltip>
    );
  });
};

const TopResourcesExpensesCard = ({ cleanExpenses, isLoading }) => {
  const navigate = useNavigate();

  const { validPerspectives } = useOrganizationPerspectives();
  const perspectiveNames = Object.keys(validPerspectives);
  const hasPerspectives = !isEmptyArray(perspectiveNames);

  const goToResources = () => navigate(getLast30DaysResourcesUrl());

  return (
    <WrapperCard
      needAlign
      title={
        <Box display="flex" alignItems="center">
          <Box mr={0.5}>
            <FormattedMessage id="topResourcesExpenses" />
          </Box>
          <Box display="flex" mr={hasPerspectives ? 0.5 : 0}>
            <IconButton
              icon={<ExitToAppOutlinedIcon />}
              tooltip={{
                show: true,
                messageId: "goToResources"
              }}
              onClick={goToResources}
              isLoading={isLoading}
              dataTestId="btn_go_to_resources"
            />
          </Box>
          {hasPerspectives && (
            <Popover
              label={
                <DashedTypography component="div">
                  <FormattedMessage id="perspectives" />
                </DashedTypography>
              }
              anchorOrigin={{
                vertical: "bottom",
                horizontal: "left"
              }}
              transformOrigin={{
                vertical: "top",
                horizontal: "left"
              }}
              menu={
                <List>
                  {[
                    ...perspectiveNames.map((name) => <PerspectiveMenuItem key={name} perspectiveName={name} />),
                    <MenuItem key="seeAllPerspectives" onClick={() => navigate(RESOURCE_PERSPECTIVES)}>
                      <ListItemText primary={<FormattedMessage id="seeAllPerspectives" />} />
                    </MenuItem>
                  ]}
                </List>
              }
            />
          )}
        </Box>
      }
      dataTestIds={{
        wrapper: "block_top_resources",
        title: "lbl_top_resources",
        titleCaption: "p_last_30_days"
      }}
      elevation={0}
    >
      {isLoading ? <TableLoader columnsCounter={1} /> : <TopResourcesView data={cleanExpenses} />}
    </WrapperCard>
  );
};

export default TopResourcesExpensesCard;
