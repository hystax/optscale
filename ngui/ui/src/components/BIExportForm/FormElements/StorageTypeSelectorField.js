import React from "react";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { makeStyles } from "tss-react/mui";
import Chip from "components/Chip";
import CloudLabel from "components/CloudLabel";
import Skeleton from "components/Skeleton";
import { BI_EXPORT_STORAGE_TYPE } from "utils/biExport";
import { AWS_CNR, AZURE_CNR } from "utils/constants";
import { SPACING_2 } from "utils/layouts";

export const FIELD_NAME = "storageType";

const useStyles = makeStyles()((theme) => ({
  wrapper: {
    display: "flex",
    flexWrap: "wrap",
    width: "fit-content",
    gap: theme.spacing(SPACING_2)
  },
  tile: {
    borderColor: theme.palette.secondary.main
  },
  inactiveTile: {
    filter: "grayscale(1)",
    "&:hover": {
      borderColor: theme.palette.info.main,
      filter: "grayscale(0)"
    }
  }
}));

const StorageTypeSelectorField = ({ isEdit, isLoading }) => {
  const { control } = useFormContext();

  const { classes, cx } = useStyles();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      render={({ field: { value, onChange } }) => {
        const items = [
          {
            id: BI_EXPORT_STORAGE_TYPE.AWS_RAW_EXPORT,
            type: AWS_CNR,
            messageId: "amazonS3"
          },
          {
            id: BI_EXPORT_STORAGE_TYPE.AZURE_RAW_EXPORT,
            type: AZURE_CNR,
            messageId: "azureBlobStorage"
          }
        ].filter((item) => {
          if (isEdit) {
            return item.id === value;
          }
          return true;
        });

        const selector = (
          <div className={classes.wrapper}>
            {items.map(({ id, type, messageId }) => (
              <Chip
                key={id}
                variant="outlined"
                size="large"
                clickable
                onClick={() => onChange(id)}
                label={<CloudLabel type={type} label={<FormattedMessage id={messageId} />} />}
                className={cx(classes.tile, value !== id && classes.inactiveTile)}
              />
            ))}
          </div>
        );

        return isLoading ? (
          <Skeleton variant="rectangle" fullWidth>
            {selector}
          </Skeleton>
        ) : (
          selector
        );
      }}
    />
  );
};

export default StorageTypeSelectorField;
