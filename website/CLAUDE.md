# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Astro project named "vla-exp" configured as a research thesis showcase website. The project uses Bun as the package manager, MDX for content sections, and Tailwind CSS for styling. It's designed to display academic research work with support for images, videos, and structured content sections.

## Common Commands

The project uses Bun as the package manager. All commands should be run from the root directory:

- `bun install` - Install dependencies
- `bun dev` - Start development server at localhost:4321
- `bun build` - Build production site to ./dist/
- `bun preview` - Preview production build locally
- `bun astro check` - Run TypeScript and Astro checks
- `bun astro add <integration>` - Add Astro integrations

## Architecture

This is a research showcase website with the following structure:

### Content Management
- **src/content/sections/** - MDX files for each research paper section
- **src/content/config.ts** - Content collections configuration
- **public/images/** - Static images for figures and diagrams
- **public/videos/** - Video files for demonstrations

### Components
- **src/layouts/ResearchLayout.astro** - Main layout with navigation and responsive design
- **src/components/SectionContainer.astro** - Wrapper for content sections with academic prose styling
- **src/components/Figure.astro** - Image display with captions and responsive behavior
- **src/components/VideoPlayer.astro** - Video player with controls and accessibility features

### Styling
- **Tailwind CSS** with typography plugin for academic content
- **Responsive design** optimized for research paper presentation
- **Academic styling** inspired by research websites

## Content Structure

The research content is organized into 8 MDX sections:

1. **01-hero.mdx** - Title, authors, affiliations, links, and demo video
2. **02-abstract.mdx** - Research summary and key contributions
3. **03-introduction.mdx** - Problem statement and motivation
4. **04-methodology.mdx** - Technical approach and implementation
5. **05-experiments.mdx** - Experimental setup, results, and demos
6. **06-discussion.mdx** - Analysis of results and implications
7. **07-conclusion.mdx** - Summary and future work directions
8. **08-references.mdx** - Citations and related resources

## Key Features

- **MDX Content Collections** - Easy content management with frontmatter
- **Media Support** - Optimized image and video components
- **Responsive Navigation** - Smooth scrolling with active section highlighting
- **Academic Styling** - Clean, professional design for research presentation
- **Copy-Paste Friendly** - Designed for easy content transfer from Notion

## Development Workflow

1. **Content Updates** - Modify MDX files in `src/content/sections/`
2. **Media Assets** - Add images to `public/images/` and videos to `public/videos/`
3. **Styling Changes** - Modify component styles or Tailwind configuration
4. **Component Updates** - Edit components in `src/components/` for functionality changes

## Technical Stack

- **Astro 5.x** with TypeScript support
- **MDX integration** for rich content authoring
- **Tailwind CSS** with typography plugin
- **Bun** package manager
- **Content Collections** for structured content management