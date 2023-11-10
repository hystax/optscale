import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import ExecutorLabel from "components/ExecutorLabel";
import KeyValueLabel from "components/KeyValueLabel";
import TextWithDataTestId from "components/TextWithDataTestId";

const executor = () => ({
  header: (
    <TextWithDataTestId dataTestId="lbl_executor">
      <FormattedMessage id="executor" />
    </TextWithDataTestId>
  ),
  id: "executor",
  disableSortBy: true,
  cell: ({ row: { original } }) => {
    const {
      instance_region: instanceRegion,
      instance_type: instanceType,
      discovered,
      platform_type: platformType,
      instance_id: instanceId,
      resource
    } = original;
    return (
      <CaptionedCell
        caption={[
          {
            key: "name",
            node: <KeyValueLabel messageId="name" value={resource?.name} />
          },
          {
            key: "region",
            node: <KeyValueLabel messageId="region" value={instanceRegion} />
          },
          {
            key: "size",
            node: <KeyValueLabel messageId="size" value={instanceType} />
          }
        ]}
      >
        <ExecutorLabel discovered={discovered} resource={resource} instanceId={instanceId} platformType={platformType} />
      </CaptionedCell>
    );
  }
});

export default executor;
