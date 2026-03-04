# Design Plan: Forest Fluidity

## Objective
Recreate the website to be **attractive**, **fluid**, and **minimalistic**, using the existing "Forest" color palette.

## Design Philosophy
- **Minimalism**: Remove visual clutter (heavy borders, default tables). Use whitespace to group content.
- **Fluidity**: Implement smooth transitions, hover effects, and a layout that adapts gracefully to screen sizes. Use glassmorphism to create depth.
- **Atmosphere**: evoked by the "Forest" theme - deep greens, soft light, organic shapes.

## Key Changes

### 1. Visual Style (CSS)
- **Background**: subtle gradient based on the `background` variable to add depth.
- **Glassmorphism**: Use semi-transparent backgrounds (`backdrop-filter: blur(10px)`) for the header and content cards to mimic looking through mist or water.
- **Typography**: Increase line height and spacing for better readability. Use the `Lora` serif font for headings to give a classy, organic feel.
- **Borders**: Soft, rounded corners (`border-radius: 1rem`) to mimic organic softness.

### 2. Layout Structure (HTML)
- **Navigation**: A floating, sticky header with a "glass" effect.
- **Hero Section**: A clean, centered welcome message.
- **Content**: Replace the rigid HTML `<table>` with a **Responsive Grid of Cards**. Each logistical detail (Date, Location, etc.) will be its own card. This breaks the grid-lock of tables and allows for more fluid movement.

### 3. Interactions & Animations
- **Entrance Animation**: Content will fade in and slide up slightly upon page load.
- **Hover Effects**: Cards will gently lift and glow (brighten) when hovered.
- **Smooth Scrolling**: Enabled globally.

## implementation Steps
1.  **Refactor `style.css`**: Update variables, add animations, styling for glass cards, and responsive grid layouts.
2.  **Refactor `index.html`**: Convert the table into a `div` structure with classes for the grid layout. Apply new classes.
