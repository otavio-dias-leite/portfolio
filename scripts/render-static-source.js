const fs = require("node:fs");
const { JSDOM } = require("jsdom");

const input = process.argv[2] || "index.html";
const output = process.argv[3] || "dist/index.html";
const source = fs.readFileSync(input, "utf8");
const dom = new JSDOM(source, {
  url: "https://otavio-dias-leite.github.io/portfolio/",
  runScripts: "dangerously"
});
fs.mkdirSync(require("node:path").dirname(output), { recursive: true });
fs.writeFileSync(output, dom.serialize(), "utf8");
dom.window.close();
