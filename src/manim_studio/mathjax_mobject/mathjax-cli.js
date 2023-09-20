// Solution from https://github.com/manim-kindergarten/ManimGL-MathJax/blob/main/manimgl_mathjax/index.js
/**
 * This file reads asciimath string from stdin and output svg formula to
 * stdout.  On linux you can end the input with ctrl-d; unfortunately on
 * windows this is not possible, so you may use ctrl-c to interrupt the
 * input.
 *
 * Another option is to redirect from file:
 *   $ node index.js < input.txt
 * On windows, quote is needed:
 *   $ "node" index.js < input.txt
 */

const { am2tex } = require("asciimath-js");
const tex2svg = require("./tex2svg.js");
const { stdin, stdout } = process;
const buf = [];

stdin.setEncoding("utf8");

stdin.on("readable", () => {
  let data;
  while ((data = stdin.read()) !== null) {
    buf.push(data.trim());
  }
});

const convert =
  process.argv[2] === "--am" ? (input) => tex2svg(am2tex(input)) : tex2svg;

function onEnd() {
  const input = buf.join("\n");
  convert(input).then((svg) => {
    console.log(svg);
    process.exit();
  });
}

stdin.on("end", onEnd);
process.on("SIGINT", onEnd);
