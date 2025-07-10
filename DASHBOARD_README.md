# VelocityIQ Dashboard

A modern, responsive supply chain forecasting dashboard built with React and Tailwind CSS.

## ✨ New Features

### Landing Page
The dashboard now includes a beautiful landing page that introduces users to VelocityIQ and its capabilities:

- **Hero Section**: Eye-catching introduction with gradient text and call-to-action buttons
- **Feature Highlights**: Showcases key platform capabilities with icons and descriptions
- **Statistics Display**: Shows impressive platform metrics and performance indicators
- **Professional Design**: Modern UI with smooth transitions and hover effects
- **Easy Navigation**: Simple buttons to enter the dashboard or learn more

### Navigation
- Users start on the landing page when they first visit the application
- Click "Enter Dashboard" or "View Live Dashboard" to access the full analytics interface
- Use "Back to Home" button in the dashboard header to return to the landing page
- Seamless transitions between landing page and dashboard views

## Features

### Dashboard Components
- **Real-time Analytics**: Live inventory performance monitoring
- **Smart Alerts**: Instant notifications for critical events
- **Demand Forecasting**: AI-powered predictive analytics
- **Inventory Management**: Comprehensive stock level tracking
- **Interactive Charts**: Dynamic data visualizations using Recharts
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS

### Technology Stack
- **Frontend**: React 18 with functional components and hooks
- **Styling**: Tailwind CSS with custom design system
- **Icons**: Heroicons for consistent iconography
- **Charts**: Recharts for data visualization
- **State Management**: React useState and useEffect
- **API Integration**: Axios for backend communication

## Getting Started

### Prerequisites
- Node.js (version 14 or higher)
- npm or yarn package manager

### Installation

1. Navigate to the dashboard directory:
   ```bash
   cd dashboard
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open your browser and navigate to `http://localhost:3001`

### Usage Flow

1. **Landing Page**: Users are greeted with an introduction to VelocityIQ
2. **Enter Dashboard**: Click any "Enter Dashboard" button to access the analytics interface
3. **Dashboard Navigation**: Use the tab navigation to explore different sections
4. **Return Home**: Click "Back to Home" to return to the landing page

## Dashboard Sections

### Overview Tab
- Key performance metrics and statistics
- Recent alerts summary
- Forecast charts and demand trends

### Alerts Tab
- Comprehensive list of system alerts
- Categorized by severity (Critical, Warning, Info)
- Real-time status updates

### Inventory Tab
- Detailed stock status table
- Product information and availability
- Inventory level indicators

### Forecasts Tab
- Detailed forecasting charts
- Historical and predicted demand data
- Advanced analytics and insights

## Customization

### Design System
The application uses a comprehensive design system with:
- Primary colors (Blue theme)
- Success, Warning, and Danger color variants
- Purple and Indigo accent colors
- Consistent typography and spacing
- Smooth animations and transitions

### Configuration
- Auto-refresh interval: 30 seconds
- API proxy: Configured for `http://localhost:8000`
- Responsive breakpoints: Mobile, tablet, and desktop optimized

## Development

### Project Structure
```
dashboard/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── LandingPage.js      # New landing page component
│   │   ├── Header.js           # Updated with back navigation
│   │   ├── StatsOverview.js
│   │   ├── AlertsPanel.js
│   │   ├── StockStatusTable.js
│   │   ├── ForecastChart.js
│   │   ├── DemandTrends.js
│   │   └── LoadingSpinner.js
│   ├── services/
│   │   └── apiService.js
│   ├── App.js                  # Updated with landing page logic
│   ├── index.js
│   └── index.css
├── package.json
└── tailwind.config.js
```

### Key Features Added
- **LandingPage Component**: Beautiful introduction page with modern design
- **Navigation State**: Toggle between landing page and dashboard
- **Enhanced Header**: Added "Back to Home" functionality
- **Improved UX**: Smooth transitions and professional presentation
- **Extended Color Palette**: Added purple and indigo color variants

## Build and Deployment

### Production Build
```bash
npm run build
```

### Testing
```bash
npm test
```

The application is ready for production deployment with optimized builds and responsive design.

## API Integration

The dashboard expects a backend API running on `http://localhost:8000` with the following endpoints:
- `/api/overview` - Dashboard overview data
- `/api/alerts` - System alerts
- `/api/stock-status` - Inventory status
- `/api/forecasts` - Forecast data
- `/api/demand-trends` - Demand trend analysis

## Support

For technical support or questions about the dashboard implementation, please refer to the main project documentation or contact the development team. 