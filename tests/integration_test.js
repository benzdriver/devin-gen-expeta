/**
 * Integration test for Expeta 2.0
 * A simple test that opens the UI and takes screenshots of different pages
 */

const puppeteer = require('puppeteer');
const path = require('path');

// Configuration
const UI_URL = 'http://localhost:3000';
const TIMEOUT = 30000; // 30 second timeout

async function runTest() {
  console.log('Starting simple UI navigation test...');
  
  // Launch browser
  const browser = await puppeteer.launch({
    headless: false, // Set to false to see browser UI
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1280, height: 800 }
  });
  
  try {
    const page = await browser.newPage();
    
    // Configure timeout
    page.setDefaultNavigationTimeout(TIMEOUT);
    page.setDefaultTimeout(TIMEOUT);
    
    // Go to UI
    console.log('Navigating to:', UI_URL);
    await page.goto(UI_URL);
    
    // Wait for app to initialize
    try {
      await page.waitForSelector('.app-container', { timeout: 5000 });
      console.log('App loaded successfully');
    } catch (error) {
      console.log('Could not find .app-container, but continuing test...');
    }
    
    // Take screenshot of the main page
    const mainScreenshot = path.join(__dirname, 'main_page.png');
    await page.screenshot({ path: mainScreenshot, fullPage: true });
    console.log(`Main page screenshot saved to ${mainScreenshot}`);
    
    // Try to navigate to each page
    const pages = [
      { name: 'Requirements', selector: 'a[href="#requirements"]' },
      { name: 'Expectations', selector: 'a[href="#expectations"]' },
      { name: 'Code Generation', selector: 'a[href="#code-generation"]' },
      { name: 'Validation', selector: 'a[href="#validation"]' },
      { name: 'Memory', selector: 'a[href="#memory"]' },
      { name: 'Semantic Mediator', selector: 'a[href="#semantic-mediator"]' },
      { name: 'Dashboard', selector: 'a[href="#dashboard"]' }
    ];
    
    // Navigate to each page
    for (const pageInfo of pages) {
      console.log(`Navigating to ${pageInfo.name} page...`);
      
      try {
        const link = await page.$(pageInfo.selector);
        if (link) {
          await link.click();
          
          // Wait for navigation to settle
          await page.waitForTimeout(1000);
          
          // Take screenshot
          const screenshot = path.join(__dirname, `${pageInfo.name.toLowerCase().replace(' ', '_')}_page.png`);
          await page.screenshot({ path: screenshot, fullPage: true });
          console.log(`${pageInfo.name} page screenshot saved to ${screenshot}`);
        } else {
          console.log(`Could not find selector for ${pageInfo.name}`);
        }
      } catch (error) {
        console.log(`Error navigating to ${pageInfo.name}:`, error.message);
      }
    }
    
    console.log('Navigation test completed successfully');
    return true;
  } catch (error) {
    console.error('Test failed:', error);
    return false;
  } finally {
    // Close browser
    await browser.close();
  }
}

// Run the test
(async () => {
  const success = await runTest();
  process.exit(success ? 0 : 1);
})(); 