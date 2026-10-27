# Translations (POC)

Proof-of-concept for runtime language switching. NGUI uses [react-intl](https://formatjs.io/docs/react-intl/) for i18n. English (`en-US`) is the canonical locale; other locales override keys as needed and fall back to English for anything missing.

## Layout

```
translations/
├── en-US/           # Complete translations (source of truth)
│   ├── app.json
│   ├── errors.json
│   ├── success.json
│   ├── finops.json
│   ├── currencies.json
│   └── index.ts     # Merges all JSON files into one flat map
├── es-ES/           # Partial locale example
├── localeManager.ts # Registry: locales, messages, number formats
└── react-intl-config.ts  # Legacy static intl singleton (see caveats)
```

Each locale folder mirrors the same JSON file split. Keys are flat strings (e.g. `"home"`, `"settings"`).

## Runtime switching

Locale state lives in `contexts/LocaleContext`. The app root wraps the tree in `LocaleContextProvider`, which renders `IntlProvider` with config from `getConfigForLocale(locale)`.

The header `LanguageSwitcher` reads `SUPPORTED_LOCALES` from `localeManager.ts` and calls `setLocale` on change.

**Fallback merge:**

```ts
messages: { ...messagesEnUS, ...getMessagesForLocale(locale) }
```

Only translated keys need to exist in a secondary locale file.

## Adding a new locale

1. Create `src/translations/<locale>/` with the same JSON files and an `index.ts` that merges them (copy from `en-US`).
2. Register in `localeManager.ts`:
   - Import the bundle
   - Add to `SUPPORTED_LOCALES` (label shown in the switcher)
   - Add to `messagesMap`

`SupportedLocale` is inferred from `SUPPORTED_LOCALES` — no extra type changes needed.

## Adding a new key

1. Add the key to the appropriate `en-US/*.json` file.
2. Add translations to other locale files as needed.
3. Use in components:

   ```tsx
   <FormattedMessage id="myKey" />
   // or
   const intl = useIntl();
   intl.formatMessage({ id: "myKey" });
   ```

4. Keep keys alphabetically sorted:

   ```bash
   pnpm translate:sort
   pnpm translate:test
   pnpm translate:fix   # prettier
   ```

## Caveats

- **Static `intl` singleton** — Many files import `intl` from `react-intl-config.ts`. That instance is created once at module load and does **not** update when the user switches language. Prefer `useIntl()` or `<FormattedMessage>` in React components.
- **No persistence** — Selected locale resets to `en-US` on page refresh.
- **Partial locales are fine** — Untranslated keys display in English via the merge fallback.
