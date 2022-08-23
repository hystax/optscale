import React from "react";
import MenuItemLoader from "components/MenuItemLoader";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/MenuItemLoader`
};

export const basic = () => <MenuItemLoader messageId="hystax" />;
