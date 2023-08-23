## Environment

### Node and npm

Actual versions:

- nodejs: 18.14.0
- npm: 9.3.1

Source: https://nodejs.org/en/download/releases/

### Environment variables

Samples could be found here:
- ui/.env.sample
- server/.env.sample

Set all the variables and save without `.sample`

Take a note, that at production or dockerized version server starts with `prepare-and-run.sh` script, which creates /ui/build/config.js, where **all** `REACT_APP_` variables (even unused in code!) will be listed **with** their names. At this stage, do not use `ui/.env` to store any sensitive information in `REACT_APP_` variables.