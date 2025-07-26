# Noodle Concierge Design System

## Overview

The Noodle Concierge Design System is a comprehensive visual and interaction framework for property management dashboard applications. Built on modern web technologies including Next.js 14, TypeScript, Tailwind CSS, and shadcn/ui components, this system provides a cohesive, scalable, and accessible user experience.

**Key Principles:**
- **Consistency**: Unified visual language across all components
- **Accessibility**: WCAG-compliant design patterns
- **Scalability**: Modular component architecture
- **Performance**: Optimized assets and efficient styling
- **Maintainability**: Clean code patterns with TypeScript

## Table of Contents

1. [Foundation](#foundation)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Components](#components)
6. [Navigation](#navigation)
7. [Data Visualization](#data-visualization)
8. [Icons & Assets](#icons--assets)
9. [Implementation Guide](#implementation-guide)

---

## Foundation

### Technology Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with CSS Custom Properties
- **Components**: shadcn/ui (built on Radix UI primitives)
- **Icons**: Lucide React + Custom SVG assets
- **Font**: Poppins (Google Fonts)
- **Utilities**: clsx + tailwind-merge for className management

### File Structure

```
project/
├── app/
│   ├── globals.css           # Global styles & CSS variables
│   └── layout.tsx           # Root layout with font configuration
├── components/
│   ├── ui/                  # Base shadcn/ui components
│   ├── layout/              # Layout components (Navigation)
│   ├── dashboard/           # Dashboard-specific components
│   └── tenants/             # Tenant management components
├── lib/
│   └── utils.ts             # Utility functions (cn helper)
├── public/                  # Static assets (SVG icons)
├── tailwind.config.ts       # Tailwind configuration
└── components.json          # shadcn/ui configuration
```

---

## Color System

### CSS Custom Properties

The design system uses HSL color values stored as CSS custom properties for maximum flexibility and theme support.

#### Light Theme (Default)

```css
:root {
  --background: 99 2% 99%;           /* #fcfcfc - App background */
  --foreground: 222.2 84% 4.9%;      /* #0f0f23 - Primary text */
  --card: 0 0% 100%;                 /* #ffffff - Card backgrounds */
  --card-foreground: 222.2 84% 4.9%; /* #0f0f23 - Card text */
  --primary: 221.2 83.2% 53.3%;      /* #3b82f6 - Primary blue */
  --primary-foreground: 210 40% 98%; /* #f8fafc - Primary text */
  --secondary: 210 40% 96%;          /* #f1f5f9 - Secondary gray */
  --secondary-foreground: 222.2 84% 4.9%; /* #0f0f23 - Secondary text */
  --muted: 210 40% 96%;              /* #f1f5f9 - Muted backgrounds */
  --muted-foreground: 215.4 16.3% 46.9%; /* #64748b - Muted text */
  --accent: 210 40% 96%;             /* #f1f5f9 - Accent backgrounds */
  --accent-foreground: 222.2 84% 4.9%; /* #0f0f23 - Accent text */
  --destructive: 0 84.2% 60.2%;      /* #ef4444 - Error/danger */
  --destructive-foreground: 210 40% 98%; /* #f8fafc - Error text */
  --border: 214.3 31.8% 91.4%;       /* #e2e8f0 - Border color */
  --input: 214.3 31.8% 91.4%;        /* #e2e8f0 - Input borders */
  --ring: 221.2 83.2% 53.3%;         /* #3b82f6 - Focus rings */
  --radius: 0.5rem;                  /* 8px - Base border radius */
}
```

#### Dark Theme Support

```css
.dark {
  --background: 222.2 84% 4.9%;      /* #0f0f23 - Dark background */
  --foreground: 210 40% 98%;         /* #f8fafc - Light text */
  --card: 222.2 84% 4.9%;            /* #0f0f23 - Dark card */
  --primary: 210 40% 98%;            /* #f8fafc - Light primary */
  --secondary: 217.2 32.6% 17.5%;    /* #1e293b - Dark secondary */
  --muted: 217.2 32.6% 17.5%;       /* #1e293b - Dark muted */
  --border: 217.2 32.6% 17.5%;      /* #1e293b - Dark borders */
  /* ... additional dark theme variables */
}
```

### Application-Specific Colors

#### KPI Card Colors
```css
/* KPI Card Palette */
background: #F8F5F4;    /* Warm beige background */
title: #94827C;         /* Brownish-gray titles */
value: #6C6664;         /* Dark gray values */
```

#### Lifecycle Card Color Schemes

```css
/* All Tenants */
background: #A5FFEB;    /* Light mint green */
accent: #29DFB6;        /* Mint green */

/* Pre-Move In */
background: #FFE4C2;    /* Light orange */
accent: #F2BE7C;        /* Orange */

/* Move In */
background: #FFDBF5;    /* Light pink */
accent: #DB97C8;        /* Pink */

/* Living */
background: #E5D9FF;    /* Light purple */
accent: #8677A5;        /* Purple */

/* Renewing */
background: #B3D5FF;    /* Light blue */
accent: #5184C2;        /* Blue */
```

#### Navigation Colors
```css
/* Navigation Palette */
background: #FCFCFC;    /* App background */
border: #F2F2F2;        /* Button borders */
text: #000000;          /* Button text */
active-bg: #FFFFFF;     /* Active button background */
```

### Usage in Tailwind

Colors are accessed through Tailwind's semantic naming:

```typescript
// Examples
className="bg-background text-foreground"
className="border-border"
className="text-primary bg-primary-foreground"
```

---

## Typography

### Font Configuration

**Primary Font**: Poppins (Google Fonts)
- **Weights**: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)
- **Display**: Swap for performance
- **Fallback**: system-ui, sans-serif

```typescript
// app/layout.tsx
import { Poppins } from 'next/font/google'

const poppins = Poppins({ 
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  display: 'swap',
  variable: '--font-poppins'
})
```

### Typography Scale

#### Text Sizes
- `text-xs`: 12px - Small labels, descriptions
- `text-sm`: 14px - Body text, button text
- `text-base`: 16px - Default body text
- `text-lg`: 18px - Card titles, section headers
- `text-xl`: 20px - Page titles
- `text-2xl`: 24px - Large headings
- `text-8xl`: 128px - Large display numbers (KPI values)

#### Font Weights
- `font-normal`: 400 - Body text
- `font-medium`: 500 - Buttons, labels
- `font-semibold`: 600 - Headings
- `font-bold`: 700 - Emphasis

#### Line Heights
- `leading-tight`: 1.25 - Headlines
- `leading-normal`: 1.5 - Body text
- `leading-none`: 1 - Large display text

### Typography Patterns

#### Navigation Text
```typescript
className="font-medium text-black text-sm"
style={{ fontFamily: 'Poppins, system-ui, sans-serif' }}
```

#### Card Titles
```typescript
className="text-lg font-medium text-black"
```

#### KPI Values
```typescript
className="text-8xl font-light"
style={{ lineHeight: '1', color: '#6C6664' }}
```

#### Descriptions
```typescript
className="text-xs opacity-75 text-black"
```

---

## Spacing & Layout

### Spacing Scale

Based on Tailwind's default spacing scale (0.25rem = 4px increments):

- `1`: 4px
- `2`: 8px
- `3`: 12px
- `4`: 16px
- `5`: 20px
- `6`: 24px
- `8`: 32px
- `10`: 40px
- `12`: 48px
- `16`: 64px
- `20`: 80px
- `24`: 96px

### Layout Patterns

#### Container System
```typescript
// Navigation container
style={{
  paddingLeft: '200px',
  paddingRight: '200px'
}}

// Max width container
className="container mx-auto px-8" // 1400px max-width, centered
```

#### Grid Systems
```typescript
// Lifecycle cards (5 columns)
className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4"

// KPI cards (4 columns)
className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
```

#### Card Padding
- **Standard**: `p-6` (24px)
- **Header**: `p-6` (24px)
- **Content**: `p-6 pt-0` (24px sides, no top)

#### Button Spacing
- **Standard**: `px-4 py-2` (16px horizontal, 8px vertical)
- **Small**: `px-3` (12px horizontal)
- **Large**: `px-8` (32px horizontal)

---

## Components

### Base Components (shadcn/ui)

#### Button

**Variants**:
- `default`: Primary blue button
- `destructive`: Red for dangerous actions
- `outline`: Border-only with hover states
- `secondary`: Light gray background
- `ghost`: Transparent with hover
- `link`: Text-only with underline hover

**Sizes**:
- `default`: `h-10 px-4 py-2` (40px height)
- `sm`: `h-9 px-3` (36px height)
- `lg`: `h-11 px-8` (44px height)
- `icon`: `h-10 w-10` (40px square)

```typescript
// Usage examples
<Button variant="default" size="default">Save</Button>
<Button variant="outline" size="sm">Cancel</Button>
<Button variant="ghost" size="icon"><Settings /></Button>
```

#### Card

**Structure**:
```typescript
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>
    Content here
  </CardContent>
  <CardFooter>
    Footer actions
  </CardFooter>
</Card>
```

**Styling**:
- Rounded borders with subtle shadow
- White background in light mode
- Proper spacing with `space-y-1.5` in header

#### Input

**Features**:
- Standard height: `h-10` (40px)
- Rounded borders with focus rings
- Proper disabled states
- File input support

```typescript
<Input 
  type="text" 
  placeholder="Search tenants..." 
  className="max-w-sm"
/>
```

#### Badge

**Variants**:
- `default`: Primary colored
- `secondary`: Light gray
- `destructive`: Red for errors
- `outline`: Border-only
- `warning`: Orange (custom)
- `success`: Green (custom)

```typescript
<Badge variant="default">Active</Badge>
<Badge variant="outline">Pending</Badge>
```

### Border Radius System

```css
/* CSS Variables */
--radius: 0.5rem; /* 8px base */

/* Tailwind Classes */
.rounded-lg { border-radius: var(--radius); }           /* 8px */
.rounded-md { border-radius: calc(var(--radius) - 2px); } /* 6px */
.rounded-sm { border-radius: calc(var(--radius) - 4px); } /* 4px */
.rounded-full { border-radius: 9999px; }                  /* Full radius */
```

**Custom Border Radius**:
- **Lifecycle Cards**: `0px 20px 0px 20px` (asymmetric)

---

## Navigation

### Navigation Bar Specifications

**Container**:
- Background: `#FCFCFC`
- Full width with flex layout
- Horizontal padding: 200px on desktop
- Vertical padding: 16px (`py-4`)

**Logo Section**:
- Logo dimensions: 160x20px (auto height scaling)
- SVG format: `/logo.svg`
- Clickable link to dashboard

**Navigation Buttons**:
- Shape: Pill-shaped (`rounded-full`)
- Height: 44px fixed
- Border: 1px solid `#F2F2F2`
- Padding: `px-4 py-2`
- Font: Poppins medium, 14px
- Color: `#000000`
- Transition: 200ms all properties

**Button States**:
```typescript
// Default state
className="bg-transparent border-gray-200 hover:bg-gray-50"

// Active state
className="bg-white border-gray-200 shadow-sm"
```

**Icons**:
- Size: 16x16px
- Spacing: 8px from text (`space-x-2`)
- SVG format with proper alt text

**Right Section**:
- Property name: 18px medium text, `#374151`
- Settings button: Ghost variant, icon size
- Flex alignment: `items-center space-x-4`

### Navigation Implementation

```typescript
<nav className="flex items-center justify-between w-full py-4" 
     style={{backgroundColor: '#FCFCFC', paddingLeft: '200px', paddingRight: '200px'}}>
  
  {/* Logo */}
  <div className="flex items-center space-x-4">
    <Link href="/dashboard">
      <Image src="/logo.svg" alt="Logo" width={160} height={20} />
    </Link>
  </div>

  {/* Navigation Links */}
  <div className="flex items-center space-x-2">
    <NavigationButton 
      href="/dashboard" 
      icon="/home-icon.svg" 
      label="Home" 
      active={pathname === '/dashboard'} 
    />
    <NavigationButton 
      href="/tenants" 
      icon="/managed-tenants-icon.svg" 
      label="Managed Tenants" 
      active={pathname === '/tenants'} 
    />
  </div>

  {/* Right Section */}
  <div className="flex items-center space-x-4">
    <span className="text-lg font-medium text-gray-700">Property Name</span>
    <Button variant="ghost" size="icon">
      <Settings className="w-5 h-5" />
    </Button>
  </div>
</nav>
```

---

## Data Visualization

### KPI Cards

**Purpose**: Display key performance indicators with emphasis on numerical values.

**Design Specifications**:
- Background: `#F8F5F4` (warm beige)
- Aspect ratio: 1.5:1 (width to height)
- Minimum height: 180px
- Padding: 24px (`p-6`)
- Shadow: Light (`shadow-sm`)
- Border: None

**Typography**:
- Title: 16px medium, `#94827C`
- Value: 48px medium, `#6C6664`, line-height: 1
- Subtitle: 16px, `#94827C`

**Layout Pattern**:
```typescript
<div className="h-full flex flex-col justify-between">
  <div>
    <p style={{ color: '#94827C' }}>{title}</p>
  </div>
  <div className="flex flex-col items-end">
    <div style={{ 
      fontSize: '48px', 
      fontWeight: '500', 
      color: '#6C6664',
      lineHeight: '1'
    }}>
      {value}
    </div>
    <p style={{ color: '#94827C' }}>{subtitle}</p>
  </div>
</div>
```

### Lifecycle Cards

**Purpose**: Visual filters for tenant lifecycle stages with real-time counts.

**Design Specifications**:
- Custom border radius: `0px 20px 0px 20px`
- Shadow: Light with hover enhancement
- Clickable with cursor pointer
- Active state: 2px outline in accent color with 2px offset
- Transitions: 200ms duration

**Color Schemes**: (See Color System section for complete palette)

**Layout Structure**:
```typescript
<div className="lifecycle-card" style={{
  backgroundColor: cardColor,
  borderRadius: '0px 20px 0px 20px',
  outline: isActive ? `2px solid ${accentColor}` : 'none',
  outlineOffset: isActive ? '2px' : '0'
}}>
  {/* Header */}
  <div className="flex items-start justify-between">
    <div className="flex items-center space-x-3">
      <Image src={iconSrc} width={48} height={48} />
      <div>
        <h3 className="text-lg font-medium text-black">{title}</h3>
        <p className="text-xs opacity-75 text-black">{description}</p>
      </div>
    </div>
  </div>
  
  {/* Footer */}
  <div className="flex items-end justify-between mt-4">
    <div className="flex items-center space-x-2">
      <Filter className="w-4 h-4" />
      <span className="text-sm font-medium text-black">Filter</span>
    </div>
    <div style={{ 
      fontSize: '96px', 
      fontWeight: '300', 
      color: accentColor,
      lineHeight: '1'
    }}>
      {count}
    </div>
  </div>
</div>
```

**Icon Specifications**:
- Format: SVG
- Size: 48x48px
- Style: Circular design
- Location: `/public/[lifecycle]-icon.svg`

---

## Icons & Assets

### Icon System

**Primary Icons** (Lucide React):
- `Settings`: Navigation settings
- `Filter`: Lifecycle card filters
- `Search`: Search functionality
- All standard UI icons

**Custom SVG Icons** (in `/public/`):
- `logo.svg`: Brand logo (160x20px)
- `home-icon.svg`: Home navigation (16x16px)
- `managed-tenants-icon.svg`: Tenants navigation (16x16px)
- `all-tenants-icon.svg`: All tenants lifecycle (48x48px)
- `pre-move-in-icon.svg`: Pre-move-in lifecycle (48x48px)
- `move-in-icon.svg`: Move-in lifecycle (48x48px)
- `living-icon.svg`: Living lifecycle (48x48px)
- `renewing-icon.svg`: Renewing lifecycle (48x48px)

### Asset Usage

**Next.js Image Component**:
```typescript
<Image
  src="/icon-name.svg"
  alt="Descriptive alt text"
  width={expectedWidth}
  height={expectedHeight}
  className="w-auto h-auto" // Responsive scaling
  priority={isAboveFold} // For critical assets
/>
```

**Icon Naming Convention**:
- Use kebab-case: `icon-name.svg`
- Descriptive names: `managed-tenants-icon.svg`
- Lifecycle icons: `[stage]-icon.svg`

---

## Implementation Guide

### Getting Started

1. **Install Dependencies**:
```bash
npm install next react react-dom typescript tailwindcss
npm install @radix-ui/react-* class-variance-authority clsx tailwind-merge
npm install lucide-react @next/font
```

2. **Configure Tailwind**:
```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Import CSS custom properties
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        // ... (complete color system)
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        'poppins': ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

3. **Setup CSS Variables**:
```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  /* Copy complete CSS custom properties from Color System section */
}

@layer base {
  body {
    font-family: var(--font-poppins), system-ui, sans-serif;
    background-color: #fcfcfc;
  }
}
```

4. **Configure Font**:
```typescript
// app/layout.tsx
import { Poppins } from 'next/font/google'

const poppins = Poppins({ 
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  display: 'swap',
  variable: '--font-poppins'
})

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={poppins.variable}>
      <body className={poppins.className}>
        {children}
      </body>
    </html>
  )
}
```

### Component Development

#### Creating New Components

1. **Follow shadcn/ui patterns**:
```typescript
import React from "react"
import { cn } from "@/lib/utils"

interface ComponentProps {
  className?: string
  // ... other props
}

const Component = React.forwardRef<HTMLDivElement, ComponentProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("base-styles", className)}
      {...props}
    />
  )
)
Component.displayName = "Component"

export { Component }
```

2. **Use CSS custom properties**:
```typescript
// Instead of hardcoded colors
className="bg-blue-500 text-white"

// Use semantic colors
className="bg-primary text-primary-foreground"
```

3. **Implement proper TypeScript**:
```typescript
interface Props {
  variant?: 'default' | 'outline' | 'ghost'
  size?: 'sm' | 'default' | 'lg'
  children: React.ReactNode
}
```

#### Custom Component Patterns

**KPI Card Implementation**:
```typescript
interface KPICardProps {
  title: string
  value: string | number
  subtitle?: string
  className?: string
}

export function KPICard({ title, value, subtitle, className }: KPICardProps) {
  return (
    <div 
      className={cn("border-0 shadow-sm h-full min-h-[180px] p-6", className)}
      style={{ 
        backgroundColor: '#F8F5F4',
        aspectRatio: '1.5/1'
      }}
    >
      <div className="h-full flex flex-col justify-between">
        <div>
          <p style={{ 
            fontSize: '16px', 
            fontWeight: '500', 
            color: '#94827C',
            fontFamily: 'Poppins, system-ui, sans-serif'
          }}>
            {title}
          </p>
        </div>
        <div className="flex flex-col items-end">
          <div style={{ 
            fontSize: '48px', 
            fontWeight: '500', 
            color: '#6C6664',
            lineHeight: '1',
            fontFamily: 'Poppins, system-ui, sans-serif'
          }}>
            {value}
          </div>
          {subtitle && (
            <p style={{ 
              fontSize: '16px', 
              color: '#94827C',
              fontFamily: 'Poppins, system-ui, sans-serif'
            }}>
              {subtitle}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
```

### Best Practices

#### Styling Approach
1. **Prefer Tailwind classes** for standard styling
2. **Use inline styles** for precise color control or complex calculations
3. **Combine both approaches** for maximum flexibility
4. **Always use the `cn()` utility** for conditional classes

#### Color Usage
1. **Use CSS custom properties** for theme consistency
2. **Define custom colors** as hex values when needed
3. **Test in both light and dark modes** if supporting theme switching
4. **Document custom color choices** for maintenance

#### Component Architecture
1. **Build composable components** with single responsibilities
2. **Use TypeScript interfaces** for all prop definitions
3. **Implement proper accessibility** with ARIA labels and keyboard support
4. **Follow React forwardRef patterns** for ref passing

#### Performance Optimization
1. **Use Next.js Image component** for all images
2. **Set appropriate priority** for above-fold images
3. **Optimize SVG assets** and use appropriate dimensions
4. **Implement proper lazy loading** for data components

### Maintenance & Updates

#### Version Control
- Keep design tokens in CSS custom properties for easy updates
- Document any custom color additions in this guide
- Maintain component interfaces for backward compatibility
- Use semantic versioning for major design changes

#### Testing
- Test components in various screen sizes
- Verify accessibility compliance
- Check color contrast ratios
- Validate TypeScript compilation

#### Documentation
- Update this guide when adding new patterns
- Document any deviations from the established system
- Maintain component usage examples
- Keep asset inventories current

---

## Conclusion

This design system provides a comprehensive foundation for building consistent, scalable, and maintainable property management dashboard applications. By following these specifications and implementation guidelines, teams can create cohesive user experiences while maintaining development efficiency.

The system balances flexibility with consistency, allowing for custom implementations when needed while providing strong defaults for common use cases. Regular maintenance and documentation updates ensure the system remains valuable as applications evolve.

For questions or contributions to this design system, refer to the project documentation or contact the development team.