#!/usr/bin/env node
const fs = require("node:fs");
const path = require("node:path");
const chromeKeys = require("./i18n-chrome-keys");

function deepMerge(target, source) {
  for (const [key, value] of Object.entries(source)) {
    if (
      value &&
      typeof value === "object" &&
      !Array.isArray(value) &&
      target[key] &&
      typeof target[key] === "object"
    ) {
      deepMerge(target[key], value);
    } else {
      target[key] = value;
    }
  }
  return target;
}

const root = path.join(__dirname, "..", "apps", "web", "messages");
for (const locale of ["vi", "en"]) {
  const filePath = path.join(root, `${locale}.json`);
  const current = JSON.parse(fs.readFileSync(filePath, "utf8"));
  deepMerge(current, chromeKeys[locale]);
  fs.writeFileSync(filePath, `${JSON.stringify(current, null, 2)}\n`);
}

console.log("Merged chrome i18n keys into vi.json and en.json");
