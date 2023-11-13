import DeleteEntity from "components/DeleteEntity";
import { KINDS } from "stories";
import TableUseMemoWrapper from "stories/Other/TableUseMemoWrapper";

export default {
  title: `${KINDS.OTHER}/DeleteEntity`,
  argTypes: {
    messageId: {
      name: "Message ID",
      control: "select",
      options: ["deleteResourcesQuestion", "deleteDRPlansQuestion", "custom"],
      defaultValue: "deleteResourcesQuestion"
    },
    withChildren: { name: "With children", control: "boolean", defaultValue: true }
  }
};

const data = [
  { name: "Name 1", cloud: "Cloud 1" },
  { name: "Name 2", cloud: "Cloud 2" }
];

export const basic = () => (
  <DeleteEntity
    message={{ messageId: "deleteResourcesQuestion", values: { count: data.length } }}
    deleteButtonProps={{
      onDelete: () => console.log("Delete")
    }}
    onCancel={() => console.log("Cancel")}
  >
    <TableUseMemoWrapper
      data={data}
      columns={[
        {
          header: "Name",
          accessorKey: "name",
          defaultSort: "asc"
        },
        {
          header: "Cloud",
          accessorKey: "cloud"
        }
      ]}
      localization={{
        emptyMessageId: "notResources"
      }}
    />
  </DeleteEntity>
);

export const withChildren = (args) => (
  <DeleteEntity
    message={{
      messageId: "deleteResourcesQuestion",
      values: { count: args.withChildren ? data.length : 1 }
    }}
    deleteButtonProps={{
      onDelete: () => console.log("Delete")
    }}
    onCancel={() => console.log("Cancel")}
  >
    {args.withChildren ? (
      <TableUseMemoWrapper
        data={data}
        columns={[
          {
            header: "Name",
            accessorKey: "name",
            defaultSort: "asc"
          },
          {
            header: "Cloud",
            accessorKey: "cloud"
          }
        ]}
        localization={{
          emptyMessageId: "notResources"
        }}
      />
    ) : null}
  </DeleteEntity>
);

export const withKnobs = (args) => (
  <DeleteEntity
    message={{
      messageId: args.messageId,
      values: { count: data.length }
    }}
    deleteButtonProps={{
      onDelete: () => console.log("Delete")
    }}
    onCancel={() => console.log("Cancel")}
  >
    <TableUseMemoWrapper
      data={data}
      columns={[
        {
          header: "Name",
          accessorKey: "name",
          defaultSort: "asc"
        },
        {
          header: "Cloud",
          accessorKey: "cloud"
        }
      ]}
      localization={{
        emptyMessageId: "notResources"
      }}
    />
  </DeleteEntity>
);
