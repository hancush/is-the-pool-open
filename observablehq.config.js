// See https://observablehq.com/framework/config for documentation.
export default {
  // The project’s title; used in the sidebar and webpage titles.
  title: "Is The Pool Open",

  // The pages and sections in the sidebar. If you don’t specify this option,
  // all pages will be listed in alphabetical order. Listing pages explicitly
  // lets you organize them into sections and have unlisted pages.
  // pages: [
  //   {
  //     name: "Examples",
  //     pages: [
  //       {name: "Dashboard", path: "/example-dashboard"},
  //       {name: "Report", path: "/example-report"}
  //     ]
  //   }
  // ],

  // Content to add to the head of the page, e.g. for a favicon:
  head: `
    <link rel="icon" href="favicon.ico" type="image/png" sizes="32x32">

    <!-- Primary Meta Tags -->
    <title>Is The Pool Open????</title>
    <meta name="title" content="Is The Pool Open????" />
    <meta name="description" content="Find an open Chicago Park District pool near you!" />

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://metatags.io/" />
    <meta property="og:title" content="Is The Pool Open????" />
    <meta property="og:description" content="Find an open Chicago Park District pool near you!" />
    <meta property="og:image" content="https://github.com/hancush/is-the-pool-open/blob/main/src/preview.png?raw=true" />

    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image" />
    <meta property="twitter:url" content="https://metatags.io/" />
    <meta property="twitter:title" content="Is The Pool Open????" />
    <meta property="twitter:description" content="Find an open Chicago Park District pool near you!" />
    <meta property="twitter:image" content="https://github.com/hancush/is-the-pool-open/blob/main/src/preview.png?raw=true" />
  `,

  // The path to the source root.
  root: "src",

  // Some additional configuration options and their defaults:
  // theme: "default", // try "light", "dark", "slate", etc.
  // header: "", // what to show in the header (HTML)
  footer: `Built with Observable by <a href="https://github.com/hancush" target="_blank">Hannah Cushman Garland</a>. ✨`,
  // sidebar: true, // whether to show the sidebar
  // toc: true, // whether to show the table of contents
  // pager: true, // whether to show previous & next links in the footer
  // output: "dist", // path to the output root for build
  // search: true, // activate search
  // linkify: true, // convert URLs in Markdown to links
  // typographer: false, // smart quotes and other typographic improvements
  // cleanUrls: true, // drop .html from URLs
};
