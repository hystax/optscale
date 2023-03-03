import React from "react";
import { Check } from "@mui/icons-material";
import { Box, Card, CardContent, List, ListItemText, Typography } from "@mui/material";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { v4 as uuidv4 } from "uuid";
import FormattedMoney from "components/FormattedMoney";
import RecommendationDescription from "components/RecommendationDescription";
import { MLRecommendationDetailsModal } from "components/SideModalManager/SideModals";
import Skeleton from "components/Skeleton";
import TitleValue from "components/TitleValue";
import Tooltip from "components/Tooltip";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import useStyles from "./RecommendationCard.styles";

const MAX_PREVIEW_ITEMS = 2;

// TODO: it is copy of summary card money value
const NiceMoneyView = ({ value, ...rest }) => {
  const { currency = "USD" } = useOrganizationInfo();

  return (
    <Tooltip title={<FormattedNumber format={currency} value={value} />}>
      <span>
        <FormattedMoney {...rest} value={value} type={FORMATTED_MONEY_TYPES.COMPACT} />
      </span>
    </Tooltip>
  );
};

const Excerpt = ({ saving, count, isLoading, color }) => {
  if (isLoading) {
    return (
      <div>
        <Skeleton>
          <Typography variant="h5" component="div">
            1204$
          </Typography>
        </Skeleton>
        <Skeleton>
          <Typography variant="body2">
            <FormattedMessage id="savings" />
          </Typography>
        </Skeleton>
      </div>
    );
  }

  let value = saving ? <NiceMoneyView value={saving} /> : count;
  let label = <FormattedMessage id={saving ? "savings" : "count"} />;

  if (!value) {
    value = <Check color={color} />;
    label = "";
  }

  return (
    <div>
      <Typography variant="h5" component="div" color={color} fontWeight="bold">
        {value}
      </Typography>
      <Typography variant="body2" fontWeight="bold" color={color}>
        {label}
      </Typography>
    </div>
  );
};

const RecordsPreview = ({ items, isLoading, recommendationInstance }) => {
  if (isLoading) {
    return (
      <div>
        <Skeleton fullWidth>
          <ListItemText>...</ListItemText>
        </Skeleton>
        <Skeleton fullWidth>
          <ListItemText>...</ListItemText>
        </Skeleton>
      </div>
    );
  }

  if (!items.length) {
    return null;
  }

  const recordsTable = items
    .slice(0, MAX_PREVIEW_ITEMS)
    .map((item) =>
      typeof recommendationInstance.constructor.getListItem === "function" ? (
        <ListItemText key={uuidv4()} primary={recommendationInstance.constructor.getListItem(item)} />
      ) : null
    );

  return (
    <List dense>
      {recordsTable}
      {items.length > MAX_PREVIEW_ITEMS && <ListItemText primary={`...and ${items.length - 2} more`} />}
    </List>
  );
};

const Details = ({ buildedRecommendation, recommendationInstance, items, isLoading }) => {
  const openSideModal = useOpenSideModal();

  if (isLoading) {
    return (
      <Skeleton>
        <Typography>
          <FormattedMessage id="seeDetails" />
        </Typography>
      </Skeleton>
    );
  }

  if (!items.length) {
    return null;
  }

  const sidemodalPayload = {
    columns: buildedRecommendation.columns,
    items,
    descriptionMessageId: buildedRecommendation.descriptionMessageId,
    titleMessageId: recommendationInstance.messageId
  };
  const openDetails = () => openSideModal(MLRecommendationDetailsModal, sidemodalPayload);

  return (
    <Link
      sx={{
        ":hover": {
          cursor: "pointer"
        }
      }}
      onClick={openDetails}
    >
      <FormattedMessage id="seeDetails" />
    </Link>
  );
};

const RecommendationCard = ({ items = [], saving, count, isLoading, recommendationInstance, buildedRecommendation }) => {
  let color = "success";
  if (saving || count > 10) {
    color = "error";
  } else if (count || isLoading) {
    color = undefined;
  }

  const { classes } = useStyles(color);

  return (
    <Card elevation={0} className={classes.card}>
      <CardContent className={classes.content}>
        <Box className={classes.header}>
          <div className={classes.title}>
            <TitleValue>
              <FormattedMessage id={recommendationInstance.messageId} />
            </TitleValue>
            <RecommendationDescription messageId={buildedRecommendation.descriptionMessageId} />
          </div>
          <div>
            <Excerpt color={color} saving={saving} count={count} isLoading={isLoading} />
          </div>
        </Box>
        <RecordsPreview items={items} isLoading={isLoading} recommendationInstance={recommendationInstance} />
        <Details
          buildedRecommendation={buildedRecommendation}
          recommendationInstance={recommendationInstance}
          items={items}
          isLoading={isLoading}
        />
      </CardContent>
    </Card>
  );
};

RecommendationCard.propTypes = {
  recommendationType: PropTypes.string,
  items: PropTypes.array,
  saving: PropTypes.number,
  count: PropTypes.number,
  isLoading: PropTypes.bool,
  recommendationInstance: PropTypes.object,
  buildedRecommendation: PropTypes.object
};

export default RecommendationCard;
