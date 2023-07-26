import React from "react";
import ProfileMenu from "components/ProfileMenu";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/ProfileMenu`,
  argTypes: {
    email: { name: "Name", control: "text", defaultValue: "example@email.com" },
    name: { name: "Email", control: "text", defaultValue: "Some Name" }
  }
};

export const withKnobs = (args) => <ProfileMenu email={args.email} name={args.name} isLoading={false} signOut={() => {}} />;
