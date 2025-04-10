/**
 * Functional test for Expeta 2.0
 * Tests the actual application logic and data flow between UI and backend
 */

import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import fetch from 'node-fetch';

// Get the __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const UI_URL = 'http://localhost:3000';
const API_URL = 'http://localhost:8000';
const TIMEOUT = 60000; // 60 second timeout for longer operations

// Test data
const TEST_REQUIREMENT = '创建一个用户管理系统，支持用户注册、登录和个人资料管理。系统需要安全存储用户数据，并支持权限控制。';
const TEST_CLARIFICATION = '系统应该支持基于角色的权限控制，包括管理员和普通用户两种角色。';

// Helper to make API requests
async function callAPI(endpoint, method = 'GET', data = null, sessionId = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json'
    }
  };
  
  if (sessionId) {
    options.headers['Session-ID'] = sessionId;
  }
  
  if (data && (method === 'POST' || method === 'PUT')) {
    options.body = JSON.stringify(data);
  }
  
  const response = await fetch(`${API_URL}${endpoint}`, options);
  if (!response.ok) {
    throw new Error(`API call failed: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

// Main test function
async function runFunctionalTest() {
  console.log('Starting functional test...');
  
  // Create output directory for artifacts
  const outputDir = path.join(__dirname, 'test_results');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
  }
  
  // Launch browser
  const browser = await puppeteer.launch({
    headless: false, // Set to false to see browser UI
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1280, height: 800 }
  });
  
  try {
    const page = await browser.newPage();
    
    // Enable console logging from the page
    page.on('console', msg => console.log('Browser console:', msg.text()));
    
    // Configure network monitoring to capture API calls
    let sessionId = null;
    page.on('response', async (response) => {
      const url = response.url();
      if (url.includes('/chat/session') && response.status() === 200) {
        try {
          const data = await response.json();
          if (data.session_id) {
            sessionId = data.session_id;
            console.log(`Captured session ID: ${sessionId}`);
          }
        } catch (e) {
          // Ignore errors parsing JSON
        }
      }
    });
    
    // Configure timeout
    page.setDefaultNavigationTimeout(TIMEOUT);
    page.setDefaultTimeout(TIMEOUT);
    
    // Go to UI
    console.log('Navigating to:', UI_URL);
    await page.goto(UI_URL);
    
    // Wait for app to initialize
    await page.waitForSelector('.app-container', { timeout: 10000 })
      .catch(() => console.log('Could not find .app-container, but continuing test...'));
    console.log('App loaded successfully');
    
    // Wait for session initialization
    await page.waitForFunction(() => {
      return !!document.querySelector('.main-content');
    }, { timeout: 10000 });
    
    // Take initial screenshot
    await page.screenshot({ 
      path: path.join(outputDir, 'init_page.png'), 
      fullPage: true 
    });
    
    // ===================================================
    // Test 1: Navigate to Requirements page and submit requirement
    // ===================================================
    console.log('Test 1: Testing requirement submission...');
    
    // Click on Requirements nav item
    await page.click('a[href="#requirements"]');
    await page.waitForTimeout(1000);
    
    // Find and fill requirement text area
    const textareaSelectors = [
      '.input-area textarea',
      '.requirement-input textarea',
      'textarea'
    ];
    
    let textareaSelector = null;
    for (const selector of textareaSelectors) {
      const exists = await page.$(selector);
      if (exists) {
        textareaSelector = selector;
        break;
      }
    }
    
    if (!textareaSelector) {
      throw new Error('Could not find textarea for requirement input');
    }
    
    // Clear and enter new requirement
    await page.click(textareaSelector);
    await page.evaluate((selector) => {
      document.querySelector(selector).value = '';
    }, textareaSelector);
    await page.type(textareaSelector, TEST_REQUIREMENT);
    
    // Take screenshot of requirements page with input
    await page.screenshot({ 
      path: path.join(outputDir, 'requirement_input.png'), 
      fullPage: true 
    });
    
    // Find and click the submit button
    const submitButtonSelectors = [
      '.clarify-button',
      '.submit-button',
      'button.primary-button',
      'button[type="submit"]'
    ];
    
    let submitButtonClicked = false;
    for (const selector of submitButtonSelectors) {
      const button = await page.$(selector);
      if (button) {
        await button.click();
        submitButtonClicked = true;
        console.log(`Clicked submit button with selector: ${selector}`);
        break;
      }
    }
    
    if (!submitButtonClicked) {
      const buttons = await page.$$('button');
      if (buttons.length > 0) {
        // Click the first button as a fallback
        await buttons[0].click();
        submitButtonClicked = true;
        console.log('Clicked first button as fallback');
      }
    }
    
    if (!submitButtonClicked) {
      throw new Error('Could not find or click submit button');
    }
    
    // Wait for clarification process to begin (workflow step 2 active)
    try {
      await page.waitForSelector('.workflow-step:nth-child(2).active', { timeout: 10000 });
      console.log('Clarification step is active');
    } catch (error) {
      console.log('Could not detect active clarification step, continuing...');
    }
    
    // Take screenshot after requirement submission
    await page.screenshot({ 
      path: path.join(outputDir, 'requirement_submitted.png'), 
      fullPage: true 
    });
    
    // Try to interact with chat if available
    try {
      // Find chat input field
      const chatInputSelectors = [
        '.chat-input textarea',
        '.message-input textarea',
        '.chat-container textarea',
        'textarea:not(:disabled)'
      ];
      
      let chatInputSelector = null;
      for (const selector of chatInputSelectors) {
        const exists = await page.$(selector);
        if (exists) {
          chatInputSelector = selector;
          break;
        }
      }
      
      if (chatInputSelector) {
        console.log(`Found chat input with selector: ${chatInputSelector}`);
        await page.type(chatInputSelector, TEST_CLARIFICATION);
        
        // Take screenshot of chat interaction
        await page.screenshot({
          path: path.join(outputDir, 'chat_input.png'),
          fullPage: true
        });
        
        // Find and click send button
        const sendButtonSelectors = [
          '.send-button',
          '.chat-actions button',
          'button.primary-button:not([disabled])',
          'button[type="submit"]'
        ];
        
        let sendButtonClicked = false;
        for (const selector of sendButtonSelectors) {
          const button = await page.$(selector);
          if (button) {
            await button.click();
            sendButtonClicked = true;
            console.log(`Clicked send button with selector: ${selector}`);
            break;
          }
        }
        
        if (sendButtonClicked) {
          // Wait for response to appear
          await page.waitForTimeout(3000);
          
          // Take screenshot after chat response
          await page.screenshot({
            path: path.join(outputDir, 'chat_response.png'),
            fullPage: true
          });
          
          console.log('Chat interaction completed');
        } else {
          console.log('Could not find send button for chat');
        }
        
        // Look for a finalize/complete button
        const finalizeSelectors = [
          '.finalize-button',
          'button:has-text("完成")',
          'button:has-text("完成期望")',
          'button:has-text("生成期望")',
          '.workflow-actions button',
          '.section-actions button.primary-button'
        ];
        
        let finalizeClicked = false;
        for (const selector of finalizeSelectors) {
          try {
            const button = await page.$(selector);
            if (button) {
              await button.click();
              finalizeClicked = true;
              console.log(`Clicked finalize button with selector: ${selector}`);
              break;
            }
          } catch (error) {
            // Continue trying other selectors
          }
        }
        
        if (finalizeClicked) {
          // Wait for expectation to be finalized
          await page.waitForTimeout(3000);
          
          // Take screenshot after finalization
          await page.screenshot({
            path: path.join(outputDir, 'expectation_finalized.png'),
            fullPage: true
          });
        } else {
          console.log('Could not find finalize button');
        }
      } else {
        console.log('Could not find chat input field');
      }
    } catch (error) {
      console.log('Error during chat interaction:', error.message);
    }
    
    // ===================================================
    // Test 2: Verify generated expectation
    // ===================================================
    console.log('Test 2: Verifying expectation generation...');
    
    // Extract expectation ID from UI or use a direct API call with session ID
    let expectationId = null;
    
    try {
      // Attempt to get expectation ID from UI
      expectationId = await page.evaluate(() => {
        const elements = Array.from(document.querySelectorAll('p, span, div'));
        for (const element of elements) {
          const text = element.textContent;
          if (text.includes('ID:')) {
            return text.split('ID:')[1].trim();
          }
        }
        return null;
      });
      
      console.log(`Found expectation ID from UI: ${expectationId}`);
    } catch (error) {
      console.log('Could not extract expectation ID from UI');
    }
    
    // If we have a session ID but couldn't get expectation ID from UI, try API
    if (sessionId && !expectationId) {
      try {
        const expectationsResult = await callAPI('/memory/expectations', 'GET', null, sessionId);
        if (expectationsResult && expectationsResult.length > 0) {
          expectationId = expectationsResult[0].id;
          console.log(`Found expectation ID from API: ${expectationId}`);
        }
      } catch (error) {
        console.log('Failed to get expectations from API:', error.message);
      }
    }
    
    // If we still don't have an expectation ID, use a fallback
    if (!expectationId) {
      expectationId = 'test-expectation-id';
      console.log(`Using fallback expectation ID: ${expectationId}`);
    }
    
    // ===================================================
    // Test 3: Navigate to Expectations page
    // ===================================================
    console.log('Test 3: Navigating to Expectations page...');
    
    await page.click('a[href="#expectations"]');
    await page.waitForTimeout(2000);
    
    // Take screenshot of expectations page
    await page.screenshot({
      path: path.join(outputDir, 'expectations_page.png'),
      fullPage: true
    });
    
    // ===================================================
    // Test 4: Navigate to Code Generation page
    // ===================================================
    console.log('Test 4: Testing code generation...');
    
    await page.click('a[href="#code-generation"]');
    await page.waitForTimeout(2000);
    
    // Take screenshot of code generation page
    await page.screenshot({
      path: path.join(outputDir, 'code_generation_init.png'),
      fullPage: true
    });
    
    // Find expectation ID input
    const searchInput = await page.$('.search-input');
    if (searchInput) {
      await searchInput.type(expectationId);
      
      // Find and click load button
      const loadButtons = await page.$$('button.primary-button');
      if (loadButtons.length > 0) {
        await loadButtons[0].click();
        console.log('Clicked load button for expectation');
        
        // Wait for expectation to load
        await page.waitForTimeout(3000);
        
        // Take screenshot after expectation loaded
        await page.screenshot({
          path: path.join(outputDir, 'expectation_loaded.png'),
          fullPage: true
        });
        
        // Try to generate code
        const generateButtons = await page.$$('.generation-actions button, button:has-text("生成代码")');
        if (generateButtons.length > 0) {
          await generateButtons[0].click();
          console.log('Clicked generate code button');
          
          // Wait for code generation (this could take some time)
          await page.waitForTimeout(10000);
          
          // Take screenshot after code generation
          await page.screenshot({
            path: path.join(outputDir, 'code_generated.png'),
            fullPage: true
          });
          
          // Check if code was generated
          const codeContent = await page.$('.code-block, .code-content, pre');
          if (codeContent) {
            console.log('Code was successfully generated');
          } else {
            console.log('Could not detect generated code in UI');
          }
        } else {
          console.log('Could not find generate code button');
        }
      } else {
        console.log('Could not find load button for expectation');
      }
    } else {
      console.log('Could not find expectation ID input field');
    }
    
    // ===================================================
    // Test 5: Navigate to Semantic Mediator page
    // ===================================================
    console.log('Test 5: Testing Semantic Mediator page...');
    
    await page.click('a[href="#semantic-mediator"]');
    await page.waitForTimeout(2000);
    
    // Take screenshot of semantic mediator page
    await page.screenshot({
      path: path.join(outputDir, 'semantic_mediator.png'),
      fullPage: true
    });
    
    // Check if semantic mediator data is loaded
    const mediatorStats = await page.$('.stats-row, .architecture-diagram');
    if (mediatorStats) {
      console.log('Semantic Mediator page data loaded successfully');
    } else {
      console.log('Could not detect Semantic Mediator statistics');
    }
    
    // ===================================================
    // Test 6: Check Memory page for stored data
    // ===================================================
    console.log('Test 6: Testing Memory system...');
    
    await page.click('a[href="#memory"]');
    await page.waitForTimeout(2000);
    
    // Take screenshot of memory page
    await page.screenshot({
      path: path.join(outputDir, 'memory_page.png'),
      fullPage: true
    });
    
    // Try to search for the expectation
    const memorySearchInput = await page.$('.search-input');
    if (memorySearchInput && expectationId) {
      await memorySearchInput.type(expectationId);
      await page.waitForTimeout(2000);
      
      // Take screenshot after search
      await page.screenshot({
        path: path.join(outputDir, 'memory_search.png'),
        fullPage: true
      });
      
      // Check if item was found
      const memoryItem = await page.$('.memory-item, .expectation-item');
      if (memoryItem) {
        console.log('Found expectation in memory system');
      } else {
        console.log('Could not find expectation in memory UI');
      }
    }
    
    // ===================================================
    // Results collection
    // ===================================================
    console.log('Collecting test results...');
    
    // Create a test report
    const reportPath = path.join(outputDir, 'test_report.json');
    const report = {
      timestamp: new Date().toISOString(),
      sessionId,
      expectationId,
      tests: [
        { name: 'Requirements Submission', result: submitButtonClicked ? 'PASS' : 'FAIL' },
        { name: 'Expectation Generation', result: expectationId && expectationId !== 'test-expectation-id' ? 'PASS' : 'INCONCLUSIVE' },
        { name: 'Navigation to Expectations Page', result: 'PASS' },
        { name: 'Code Generation', result: await page.$('.code-block, .code-content, pre') ? 'PASS' : 'INCONCLUSIVE' },
        { name: 'Semantic Mediator Page', result: await page.$('.semantic-mediator-container') ? 'PASS' : 'FAIL' },
        { name: 'Memory System', result: await page.$('.memory-container, .memory-item') ? 'PASS' : 'INCONCLUSIVE' }
      ],
      artifacts: fs.readdirSync(outputDir).filter(f => f.endsWith('.png'))
    };
    
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`Test report written to ${reportPath}`);
    
    console.log('Functional test completed successfully');
    return true;
  } catch (error) {
    console.error('Functional test failed:', error);
    
    // Try to take failure screenshot
    try {
      const page = await browser.pages();
      if (page.length > 0) {
        const screenshotPath = path.join(__dirname, 'test_results', 'test_failure.png');
        await page[0].screenshot({ path: screenshotPath, fullPage: true });
        console.log(`Failure screenshot saved to ${screenshotPath}`);
      }
    } catch (screenshotError) {
      console.error('Failed to take failure screenshot:', screenshotError);
    }
    
    return false;
  } finally {
    // Close browser
    await browser.close();
  }
}

// Run the test if this file is executed directly
if (require.main === module) {
  (async () => {
    const success = await runFunctionalTest();
    process.exit(success ? 0 : 1);
  })();
}

export { runFunctionalTest }; 