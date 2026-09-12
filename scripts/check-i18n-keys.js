#!/usr/bin/env node
/** Compare message keys between vi.json and en.json */
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname, "..", "apps", "web", "messages");
const vi = JSON.parse(fs.readFileSync(path.join(root, "vi.json"), "utf8"));
const en = JSON.parse(fs.readFileSync(path.join(root, "en.json"), "utf8"));

function flatten(obj, prefix = "") {
  const keys = [];
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (typeof v === "object" && v !== null) keys.push(...flatten(v, key));
    else keys.push(key);
  }
  return keys;
}

const viKeys = new Set(flatten(vi));
const enKeys = new Set(flatten(en));
const missingInEn = [...viKeys].filter((k) => !enKeys.has(k));
const missingInVi = [...enKeys].filter((k) => !viKeys.has(k));

if (missingInEn.length || missingInVi.length) {
  if (missingInEn.length) {
    console.error("Missing in en.json:", missingInEn.join(", "));
  }
  if (missingInVi.length) {
    console.error("Missing in vi.json:", missingInVi.join(", "));
  }
  process.exit(1);
}

console.log(`OK: ${viKeys.size} i18n keys match between vi.json and en.json`);
