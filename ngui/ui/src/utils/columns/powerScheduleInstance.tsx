import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import Circle from "components/Circle";
import IconLabel from "components/IconLabel";
import OnScheduleLabel from "components/OnScheduleLabel";
import ResourceLabel from "components/ResourceLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getCloudResourceIdentifier } from "utils/resources";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";

const powerScheduleInstance = ({
  idAccessor,
  nameAccessor,
  powerScheduleAccessor,
  activeAccessor,
  headerDataTestId,
  titleMessageId,
}) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={titleMessageId} />
    </TextWithDataTestId>
  ),
  id: "instance",
  accessorFn: (originalRow) => `${getCloudResourceIdentifier(originalRow)} ${originalRow[nameAccessor]}`,
  style: RESOURCE_ID_COLUMN_CELL_STYLE,
  cell: ({ row: { original } }) => (
    <CaptionedCell
      caption={[
        {
          key: "name",
          node: original[nameAccessor],
        },
        ...(activeAccessor && original[activeAccessor]
          ? [
              {
                key: "active",
                node: (
                  <IconLabel
                    icon={<Circle color="success" />}
                    display="flex"
                    label={
                      <Typography variant="caption" noWrap>
                        <FormattedMessage id="active" />
                      </Typography>
                    }
                  />
                ),
              },
            ]
          : []),
        ...(powerScheduleAccessor && original[powerScheduleAccessor]
          ? [
              {
                key: "powerSchedule",
                node: <OnScheduleLabel powerScheduleId={original[powerScheduleAccessor]} />,
              },
            ]
          : []),
      ]}
    >
      <ResourceLabel resourceId={original[idAccessor]} cloudResourceIdentifier={getCloudResourceIdentifier(original)} />
    </CaptionedCell>
  ),
});

export default powerScheduleInstance;
