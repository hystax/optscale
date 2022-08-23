import React from "react";
import { text } from "@storybook/addon-knobs";
import ProfileMenu from "components/ProfileMenu";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ProfileMenu`
};

export const withKnobs = () => (
  <ProfileMenu
    email={text("email", "example@email.com")}
    name={text("name", "Some Name")}
    isLoading={false}
    signOut={() => {}}
  />
);
