import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import tailwind from '@astrojs/tailwind';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import icon from 'astro-icon';

// https://astro.build/config
export default defineConfig({
  site: "https://vla.lbxa.net",

  prefetch: {
    prefetchAll: true,
    defaultStrategy: "viewport"
  },

  integrations: [
    mdx({
      remarkPlugins: [remarkMath],
      rehypePlugins: [rehypeKatex],
      syntaxHighlight: 'shiki',
      shikiConfig: {
        themes: { 
          light: "one-light",
          dark: "dark-plus",
        },
      }
    }), 
    tailwind(),
    icon({
      iconDir: "src/assets/icons",
    })
  ],
});
