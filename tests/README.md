# Expeta 2.0 Integration Tests

This directory contains simple UI navigation tests for Expeta 2.0 that capture screenshots of each page to verify the UI is working correctly.

## Prerequisites

- Node.js and npm installed
- The Expeta 2.0 UI running on http://localhost:3000

## Setup

Install the testing dependencies:

```bash
cd tests
npm install
```

## Running Tests

Make sure the Expeta 2.0 UI is running at http://localhost:3000 first. You can start it with:

```bash
cd access/ui
npm start
```

Then, to run the navigation tests, use the following command from the tests directory:

```bash
npm test
```

This will:
1. Launch a Puppeteer browser
2. Navigate to each page in the UI
3. Take screenshots of each page
4. Store the screenshots in the tests directory

## Screenshots

The test will generate screenshots for each page:

- `main_page.png` - The initial loading page
- `requirements_page.png` - Requirements page
- `expectations_page.png` - Expectations page
- `code_generation_page.png` - Code Generation page
- `validation_page.png` - Validation page
- `memory_page.png` - Memory page
- `semantic_mediator_page.png` - Semantic Mediator page
- `dashboard_page.png` - Dashboard page

These screenshots can be used to verify that the UI is rendering correctly. 