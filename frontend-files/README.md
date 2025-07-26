# Fineman West Concierge AI

A Next.js 14 frontend application for the AI-powered property management concierge system, designed to integrate with a FastAPI backend.

## 🚀 Project Overview

This application provides a modern dashboard interface for managing property collections, email campaigns, and tenant communications. Built with the latest web technologies and designed following the comprehensive Noodle Concierge Design System.

## 🛠 Tech Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS v3
- **Components**: shadcn/ui (built on Radix UI)
- **Icons**: Lucide React
- **Font**: Poppins (Google Fonts)

### Backend Integration
- **API**: FastAPI ready integration
- **Data Validation**: TypeScript interfaces matching Pydantic models
- **HTTP Client**: Custom API client with error handling

### Development Tools
- **Linting**: ESLint with Next.js and TypeScript rules
- **Type Checking**: TypeScript compiler
- **Package Manager**: npm

## 📁 Project Structure

```
fineman-west-concierge/
├── app/                     # Next.js 14 app router
│   ├── globals.css         # Global styles with design system
│   ├── layout.tsx          # Root layout with Poppins font
│   └── page.tsx            # Home page component
├── components/             # React components  
│   └── ui/                 # shadcn/ui base components
├── lib/                    # Utilities and configurations
│   ├── api/                # FastAPI integration
│   │   ├── client.ts       # HTTP client
│   │   └── services.ts     # API services with mock data
│   └── utils.ts            # Utility functions
├── public/                 # Static assets
│   ├── logo.svg            # Fineman Concierge logo
│   ├── home-icon.svg       # Navigation icons
│   └── active-collections-icon.svg
├── types/                  # TypeScript type definitions
│   └── index.ts            # API and data types
└── tailwind.config.ts      # Tailwind with design system colors
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm

### Installation

1. **Navigate to project directory**:
   ```bash
   cd fineman-west-concierge
   ```

2. **Install dependencies** (already installed):
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```

4. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production  
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npx tsc --noEmit` - Check TypeScript types

## 🔌 FastAPI Integration

The application is pre-configured to integrate with a FastAPI backend:

### API Client Features
- **HTTP Client**: Custom client with error handling
- **Type Safety**: TypeScript interfaces for all API responses
- **Environment Config**: Configurable API base URL (.env.local)
- **Error Handling**: Structured error responses

### Mock Data Available
Development includes comprehensive mock data matching the design:
- Collection metrics (10 successful collections, 9 campaigns, 28 communications)
- Escalation queue (Hudson Jeans - $43,250 example)
- Recent email activity with company data
- Receivables and activity summaries

## ✅ Completed Setup

All foundational elements are ready:

- [x] **Next.js 14** with TypeScript and App Router
- [x] **Tailwind CSS v3** with complete design system colors
- [x] **shadcn/ui components** (Button, Card, Input, Badge, Tabs)
- [x] **Poppins font** configuration and typography system
- [x] **Lucide React** icons and UI dependencies
- [x] **FastAPI integration** structure with TypeScript types
- [x] **Asset management** with properly named SVG files
- [x] **ESLint & TypeScript** development environment

## 🎯 Ready for Implementation

The following components are ready to be built using the provided design mockup:

### Dashboard Interface
- Header navigation with logo and tabs
- KPI metrics cards with color-coded backgrounds:
  - Successful Collections (mint green)
  - Active Email Campaigns (orange)  
  - Email Escalation Queue (pink)
  - Total Email Communications (purple)

### Interactive Features
- Email escalation queue management
- File upload functionality
- Recent activity tracking
- Navigation between Home and Active Collections

## 🎨 Design System Integration

The project implements the complete Noodle Concierge Design System:

- **Colors**: HSL-based system with CSS custom properties
- **Typography**: Poppins font with defined scales
- **Components**: Accessible UI components
- **Layout**: Responsive grids and spacing
- **Assets**: Optimized SVG icons and logos

## 📝 Next Steps

1. **Build Dashboard Components**: Implement the home page interface
2. **Add Navigation Logic**: Create routing between sections  
3. **Implement KPI Cards**: Build metric displays with proper colors
4. **Connect Mock Data**: Use provided API services for development
5. **Add Interactivity**: Implement button actions and state management

## 🔧 Development Guidelines

- Use TypeScript for all components
- Follow ESLint rules and design system specifications  
- Implement proper error handling and loading states
- Test responsive behavior across screen sizes
- Maintain accessibility compliance (WCAG)

The foundation is complete and ready for building the dashboard interface according to the provided design mockup.
