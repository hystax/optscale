import useMediaQuery from "@mui/material/useMediaQuery";

// See https://material-ui.com/components/use-media-query/#usemediaquery-query-options-matches for more details about 'noSsr'
export const useIsDownMediaQuery = (query) => useMediaQuery((theme) => theme.breakpoints.down(query), { noSsr: true });

export const useIsUpMediaQuery = (query) => useMediaQuery((theme) => theme.breakpoints.up(query), { noSsr: true });
