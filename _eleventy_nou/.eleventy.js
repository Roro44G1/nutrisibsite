module.exports = function(eleventyConfig) {
  // Copiaza folderul imagini
  eleventyConfig.addPassthroughCopy("imagini");
  // Copiaza CSS-urile
  eleventyConfig.addPassthroughCopy("*.css");
  // Copiaza JS-urile
  eleventyConfig.addPassthroughCopy("*.js");

  return {
    dir: {
      input: ".",
      output: "_site",
      includes: "_includes"
    }
  };
};
