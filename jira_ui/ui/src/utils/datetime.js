// TODO: generalize with minutes, seconds, days, etc.
export const differenceInHours = (date1, date2) => Math.abs(Math.round((date1 - date2) / 36e5));
