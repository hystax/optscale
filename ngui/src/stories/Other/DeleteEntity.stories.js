import React from "react";
import TableUseMemoWrapper from "stories/Other/TableUseMemoWrapper";
import { text, select, boolean } from "@storybook/addon-knobs";
import Box from "@mui/material/Box";
import DeleteEntity from "components/DeleteEntity";
import { KINDS } from "stories";

export default {
  title: `${KINDS.OTHER}/DeleteEntity`
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
          Header: "Name",
          accessor: "name",
          defaultSort: "asc"
        },
        {
          Header: "Cloud",
          accessor: "cloud"
        }
      ]}
      localization={{
        emptyMessageId: "notResources"
      }}
    />
  </DeleteEntity>
);

export const withChildren = () => (
  <DeleteEntity
    message={{
      messageId: "deleteResourcesQuestion",
      values: { count: boolean("render children", true) ? data.length : 1 }
    }}
    deleteButtonProps={{
      onDelete: () => console.log("Delete")
    }}
    onCancel={() => console.log("Cancel")}
  >
    {boolean("render children", true) ? (
      <TableUseMemoWrapper
        data={data}
        columns={[
          {
            Header: "Name",
            accessor: "name",
            defaultSort: "asc"
          },
          {
            Header: "Cloud",
            accessor: "cloud"
          }
        ]}
        localization={{
          emptyMessageId: "notResources"
        }}
      />
    ) : null}
  </DeleteEntity>
);

export const withKnobs = () => (
  <Box width={text("Wrapper width", "300px")}>
    <DeleteEntity
      message={{
        messageId: select("message", ["deleteResourcesQuestion", "deleteDRPlansQuestion", "custom"], "deleteResourcesQuestion"),
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
            Header: "Name",
            accessor: "name",
            defaultSort: "asc"
          },
          {
            Header: "Cloud",
            accessor: "cloud"
          }
        ]}
        localization={{
          emptyMessageId: "notResources"
        }}
      />
    </DeleteEntity>
  </Box>
);
