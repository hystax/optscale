import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import OnScheduleLabel from "components/OnScheduleLabel";
import ResourceLabel from "components/ResourceLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { getCloudResourceIdentifier } from "utils/resources";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";

const powerScheduleInstance = ({ idAccessor, nameAccessor, powerScheduleAccessor, headerDataTestId, titleMessageId }) => ({
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
          node: original[nameAccessor]
        },
        ...(powerScheduleAccessor && original[powerScheduleAccessor]
          ? [
              {
                key: "powerSchedule",
                node: <OnScheduleLabel powerScheduleId={original[powerScheduleAccessor]} />
              }
            ]
          : [])
      ]}
    >
      <ResourceLabel resourceId={original[idAccessor]} cloudResourceIdentifier={getCloudResourceIdentifier(original)} />
    </CaptionedCell>
  )
});

export default powerScheduleInstance;
