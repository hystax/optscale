import React from "react";
import PlaylistAddOutlinedIcon from "@mui/icons-material/PlaylistAddOutlined";
import PlaylistRemoveOutlinedIcon from "@mui/icons-material/PlaylistRemoveOutlined";
import PriorityHighOutlinedIcon from "@mui/icons-material/PriorityHighOutlined";
import { Box, Typography } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import CloudLabel from "components/CloudLabel";
import ExpandableList from "components/ExpandableList";
import FormattedMoney from "components/FormattedMoney";
import IconButton from "components/IconButton";
import QuestionMark from "components/QuestionMark";
import TextWithDataTestId from "components/TextWithDataTestId";
import Tooltip from "components/Tooltip";
import { useIsSizeSelected, useSelectionActions } from "reducers/cloudCostComparisonSelectedSizes/hooks";
import { isLastItem } from "utils/arrays";
import { AWS_CNR, AZURE_CNR, FORMATTED_MONEY_TYPES, NEBIUS } from "utils/constants";

const Flavor = ({ flavor }) => {
  const { addSize, removeSize } = useSelectionActions();

  const { id, name, location, instance_family: instanceFamily, cost, currency } = flavor;

  const isFlavorSelected = useIsSizeSelected(id);

  return (
    <>
      <div
        style={{
          position: "relative"
        }}
      >
        <Typography
          color={isFlavorSelected ? "secondary" : undefined}
          component="span"
          sx={{
            whiteSpace: "nowrap"
          }}
        >
          <strong>
            <FormattedMessage
              id="value / value"
              values={{
                value1: name,
                value2: location
              }}
            />
          </strong>
        </Typography>
        <Tooltip
          title={isFlavorSelected ? <FormattedMessage id="removeFromComparison" /> : <FormattedMessage id="addToComparison" />}
        >
          <IconButton
            onClick={() => {
              if (isFlavorSelected) {
                removeSize(flavor);
              } else {
                addSize(flavor);
              }
            }}
            icon={isFlavorSelected ? <PlaylistRemoveOutlinedIcon /> : <PlaylistAddOutlinedIcon />}
            sx={{
              position: "absolute",
              top: "-9px"
            }}
          />
        </Tooltip>
      </div>
      <div>{instanceFamily}</div>
      <div>
        <FormattedMessage
          id="valuePerHour"
          values={{
            value: (
              <FormattedMoney value={cost} format={currency} type={FORMATTED_MONEY_TYPES.TINY} maximumFractionDigits={20} />
            )
          }}
        />
      </div>
    </>
  );
};

const FlavorsCell = ({ flavors }) => (
  <ExpandableList
    items={flavors.map((flavor, itemIndex) => (
      <Box
        key={flavor.id}
        sx={{
          marginBottom: isLastItem(itemIndex, flavors.length) ? 0 : 1
        }}
      >
        <Flavor flavor={flavor} />
      </Box>
    ))}
    render={(item) => item}
    maxRows={5}
  />
);

const Header = ({ cloudType, error }) => {
  const intl = useIntl();

  return (
    <Box display="flex" alignItems="center">
      <TextWithDataTestId dataTestId={`lbl_${cloudType}`}>
        {
          {
            [AWS_CNR]: <CloudLabel name={intl.formatMessage({ id: "aws" })} type={AWS_CNR} disableLink />,
            [AZURE_CNR]: <CloudLabel name={intl.formatMessage({ id: "azure" })} type={AZURE_CNR} disableLink />,
            [NEBIUS]: <CloudLabel name={intl.formatMessage({ id: "nebius" })} type={NEBIUS} disableLink />
          }[cloudType]
        }
      </TextWithDataTestId>
      {error && <QuestionMark fontSize="small" tooltipText={error} Icon={PriorityHighOutlinedIcon} color="error" />}
    </Box>
  );
};

export const flavors = ({ cloudType, error }) => ({
  header: <Header cloudType={cloudType} error={error} />,
  accessorKey: cloudType,
  enableSorting: false,
  style: {
    minWidth: "200px",
    verticalAlign: "top"
  },
  cell: ({
    row: {
      original: { [cloudType]: cloudTypeFlavors }
    }
  }) => <FlavorsCell flavors={cloudTypeFlavors} />
});
