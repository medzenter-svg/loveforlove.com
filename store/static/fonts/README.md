# Local fonts for Amalfi

Place the locally licensed font files in this directory using these exact names:

- `CormorantGaramond-Regular.woff2`
- `CormorantGaramond-SemiBold.woff2`
- `Allura-Regular.woff2`

TTF fallback names are also supported:

- `CormorantGaramond-Regular.ttf`
- `CormorantGaramond-SemiBold.ttf`
- `Allura-Regular.ttf`

WOFF2 is preferred for the web editor because it is smaller. The PDF generator embeds whichever local file is present into the Playwright HTML, so PDF generation does not depend on Google Fonts or an external network request.
