## UI Design System: Forest Theme

### Core Design Philosophy

Create an interface embodying **organic serenity** and **layered growth** through the lens of the **forest**--celebrating the quiet accumulation of living systems, the patience of ancient trees, and the soft diffusion of light through a dense canopy. Inspired by old-growth forests, moss-covered stones, and the gentle geometry of ferns unfolding, UI components should feel grown rather than built, as though they emerged from the soil over centuries. The design honors **komorebi** (木漏れ日)--the dappled light filtering through leaves--as the guiding metaphor for how information is revealed.

**Guiding Principles:**
- **Seichou** (成長) -- Growth: every element should feel like it grew into its place naturally
- **Kasanari** (重なり) -- Layering: surfaces overlap like canopy leaves, creating depth through stacking
- **Shizukesa** (静けさ) -- Tranquility: the deep calm of a forest floor, undisturbed
- **Fukuzatsu** (複雑) -- Complexity from simplicity: intricate systems built from repeated, simple organic forms
- **Nenchaku** (粘着) -- Rootedness: elements feel anchored, grounded, weighty with purpose
- **Kuchiru** (朽ちる) -- Graceful decay: beauty in weathered bark, fallen leaves, the patina of age

---

### Color Palette

**Deep Foliage Tones (Backgrounds):**
- **Forest Floor**: `#1A2316` -- the darkest earth beneath the oldest trees, primary dark background
- **Understory**: `#232E1F` -- the shadow layer where ferns grow, secondary dark background
- **Loam**: `#2D3A28` -- rich soil visible between roots, elevated surface background
- **Duff Layer**: `rgba(26, 35, 22, 0.85)` -- decomposing leaves, translucent overlay background
- **Bark Wash**: `#3A4A34` -- weathered bark seen in low light, card surface alternative

**Hunter Green Tones (Primary Palette):**
- **Old Growth**: `#2E5C3E` -- the deepest, most saturated green of ancient conifers
- **Canopy**: `#3D7A52` -- mid-height foliage catching filtered light
- **Fern**: `#4A8A5E` -- the bright clarity of a forest fern in indirect light
- **Lichen**: `#6A9A74` -- pale green-gray of tree lichen, for secondary elements
- **Moss Veil**: `rgba(46, 92, 62, 0.15)` -- transparent moss-green wash for subtle tints

**Meadow Tones (Action/Interactive):**
- **Meadow**: `#5DAE5F` -- the vivid green of a sunlit clearing, primary action color
- **Meadow Bright**: `#6EC26E` -- sunstruck grass, hover state
- **Meadow Muted**: `#4D9A50` -- meadow in shade, pressed state

**Sprout Tones (Accent -- Used Sparingly):**
- **Fresh Sprout**: `#A8E06A` -- new growth pushing through dark soil, accent highlights
- **Bud**: `#C4EE8C` -- the pale yellow-green of an unfurling leaf, subtle accent
- **Tendril**: `#8ACC4A` -- climbing vine energy, for active/success indicators

**Old Parchment Tones (Text & Neutrals):**
- **Parchment**: `#E8DCC8` -- aged paper left in a cabin, primary text on dark backgrounds
- **Vellum**: `#D4C8B0` -- slightly yellowed, secondary text
- **Birch Bark**: `#C0B49A` -- peeling birch, tertiary/disabled text
- **Cobweb**: `rgba(232, 220, 200, 0.08)` -- near-invisible parchment, ghost borders

**Seasonal Accents (Contextual):**
- **Autumn Ember**: `#D4713A` -- a single turning leaf, for warnings
- **Berry**: `#C44B4B` -- forest berry, for errors and destructive actions
- **Chanterelle**: `#E0A830` -- golden mushroom, for informational highlights
- **Twilight Violet**: `#7A5A8A` -- dusk through the trees, for visited/historic states

**Material References:**
- Komorebi glow: `rgba(168, 224, 106, 0.12)` -- dappled sunlight on surfaces
- Wet moss: `#3A5A3A`
- Petrified wood: `#6A5A48`
- Morning fog between trees: `rgba(200, 210, 190, 0.06)`

---

### Typography

**Font Philosophy:** Headers should feel like carved wood or hand-lettered trail signs--organic serif forms with natural curves and visible character. Body text is warm, approachable, and effortlessly readable, like handwriting in a naturalist's field journal. Spacing is generous, evoking sunlight filtering through a canopy onto a page.

**Font Stack:**
```css
--font-primary: 'Lora', 'Palatino Linotype', 'Book Antiqua', 'Georgia', serif;
--font-body: 'Nunito Sans', 'Segoe UI', -apple-system, sans-serif;
--font-mono: 'Fira Code', 'Cascadia Code', 'SF Mono', monospace;
```

**Type Scale:**
- **Display**: 30-36px, weight 400 (regular serif, stately like old-growth trunks)
- **Heading**: 22-26px, weight 600
- **Section title**: 14-16px, weight 700, `letter-spacing: 0.10em` (uppercase, like trail markers)
- **Body**: 15-16px, weight 400, line-height 1.75
- **Small/Caption**: 12-13px, weight 400, `letter-spacing: 0.02em`
- **Whisper**: 11px, weight 300, `letter-spacing: 0.06em`, birch bark color

**Text Styling:**
- Generous line-height (1.7-1.85) for breathing room, like spacing between branches
- Headers use serif; body uses sans-serif for warm contrast
- Color hierarchy through the parchment scale: brighter parchment for emphasis, birch bark for receding text
- Avoid heavy bold in body text; use `font-weight: 600` sparingly, like strong branches among slender ones
- Optional decorative initial caps on long-form text, styled as botanical illustrations

---

### Component Patterns

#### Cards & Containers -- *Canopy Layers*

Inspired by overlapping leaves in a canopy and the way forest floors accumulate layers of organic material:

```css
.card {
  background: #2D3A28;
  border: 1px solid rgba(232, 220, 200, 0.06);
  border-radius: 8px 16px 12px 16px; /* Organic, slightly irregular, like a leaf */
  padding: 28px 32px;
  box-shadow:
    0 4px 8px rgba(10, 14, 8, 0.15),
    0 16px 48px rgba(10, 14, 8, 0.20);
  transition: box-shadow 0.4s cubic-bezier(0.23, 1, 0.32, 1),
              transform 0.4s cubic-bezier(0.23, 1, 0.32, 1);
}

.card:hover {
  box-shadow:
    0 6px 12px rgba(10, 14, 8, 0.18),
    0 24px 64px rgba(10, 14, 8, 0.25);
  transform: translateY(-2px);
}

.card-canopy {
  /* Stacked appearance: multiple overlapping surfaces */
  background: #2D3A28;
  position: relative;
}

.card-canopy::before {
  content: '';
  position: absolute;
  inset: 4px -4px -4px 4px;
  background: #232E1F;
  border-radius: inherit;
  z-index: -1;
  border: 1px solid rgba(232, 220, 200, 0.03);
}

.card-canopy::after {
  content: '';
  position: absolute;
  inset: 8px -8px -8px 8px;
  background: #1A2316;
  border-radius: inherit;
  z-index: -2;
  border: 1px solid rgba(232, 220, 200, 0.02);
}

.card-mossy {
  background: linear-gradient(170deg, #2D3A28 0%, #3A4A34 100%);
  border: 1px solid rgba(93, 174, 95, 0.08);
  box-shadow:
    inset 0 1px 0 rgba(168, 224, 106, 0.04),
    0 16px 48px rgba(10, 14, 8, 0.25);
}
```

**Border Radius Philosophy:**
- Avoid perfectly uniform roundness; mimic the gentle irregularity of natural forms
- Pair slightly different radii on each corner: `8px 16px 12px 16px`
- Larger containers use subtler variation; smaller elements can be more organic
- Reference how bark cracks into irregular rounded plates

**Depth & Shadow:**
- Shadows are large, soft, and dark--simulating canopy depth where light rarely penetrates
- Multiple shadow layers create convincing depth: near shadow + far ambient shadow
- Inner glow for moss-like luminosity: `inset 0 1px 0 rgba(168, 224, 106, 0.04)`
- Avoid sharp, hard-edged shadows; everything is diffused through foliage

---

#### Buttons & Interactive Elements -- *Meadow Stones*

```css
.button-primary {
  background: #5DAE5F;
  color: #1A2316;
  border: none;
  border-radius: 6px 12px 8px 14px; /* Organic, slightly irregular */
  padding: 12px 28px;
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 14px;
  letter-spacing: 0.02em;
  transition: all 0.35s cubic-bezier(0.23, 1, 0.32, 1);
  box-shadow: 0 2px 8px rgba(93, 174, 95, 0.20);
}

.button-primary:hover {
  background: #6EC26E;
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(93, 174, 95, 0.30);
}

.button-primary:active {
  background: #4D9A50;
  transform: translateY(0px);
  box-shadow: 0 1px 4px rgba(93, 174, 95, 0.15);
}

.button-secondary {
  background: #2E5C3E;
  color: #E8DCC8;
  border: 1px solid rgba(232, 220, 200, 0.10);
  border-radius: 6px 12px 8px 14px;
  padding: 12px 28px;
  font-weight: 600;
  font-size: 14px;
}

.button-secondary:hover {
  background: #3D7A52;
  border-color: rgba(232, 220, 200, 0.15);
}

.button-ghost {
  background: transparent;
  border: 1px solid rgba(232, 220, 200, 0.12);
  color: #D4C8B0;
  border-radius: 6px 12px 8px 14px;
  padding: 12px 28px;
}

.button-ghost:hover {
  background: rgba(93, 174, 95, 0.06);
  border-color: rgba(93, 174, 95, 0.20);
  color: #E8DCC8;
}

.button-sprout { /* Accent action -- like a bright sprout in dark soil */
  background: linear-gradient(135deg, #5DAE5F, #A8E06A);
  color: #1A2316;
  border: none;
  border-radius: 20px;
  padding: 10px 24px;
  font-weight: 700;
  box-shadow: 0 0 20px rgba(168, 224, 106, 0.15);
}
```

**Icon Buttons:**
- Rounded, organic pill shapes or soft squares
- Generous touch targets: 44px minimum
- Hover reveals a soft green glow: `background: rgba(93, 174, 95, 0.08)`
- Active state feels like pressing into soft earth: slight downward shift, reduced shadow

---

#### Form Elements -- *Root Inputs*

```css
.input {
  background: rgba(26, 35, 22, 0.60);
  border: 1px solid rgba(232, 220, 200, 0.10);
  border-radius: 6px 10px 6px 10px;
  padding: 14px 18px;
  font-size: 15px;
  font-family: var(--font-body);
  color: #E8DCC8;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.input::placeholder {
  color: #6A5A48;
  font-style: italic;
}

.input:focus {
  outline: none;
  border-color: rgba(93, 174, 95, 0.40);
  box-shadow: 0 0 0 3px rgba(93, 174, 95, 0.08);
}

.input-minimal {
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(232, 220, 200, 0.12);
  border-radius: 0;
  padding: 12px 0;
}

.input-minimal:focus {
  border-bottom-color: #5DAE5F;
  box-shadow: none;
}

.textarea {
  background: rgba(26, 35, 22, 0.60);
  border: 1px solid rgba(232, 220, 200, 0.10);
  border-radius: 8px 14px 10px 14px;
  padding: 16px 18px;
  font-size: 15px;
  color: #E8DCC8;
  line-height: 1.7;
  min-height: 120px;
  resize: vertical;
}

.checkbox {
  width: 20px;
  height: 20px;
  border: 1.5px solid rgba(232, 220, 200, 0.20);
  border-radius: 4px 6px 4px 6px;
  background: rgba(26, 35, 22, 0.40);
  transition: all 0.25s ease;
}

.checkbox:checked {
  background: #5DAE5F;
  border-color: #5DAE5F;
  /* Checkmark styled as a small leaf or organic check */
}

.select {
  background: rgba(26, 35, 22, 0.60);
  border: 1px solid rgba(232, 220, 200, 0.10);
  border-radius: 6px 10px 6px 10px;
  padding: 14px 36px 14px 18px;
  color: #E8DCC8;
  appearance: none;
  /* Dropdown arrow styled as a small downward leaf/chevron */
}

.label {
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #C0B49A;
  margin-bottom: 8px;
}
```

**Focus State Philosophy:**
- No harsh browser outlines; replace with gentle green glow
- Focus ring expands outward like roots spreading: `box-shadow: 0 0 0 3px rgba(93, 174, 95, 0.08)`
- Color shifts from neutral border to meadow green, like a plant turning toward light

---

#### Status & Feedback -- *Forest Signals*

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 14px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  border-radius: 10px 4px 10px 4px; /* Leaf-shaped asymmetry */
  background: rgba(93, 174, 95, 0.10);
  color: #A8E06A;
}

.badge-pill {
  border-radius: 20px; /* Seed-pod rounded */
  padding: 4px 16px;
}

.badge-success {
  background: rgba(168, 224, 106, 0.12);
  color: #A8E06A;
}

.badge-warning {
  background: rgba(212, 113, 58, 0.12);
  color: #D4713A;
}

.badge-error {
  background: rgba(196, 75, 75, 0.12);
  color: #C44B4B;
}

.badge-info {
  background: rgba(224, 168, 48, 0.10);
  color: #E0A830;
}

.progress-bar {
  height: 4px;
  background: rgba(232, 220, 200, 0.06);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #2E5C3E, #5DAE5F, #A8E06A);
  border-radius: 2px;
  transition: width 0.6s cubic-bezier(0.23, 1, 0.32, 1);
  /* Growth gradient: deep root green to bright sprout */
}

.toast {
  background: #2D3A28;
  border: 1px solid rgba(232, 220, 200, 0.08);
  border-left: 3px solid #5DAE5F;
  border-radius: 4px 10px 10px 4px;
  padding: 16px 20px;
  color: #E8DCC8;
  box-shadow: 0 8px 32px rgba(10, 14, 8, 0.30);
}

.toast-error {
  border-left-color: #C44B4B;
}

.toast-warning {
  border-left-color: #D4713A;
}
```

---

### Layout Principles -- *The Forest Floor*

**Spacing Scale:**
`4, 8, 12, 16, 24, 32, 48, 64, 96, 128px`

Prefer generous spacing. Let elements breathe like clearings between clusters of trees. Dense information areas should feel like thickets--tighter spacing, but still with visible space between each element.

**Grid Philosophy:**
- Layer-based layouts over flat grids; z-depth matters as much as x/y position
- Overlapping card edges suggest canopy layers: cards can peek from behind siblings by 4-8px
- Off-center focal points, as forest paths rarely run straight
- Maximum content width: 720px for reading, 1200px for applications
- Sidebar layouts feel like the forest edge: a dense navigation column opening to a wide clearing

**Visual Weight Distribution:**
```
+-----------------------------+
|  [nav]                      |
|   ||                        |
|   ||   +-------+            |   <- Primary card, slightly off-center like a dominant tree
|   ||   | Main  |  +----+    |   <- Secondary card overlaps, like understory
|   ||   |       |  |Side|    |
|   ||   +-------+  +----+    |
|   ||                        |
|   ||        ...             |   <- Scattered small elements, like forest floor debris
+-----------------------------+
```

**Dividers & Separators:**
- Thin lines with very low opacity: `1px solid rgba(232, 220, 200, 0.06)`
- Or pure negative space--clearings in the forest need no fences
- Decorative leaf or branch SVG as occasional section break, very subtle
- Gradient fades from transparent to border color and back, like a shadow cast by a branch

---

### Interaction Design -- *Growth in Motion*

**Transition Timing:**
```css
--ease-growth: cubic-bezier(0.34, 1.56, 0.64, 1); /* Slight overshoot, like a branch springing back */
--ease-settle: cubic-bezier(0.23, 1, 0.32, 1); /* Gentle settling, like a leaf landing */
--ease-unfurl: cubic-bezier(0.16, 1, 0.3, 1); /* Slow start, confident finish, like a fern unfurling */
--ease-root: cubic-bezier(0.45, 0, 0.15, 1); /* Grounded, deliberate motion */
--duration-slow: 0.6s;
--duration-medium: 0.35s;
--duration-fast: 0.2s;
--duration-growth: 0.8s; /* For expansion/reveal animations */
```

**Hover Philosophy:**
- Soft green luminosity appears beneath the element: `box-shadow: 0 0 16px rgba(93, 174, 95, 0.08)`
- Gentle lift, as though growing upward: `transform: translateY(-2px)`
- Background subtly warms: `background: rgba(93, 174, 95, 0.04)`
- Never sudden; always organic, like moss spreading slowly

**Loading States:**
- Pulsing leaf/sprout icon that gently grows and recedes
- Ring of dots that grow sequentially, like seeds sprouting in a circle
- Slow, steady growth animation--a line extending like a root through soil

```css
@keyframes forest-breathe {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.03); }
}

@keyframes sprout-grow {
  0% { transform: scaleY(0); transform-origin: bottom; opacity: 0; }
  60% { transform: scaleY(1.05); opacity: 1; }
  100% { transform: scaleY(1); opacity: 1; }
}

@keyframes root-extend {
  0% { width: 0%; opacity: 0.3; }
  100% { width: 100%; opacity: 1; }
}

@keyframes leaf-fall {
  0% { transform: translateY(-10px) rotate(0deg); opacity: 0; }
  50% { transform: translateY(5px) rotate(8deg); opacity: 1; }
  100% { transform: translateY(0px) rotate(3deg); opacity: 1; }
}

@keyframes komorebi-flicker {
  0%, 100% { opacity: 0.03; }
  25% { opacity: 0.06; }
  50% { opacity: 0.02; }
  75% { opacity: 0.05; }
}
```

**Page Transitions:**
- New content grows upward from the bottom, like a plant emerging
- Exiting content fades and shrinks slightly, returning to the soil
- Overlays darken like the forest canopy closing in

---

### Texture & Material References

**Organic Textures:**
- Subtle noise overlay simulating bark grain: `opacity: 0.03`
- Faint moss-like texture on card surfaces using CSS gradients
- Paper-like warmth on background surfaces, as though pages left in a woodland cabin

**Forest-Inspired Patterns:**
- Komorebi (dappled light): subtle, shifting radial gradients on surfaces
- Moss growth: slight green tint accumulating at edges and corners
- Root patterns: thin branching lines as decorative elements (SVG)
- Ring patterns: concentric subtle circles referencing tree cross-sections

```css
.komorebi-overlay {
  background:
    radial-gradient(ellipse at 20% 30%, rgba(168, 224, 106, 0.04) 0%, transparent 50%),
    radial-gradient(ellipse at 70% 60%, rgba(168, 224, 106, 0.03) 0%, transparent 40%),
    radial-gradient(ellipse at 50% 80%, rgba(93, 174, 95, 0.02) 0%, transparent 45%);
  pointer-events: none;
}

.bark-texture {
  background-image:
    repeating-linear-gradient(
      175deg,
      rgba(232, 220, 200, 0.01) 0px,
      rgba(232, 220, 200, 0.02) 1px,
      transparent 1px,
      transparent 4px
    );
}

.moss-edge {
  /* Subtle green tint along bottom edges */
  border-image: linear-gradient(
    to right,
    transparent 0%,
    rgba(93, 174, 95, 0.15) 30%,
    rgba(93, 174, 95, 0.15) 70%,
    transparent 100%
  ) 1;
  border-bottom: 2px solid;
}

.tree-ring-bg {
  background:
    radial-gradient(circle at center, transparent 30%, rgba(232, 220, 200, 0.02) 31%, transparent 32%),
    radial-gradient(circle at center, transparent 45%, rgba(232, 220, 200, 0.015) 46%, transparent 47%),
    radial-gradient(circle at center, transparent 60%, rgba(232, 220, 200, 0.01) 61%, transparent 62%);
}
```

---

### Iconography -- *Branch Strokes*

- Stroke-based icons, weight 1.5-2px
- Rounded line caps and joins, like branches worn smooth
- Organic, slightly irregular paths preferred over geometric perfection
- Icon size: 18-22px inline, 28-32px standalone

**Style Reference:**
```
Standard:  [ ] O ^
Forest:    ( ) o ~  (organic, rounded, grown forms)
```

Consider icons that feel hand-carved or grown:
- Slight stroke weight variation, like a twig thickening at joints
- Ends that taper naturally, like a branch tip
- Rounded, warm forms; avoid sharp angles unless representing thorns (warning/danger states)
- Leaf motifs can replace standard chevrons for navigation: a leaf pointing right for "next"

---

### Organic Imperfection Details

1. **Slightly irregular border-radius**: Each corner a different value (`8px 16px 12px 16px`) -- bark cracks unevenly
2. **Komorebi shimmer**: A faint, slow-cycling opacity animation on accent elements -- dappled light moves
3. **Warm paper textures**: Parchment undertones in all light surfaces -- nothing is pure white
4. **Moss accumulation**: Subtle green tint builds up on elements that persist on screen -- `border-bottom: 2px solid rgba(93, 174, 95, 0.15)`
5. **Hand-drawn SVG flourishes**: Slightly wobbly paths for decorative dividers -- not mathematically perfect
6. **Shadow color variation**: Shadows carry a hint of green (`rgba(20, 40, 20, 0.20)`) rather than pure black
7. **Stacking overlap**: Cards and containers overlap by 4-8px, creating canopy-like layering
8. **Grain noise**: A barely-perceptible noise texture over backgrounds (`opacity: 0.03`) evoking bark or soil
9. **Growth direction**: Elements tend to anchor at the bottom and grow upward, like plants
10. **Weathering**: Borders thicken slightly at the bottom: `border-width: 1px 1px 1.5px 1px` -- gravity pulls

---

### Recommended shadcn/ui Components

The following 22 components are most relevant to the Forest Theme. Each includes specific CSS variable overrides and styling notes to adapt the shadcn/ui `theme-stone` base to the forest palette.

**Base theme:** Start with `theme-stone` and override the following CSS custom properties globally:

```css
:root {
  /* Forest Theme Global Overrides on theme-stone */
  --background: 100 14% 11%;          /* #1A2316 Forest Floor */
  --foreground: 34 26% 85%;           /* #E8DCC8 Parchment */
  --card: 108 17% 19%;                /* #2D3A28 Loam */
  --card-foreground: 34 26% 85%;      /* #E8DCC8 Parchment */
  --popover: 108 17% 19%;             /* #2D3A28 Loam */
  --popover-foreground: 34 26% 85%;   /* #E8DCC8 Parchment */
  --primary: 121 30% 52%;             /* #5DAE5F Meadow */
  --primary-foreground: 100 14% 11%;  /* #1A2316 Forest Floor */
  --secondary: 147 32% 27%;           /* #2E5C3E Old Growth */
  --secondary-foreground: 34 26% 85%; /* #E8DCC8 Parchment */
  --muted: 108 17% 15%;              /* #232E1F Understory */
  --muted-foreground: 36 15% 67%;     /* #C0B49A Birch Bark */
  --accent: 88 68% 64%;               /* #A8E06A Fresh Sprout */
  --accent-foreground: 100 14% 11%;   /* #1A2316 Forest Floor */
  --destructive: 0 45% 53%;           /* #C44B4B Berry */
  --destructive-foreground: 34 26% 85%;
  --border: 34 26% 85% / 0.08;        /* Cobweb */
  --input: 34 26% 85% / 0.10;
  --ring: 121 30% 52% / 0.20;         /* Meadow glow */
  --radius: 0.5rem;
}
```

---

#### 1. **Button** (`@shadcn/button`)
The primary interactive element. Use meadow green for primary actions, old growth green for secondary, ghost for tertiary.

```
Styling notes:
- border-radius: 6px 12px 8px 14px (organic asymmetry)
- Primary: bg-meadow, text-forest-floor, shadow with green tint
- Secondary: bg-old-growth, text-parchment, subtle border
- Ghost: transparent, parchment text, green glow on hover
- Destructive: bg-berry, text-parchment
- Transition: 0.35s with --ease-settle
```

#### 2. **Card** (`@shadcn/card`)
The fundamental container. Overlapping surfaces simulate canopy depth.

```
Styling notes:
- background: var(--card) with optional canopy stacking (::before, ::after pseudo-layers)
- border-radius: 8px 16px 12px 16px (irregular organic corners)
- box-shadow: dual-layer (near sharp + far diffused) with green-tinted shadow color
- border: 1px solid rgba(232, 220, 200, 0.06)
- CardHeader: add moss-edge border-bottom
- CardFooter: slightly darker background, like forest floor beneath the card
```

#### 3. **Input** (`@shadcn/input`)
Rooted form field. Dark recessed background suggests planting into soil.

```
Styling notes:
- background: rgba(26, 35, 22, 0.60) -- recessed into the earth
- border: 1px solid rgba(232, 220, 200, 0.10)
- border-radius: 6px 10px 6px 10px
- focus: border-color shifts to meadow green, soft ring glow
- placeholder: petrified-wood color, italic
- color: parchment
```

#### 4. **Badge** (`@shadcn/badge`)
Leaf-shaped or pill-shaped status indicators.

```
Styling notes:
- Default: border-radius: 10px 4px 10px 4px (leaf-shaped asymmetry)
- Variant "pill": border-radius: 20px (seed-pod)
- Success: sprout-green bg tint, sprout text
- Warning: ember-orange bg tint, ember text
- Destructive: berry-red bg tint, berry text
- font-size: 11px, uppercase, letter-spacing: 0.06em
```

#### 5. **Dialog** (`@shadcn/dialog`)
Modal surfaces that feel like a clearing in the forest -- focus narrows.

```
Styling notes:
- Overlay: rgba(10, 14, 8, 0.75) -- deep canopy darkness
- Content background: #2D3A28 (Loam)
- border-radius: 10px 18px 14px 18px
- box-shadow: 0 24px 80px rgba(10, 14, 8, 0.50)
- Entry animation: sprout-grow (scale from bottom)
- Add subtle komorebi-overlay as decorative background layer
```

#### 6. **Dropdown Menu** (`@shadcn/dropdown-menu`)
Cascading menus like branches extending from a trunk.

```
Styling notes:
- background: #2D3A28 with bark-texture overlay
- border: 1px solid rgba(232, 220, 200, 0.08)
- border-radius: 6px 12px 8px 12px
- Item hover: rgba(93, 174, 95, 0.08) background
- Item active: rgba(93, 174, 95, 0.12) background
- Separator: rgba(232, 220, 200, 0.06)
- Animation: unfurl downward with --ease-unfurl
```

#### 7. **Sidebar** (`@shadcn/sidebar`)
The forest edge -- a dense navigation column.

```
Styling notes:
- background: #1A2316 (Forest Floor) or #232E1F (Understory)
- Active item: rgba(93, 174, 95, 0.10) bg with left border accent in meadow green
- Hover: rgba(93, 174, 95, 0.05) bg
- Section headers: birch-bark color, uppercase, letter-spacing: 0.10em
- Dividers: rgba(232, 220, 200, 0.04)
- Collapsed state: icons only with komorebi glow on active
- Width: 260px expanded, 64px collapsed
```

#### 8. **Tabs** (`@shadcn/tabs`)
Branch-like navigation where each tab is a limb extending from a trunk.

```
Styling notes:
- Tab list border-bottom: 1px solid rgba(232, 220, 200, 0.08)
- Active tab: text color parchment, border-bottom 2px solid meadow green
- Inactive tab: birch-bark color
- Hover: vellum color, subtle green underline fade-in
- Tab content: gentle leaf-fall entrance animation
```

#### 9. **Table** (`@shadcn/table`)
Structured data, like rings visible in a tree cross-section.

```
Styling notes:
- Header: bg #232E1F, text birch-bark, uppercase, letter-spacing: 0.08em, font-size: 12px
- Row: border-bottom rgba(232, 220, 200, 0.04)
- Row hover: rgba(93, 174, 95, 0.04) bg
- Alternating rows (optional): very subtle bg variation between #2D3A28 and #2A3725
- Cell padding: 14px 18px
```

#### 10. **Select** (`@shadcn/select`)
Dropdown selection styled as a seed pod opening to reveal options.

```
Styling notes:
- Trigger: same styling as Input
- Content: same styling as Dropdown Menu
- Selected item: meadow green text with subtle left indicator
- Chevron: organic downward leaf icon or soft chevron
- Animation: unfurl with --ease-unfurl
```

#### 11. **Accordion** (`@shadcn/accordion`)
Expanding sections that unfurl like fern fronds.

```
Styling notes:
- Item border: rgba(232, 220, 200, 0.06)
- Trigger: parchment text, hover reveals green tint
- Chevron: rotates with --ease-growth, slight overshoot
- Content: animates height with --ease-unfurl over --duration-growth
- Open state: subtle left border in meadow green
```

#### 12. **Avatar** (`@shadcn/avatar`)
Organic profile indicators, like stones on the forest floor.

```
Styling notes:
- border-radius: 50% for standard, or 45% 55% 50% 50% for organic variant
- border: 2px solid rgba(232, 220, 200, 0.10)
- Fallback bg: #2E5C3E with parchment text
- Ring indicator (online): #A8E06A sprout green
- Size: 32px inline, 40px standard, 64px large
```

#### 13. **Toast / Sonner** (`@shadcn/sonner`)
Notification leaves that drift in from the edge.

```
Styling notes:
- background: #2D3A28
- border: 1px solid rgba(232, 220, 200, 0.08)
- border-left: 3px solid (color varies by type: meadow/ember/berry/chanterelle)
- border-radius: 4px 10px 10px 4px
- Entry animation: leaf-fall (slight rotation, settling)
- shadow: 0 8px 32px rgba(10, 14, 8, 0.30)
```

#### 14. **Progress** (`@shadcn/progress`)
Growth indicator, like a vine extending across a surface.

```
Styling notes:
- Track: rgba(232, 220, 200, 0.06), height 4px, border-radius 2px
- Fill: linear-gradient(90deg, #2E5C3E, #5DAE5F, #A8E06A) -- root to sprout
- Transition: width 0.6s --ease-settle
- Indeterminate: root-extend animation looping
```

#### 15. **Switch** (`@shadcn/switch`)
Toggle like a stone rolling between moss patches.

```
Styling notes:
- Track off: rgba(232, 220, 200, 0.10)
- Track on: #2E5C3E (Old Growth)
- Thumb: #E8DCC8 (Parchment) -- like a smooth stone
- Thumb shadow: 0 1px 3px rgba(10, 14, 8, 0.20)
- Transition: 0.3s --ease-growth (slight overshoot on toggle)
```

#### 16. **Tooltip** (`@shadcn/tooltip`)
Brief whispers of information, like wind through leaves.

```
Styling notes:
- background: #232E1F
- color: #D4C8B0
- border: 1px solid rgba(232, 220, 200, 0.08)
- border-radius: 4px 8px 4px 8px
- font-size: 13px
- padding: 6px 12px
- shadow: 0 4px 12px rgba(10, 14, 8, 0.25)
- Animation: gentle fade + slight translateY with --ease-settle
```

#### 17. **Separator** (`@shadcn/separator`)
Forest floor dividers -- barely there.

```
Styling notes:
- color: rgba(232, 220, 200, 0.06)
- height: 1px
- Optional moss-edge variant with green gradient tint
- Use generous margin (24-32px) -- clearings between trees
```

#### 18. **Scroll Area** (`@shadcn/scroll-area`)
Scrollable regions with vine-like scrollbar.

```
Styling notes:
- Scrollbar track: transparent
- Scrollbar thumb: rgba(232, 220, 200, 0.12), border-radius: 4px
- Scrollbar thumb hover: rgba(232, 220, 200, 0.20)
- Scrollbar width: 6px
- Fade edges: subtle gradient mask at top/bottom for content overflow hint
```

#### 19. **Navigation Menu** (`@shadcn/navigation-menu`)
Primary navigation structured like a trail map.

```
Styling notes:
- Link color: vellum, hover: parchment
- Active indicator: 2px bottom border in meadow green
- Dropdown viewport: loam background with bark-texture overlay
- Trigger hover: rgba(93, 174, 95, 0.06) background
- Transition: --ease-unfurl for dropdown reveal
```

#### 20. **Skeleton** (`@shadcn/skeleton`)
Placeholder shapes that pulse like life beneath the soil.

```
Styling notes:
- background: rgba(232, 220, 200, 0.04)
- Animation: forest-breathe (slow pulse, 3s cycle)
- border-radius: match the component being loaded (organic values)
- Shimmer gradient: subtle sweep of rgba(232, 220, 200, 0.06)
```

#### 21. **Alert** (`@shadcn/alert`)
Information panels styled as trail markers.

```
Styling notes:
- background: rgba(46, 92, 62, 0.10) for default
- border-left: 3px solid (meadow for info, ember for warning, berry for error, sprout for success)
- border-radius: 4px 10px 10px 4px (matches toast)
- Icon: organic stroke style, 20px
- Title: font-weight 600, parchment
- Description: vellum color, line-height 1.7
```

#### 22. **Slider** (`@shadcn/slider`)
A branch with a sliding stone marker.

```
Styling notes:
- Track: rgba(232, 220, 200, 0.08), height 4px, border-radius 2px
- Range (filled): #2E5C3E (Old Growth)
- Thumb: 18px circle, bg #E8DCC8, border 2px solid #5DAE5F
- Thumb hover: box-shadow 0 0 0 4px rgba(93, 174, 95, 0.12)
- Thumb active: scale(1.1), bg #5DAE5F
```

---

#### Block Pattern Notes

For dashboard and page layouts using shadcn blocks:

- **dashboard-01**: Use forest-floor background. Cards in loam with canopy stacking. Charts use the green gradient palette (old-growth through sprout).
- **sidebar-01 through sidebar-16**: Apply forest-edge sidebar styling. Dark understory background, meadow-green active indicators, birch-bark section labels.
- **login-01 through login-05**: Center card on forest-floor background with komorebi-overlay. Use sprout button for primary action. Input fields recessed into dark soil.
- **Chart color sequences**: `#2E5C3E`, `#3D7A52`, `#5DAE5F`, `#A8E06A`, `#C4EE8C`, `#E0A830`, `#D4713A` -- moving from deep roots to bright canopy to autumn accents.

---

### Key Design Principles Summary

1. **Grown, not built** -- Components should feel organic, as though they emerged naturally from the interface soil
2. **Canopy layering** -- Depth comes from overlapping surfaces with large, soft shadows; z-axis is as important as x/y
3. **Komorebi illumination** -- Light is dappled, indirect, and warm; never harsh spotlights, always filtered through leaves
4. **Rooted interaction** -- Elements are anchored; motion is upward growth, not lateral sliding
5. **Parchment legibility** -- Warm, aged text tones on deep green backgrounds ensure readability while maintaining warmth
6. **Meadow moments** -- Reserve the brightest greens (meadow, sprout) for meaningful actions and key indicators
7. **Organic asymmetry** -- No corner radius should match its opposite; irregularity signals natural origin
8. **Patient animation** -- Transitions are unhurried, like growth; use longer durations (0.4-0.8s) with organic easing
9. **Forest silence** -- Generous negative space is the quiet of the forest floor; resist the urge to fill every gap
10. **Seasonal awareness** -- Amber and berry accents provide seasonal contrast against the dominant greens, used sparingly like autumn among evergreens

---

*"The clearest way into the Universe is through a forest wilderness."* -- John Muir
