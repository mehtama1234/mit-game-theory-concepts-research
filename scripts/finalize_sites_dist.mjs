import { cpSync, existsSync, mkdirSync } from "node:fs";

if (!existsSync("dist/server/index.js")) {
  throw new Error("dist/server/index.js is missing after vinext build");
}

mkdirSync("dist/.openai", { recursive: true });
cpSync(".openai/hosting.json", "dist/.openai/hosting.json");
