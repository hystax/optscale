## Environment

### Node and npm

Actual versions:

- nodejs: 20.10.0
- npm: 10.2.3
- pnpm: 8.11.0

Source: https://nodejs.org/en/download/releases/

### Environment variables

Samples could be found here:

- ui/.env.sample
- server/.env.sample

Set all the variables and save without `.sample`

Take a note, that at production or dockerized version server starts with `prepare-and-run.sh` script, which creates /ui/build/config.js, where **all** `VITE_` variables (even unused in code!) will be listed **with** their names. At this stage, do not use `ui/.env` to store any sensitive information in `VITE_` variables.
