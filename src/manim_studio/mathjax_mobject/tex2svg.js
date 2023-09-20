// Solution from https://github.com/manim-kindergarten/ManimGL-MathJax/blob/main/manimgl_mathjax/tex2svg.js

MathJax = {
  loader: {
    paths: { mathjax: "mathjax-full/es5" },
    require: require,
    load: ["adaptors/liteDOM", "[tex]/color"],
  },
  tex: {
    packages: ["base", "autoload", "require", "ams", "newcommand", "xcolor"],
  },
  svg: {
    fontCache: "local",
  },
  startup: {
    typeset: false,
  },
};

// Load the MathJax startup module
require("mathjax-full/es5/tex-svg.js");

const texConfig = {
  display: true, // false 为行间公式
  em: 32,
  ex: 16,
  containerWidth: 80 * 16,
};

async function tex2svg(tex) {
  await MathJax.startup.promise;
  const dirtySvg = await MathJax.tex2svgPromise(tex, texConfig).then((node) =>
    MathJax.startup.adaptor.innerHTML(node)
  );
  const lastIndex = dirtySvg.lastIndexOf("</svg>");
  const svg = dirtySvg.slice(0, lastIndex + 6); // '</svg>'.length === 6
  return svg;
}

module.exports = tex2svg;
