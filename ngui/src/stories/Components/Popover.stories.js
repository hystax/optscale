import React from "react";
import Button from "@mui/material/Button";
import { text } from "@storybook/addon-knobs";
import WrapperCard from "components/WrapperCard";
import ProfileMenu from "components/ProfileMenu";
import Popover from "components/Popover";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Popover`
};

export const withTasks = () => (
  <Popover
    label={<Button>Tasks</Button>}
    menu={
      <WrapperCard title="myTasks" button={{ show: true, messageId: "goToTasks" }}>
        <ProfileMenu
          email={text("email", "example@email.com")}
          name={text("name", "Some Name")}
          isLoading={false}
          signOut={() => {}}
        />
      </WrapperCard>
    }
  />
);
