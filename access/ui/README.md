# Expeta 2.0 UI

Web-based user interface for the Expeta 2.0 system, providing visualization and interaction with the semantic-driven software development platform.

## Features

- Dashboard for system overview and monitoring
- Expectation management (view, create, edit expectations)
- Code generation and visualization
- Validation results and reports
- User authentication and access control
- Responsive design for desktop and mobile devices

## Getting Started

### Prerequisites

- Node.js (v14.0.0 or higher)
- npm (v6.0.0 or higher)
- Expeta 2.0 backend running (on port 8000 by default)

### Installation

1. Clone the repository if you haven't already:
   ```
   git clone <repository-url>
   ```

2. Navigate to the UI directory:
   ```
   cd access/ui
   ```

3. Install dependencies:
   ```
   npm install
   ```

### Running the Application

Start the development server:
```
npm start
```

This will run the app in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

### Building for Production

Create a production build:
```
npm run build
```

This builds the app for production to the `build` folder. It correctly bundles React in production mode and optimizes the build for the best performance.

## Configuration

You can configure the application by setting environment variables:

- `REACT_APP_API_BASE_URL`: Backend API URL (default: `http://localhost:8000`)
- `REACT_APP_USE_MOCK_DATA`: Enable mock data for development (default: `false`)

Create a `.env` file in the project root to set these variables.

## Project Structure

```
access/ui/
├── public/               # Static files
├── src/                  # Source code
│   ├── components/       # Reusable UI components 
│   ├── context/          # React context for state management
│   ├── pages/            # Page components
│   ├── services/         # API services
│   ├── App.js            # Main application component
│   └── index.js          # Application entry point
└── package.json          # Project dependencies and scripts
```

## Contributing

1. Follow the project coding standards
2. Write tests for new features
3. Update documentation as needed

## License

This project is licensed under the terms specified in the main repository. 