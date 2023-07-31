import React from "react";
import Button from "components/Button";
import IconError from "components/IconError";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/IconError`
};

export const basic = () => <IconError messageId="hystax" />;

export const withButton = () => (
  <IconError messageId="hystax">
    <Button color="primary" messageId="hystax" size="large" />
  </IconError>
);
