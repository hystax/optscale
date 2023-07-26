import React from "react";
import Grid from "@mui/material/Grid";
import Chip from "components/Chip";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/Chip`
};

const deleteChip = () => {
  console.log("test");
};

export const basic = () => <Chip label="Chip" />;
export const small = () => (
  <Grid container spacing={2}>
    <Grid item>
      <Chip onDelete={() => deleteChip()} label="Chip" />
    </Grid>
    <Grid item>
      <Chip onDelete={() => deleteChip()} color="primary" label="Chip" />
    </Grid>
    <Grid item>
      <Chip onDelete={() => deleteChip()} color="success" label="Chip" />
    </Grid>
    <Grid item>
      <Chip onDelete={() => deleteChip()} color="error" label="Chip" />
    </Grid>
  </Grid>
);
export const medium = () => (
  <Grid container spacing={2}>
    <Grid item>
      <Chip size="medium" onDelete={() => deleteChip()} label="Chip" />
    </Grid>
    <Grid item>
      <Chip size="medium" onDelete={() => deleteChip()} color="primary" label="Chip" />
    </Grid>
    <Grid item>
      <Chip size="medium" onDelete={() => deleteChip()} color="success" label="Chip" />
    </Grid>
    <Grid item>
      <Chip size="medium" onDelete={() => deleteChip()} color="error" label="Chip" />
    </Grid>
  </Grid>
);
