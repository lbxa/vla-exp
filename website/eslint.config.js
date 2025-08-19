import eslintPluginAstro from 'eslint-plugin-astro';
import tailwindcss from 'eslint-plugin-tailwindcss';
import typescriptEslintParser from '@typescript-eslint/parser';

export default [
  // Ignore patterns first
  {
    ignores: [
      'dist/',
      'node_modules/',
      '.astro/',
      'bun.lockb',
      '*.lock',
    ],
  },
  
  // Astro recommended configuration
  ...eslintPluginAstro.configs.recommended,
  
  // Tailwind CSS configuration
  ...tailwindcss.configs['flat/recommended'],
  
  // TypeScript and JavaScript files
  {
    files: ['**/*.{js,ts}'],
    languageOptions: {
      parser: typescriptEslintParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
    rules: {
      // Tailwind CSS rules
      'tailwindcss/classnames-order': 'warn',
      'tailwindcss/no-custom-classname': 'warn',
      'tailwindcss/enforces-shorthand': 'warn',
      
      // General rules
      'no-console': 'warn',
      'no-unused-vars': 'warn',
      'prefer-const': 'error',
    },
  },
  
  // Astro files specific configuration
  {
    files: ['**/*.astro'],
    rules: {
      // Astro specific rules
      'astro/no-conflict-set-directives': 'error',
      'astro/no-unused-define-vars-in-style': 'error',
      
      // Tailwind CSS rules for Astro files
      'tailwindcss/classnames-order': 'warn',
      'tailwindcss/no-custom-classname': 'warn',
      'tailwindcss/enforces-shorthand': 'warn',
      
      // Allow console in Astro files (for development)
      'no-console': 'off',
    },
  },
];