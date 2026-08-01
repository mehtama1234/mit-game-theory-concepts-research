import { cpSync, existsSync, rmSync } from "node:fs";

if (!existsSync("site/index.html")) {
  throw new Error("site/index.html is missing; run python3 scripts/build_site.py first");
}

rmSync("public", { recursive: true, force: true });
cpSync("site", "public", { recursive: true });
