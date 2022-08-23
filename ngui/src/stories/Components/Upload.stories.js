import React from "react";
import Upload from "components/Upload";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Upload`
};

export const basic = () => <Upload acceptedFiles={[]} setFiles={(e) => console.log(e)} />;
