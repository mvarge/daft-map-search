const fs = require('node:fs');
const path = require('node:path');

const key = process.env.CARTO_API_KEY?.trim();
if (!key) throw new Error('CARTO_API_KEY is required for the deployment build');

const root = path.join(__dirname, '..');
const output = path.join(root, 'dist');
fs.mkdirSync(output, { recursive: true });
for (const file of ['index.html', 'locations.js', 'logo.svg', 'og-image.png', 'robots.txt', 'sitemap.xml']) {
  fs.copyFileSync(path.join(root, file), path.join(output, file));
}
// This is a public browser credential. Store it in Vercel, never in source control.
fs.writeFileSync(path.join(output, 'config.js'), `window.DAFT_CONFIG = ${JSON.stringify({ cartoApiKey: key })};\n`);
