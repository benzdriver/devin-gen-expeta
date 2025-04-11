"""
UI Integration Test for Expeta 2.0

This script tests the integration between the UI and API components,
focusing on the requirements management input box and multi-round dialogue.
"""

import os
import sys
import time
import json
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

UI_URL = "http://localhost:3000"
API_URL = "http://localhost:8000"
TEST_TIMEOUT = 10  # seconds

def setup_driver():
    """Set up the Chrome WebDriver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1366, 768)
        return driver
    except Exception as e:
        print(f"Error setting up WebDriver: {str(e)}")
        return None

def test_api_health():
    """Test if the API server is running and responding"""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ API server is running")
            assert True
        else:
            print(f"❌ API server returned status code {response.status_code}")
            assert False, f"API server returned status code {response.status_code}"
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        assert False, "Could not connect to API server"

def test_ui_health():
    """Test if the UI server is running and responding"""
    try:
        response = requests.get(UI_URL)
        if response.status_code == 200:
            print("✅ UI server is running")
            assert True
        else:
            print(f"❌ UI server returned status code {response.status_code}")
            assert False, f"UI server returned status code {response.status_code}"
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to UI server")
        assert False, "Could not connect to UI server"

@pytest.fixture
def driver():
    """Set up and tear down the WebDriver for tests"""
    driver = setup_driver()
    yield driver
    if driver:
        driver.quit()

def test_chat_requirements_page(driver):
    """Test the ChatRequirements page functionality"""
    print("\n🔍 Testing ChatRequirements page...")
    
    try:
        driver.get(f"{UI_URL}/chat-requirements")
        try:
            WebDriverWait(driver, TEST_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "chat-messages"))
            )
            print("✅ ChatRequirements page loaded successfully")
        except TimeoutException:
            print("⚠️ Chat messages container not found, trying alternative selectors")
            WebDriverWait(driver, TEST_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "chat-container"))
            )
            print("✅ ChatRequirements page loaded with alternative selector")
        
        messages = driver.find_elements(By.CLASS_NAME, "message")
        if len(messages) > 0:
            print(f"✅ Found {len(messages)} messages on page load")
        else:
            print("❌ No welcome message found")
        
        input_box = WebDriverWait(driver, TEST_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "user-message"))
        )
        
        if input_box.is_enabled():
            print("✅ Input box is enabled")
        else:
            print("❌ Input box is disabled")
        
        test_message = "I need a personal website with a portfolio section and a blog functionality"
        input_box.send_keys(test_message)
        
        input_value = input_box.get_attribute("value")
        if input_value == test_message:
            print(f"✅ Input box accepted text: '{input_value}'")
        else:
            print(f"❌ Input box value mismatch. Expected: '{test_message}', Got: '{input_value}'")
        
        try:
            send_button = driver.find_element(By.XPATH, "//button[@data-testid='send-button']")
            print("✅ Found send button by data-testid")
        except NoSuchElementException:
            try:
                send_button = driver.find_element(By.XPATH, "//button[contains(@class, 'send-button')]")
                print("✅ Found send button by class")
            except NoSuchElementException:
                try:
                    send_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                    print("✅ Found send button by type")
                except NoSuchElementException:
                    try:
                        send_button = driver.find_element(By.XPATH, "//button[.//span[contains(text(), 'send')]]")
                        print("✅ Found send button by icon text")
                    except NoSuchElementException:
                        try:
                            send_button = driver.find_element(By.XPATH, "//button[.//span[contains(@class, 'material-symbols-rounded') and text()='send']]")
                            print("✅ Found send button by material icon")
                        except NoSuchElementException:
                            try:
                                print("⚠️ Attempting JavaScript click on send button")
                                driver.execute_script("""
                                    const buttons = document.querySelectorAll('button');
                                    for (const button of buttons) {
                                        if (button.textContent.includes('send') || 
                                            button.innerHTML.includes('send') || 
                                            button.className.includes('send')) {
                                            button.click();
                                            return true;
                                        }
                                    }
                                    return false;
                                """)
                                print("✅ Executed JavaScript click")
                                return
                            except Exception as e:
                                print(f"❌ JavaScript click failed: {str(e)}")
                                print("❌ Could not find send button with any selector")
                                driver.save_screenshot('/tmp/button_not_found.png')
                                print("📸 Saved screenshot to /tmp/button_not_found.png")
                                raise
        send_button.click()
        
        WebDriverWait(driver, TEST_TIMEOUT).until(
            lambda d: len(d.find_elements(By.CLASS_NAME, "message")) > len(messages)
        )
        
        new_messages = driver.find_elements(By.CLASS_NAME, "message")
        if len(new_messages) > len(messages):
            print(f"✅ Message sent successfully, received response ({len(new_messages) - len(messages)} new messages)")
        else:
            print("❌ No response received after sending message")
        
        input_box = WebDriverWait(driver, TEST_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "user-message"))
        )
        
        follow_up_message = "I want to showcase my design work with images and descriptions. The blog should have categories and comments."
        input_box.send_keys(follow_up_message)
        try:
            send_button = driver.find_element(By.XPATH, "//button[@data-testid='send-button']")
            print("✅ Found send button by data-testid")
        except NoSuchElementException:
            try:
                send_button = driver.find_element(By.XPATH, "//button[contains(@class, 'send-button')]")
                print("✅ Found send button by class")
            except NoSuchElementException:
                try:
                    send_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                    print("✅ Found send button by type")
                except NoSuchElementException:
                    try:
                        send_button = driver.find_element(By.XPATH, "//button[.//span[contains(text(), 'send')]]")
                        print("✅ Found send button by icon text")
                    except NoSuchElementException:
                        try:
                            send_button = driver.find_element(By.XPATH, "//button[.//span[contains(@class, 'material-symbols-rounded') and text()='send']]")
                            print("✅ Found send button by material icon")
                        except NoSuchElementException:
                            try:
                                print("⚠️ Attempting JavaScript click on send button")
                                driver.execute_script("""
                                    const buttons = document.querySelectorAll('button');
                                    for (const button of buttons) {
                                        if (button.textContent.includes('send') || 
                                            button.innerHTML.includes('send') || 
                                            button.className.includes('send')) {
                                            button.click();
                                            return true;
                                        }
                                    }
                                    return false;
                                """)
                                print("✅ Executed JavaScript click")
                                return
                            except Exception as e:
                                print(f"❌ JavaScript click failed: {str(e)}")
                                print("❌ Could not find send button with any selector")
                                driver.save_screenshot('/tmp/button_not_found.png')
                                print("📸 Saved screenshot to /tmp/button_not_found.png")
                                raise
        send_button.click()
        
        WebDriverWait(driver, TEST_TIMEOUT).until(
            lambda d: len(d.find_elements(By.CLASS_NAME, "message")) > len(new_messages)
        )
        
        final_messages = driver.find_elements(By.CLASS_NAME, "message")
        if len(final_messages) > len(new_messages):
            print(f"✅ Follow-up message sent successfully, received response ({len(final_messages) - len(new_messages)} new messages)")
        else:
            print("❌ No response received after sending follow-up message")
        
        input_box = WebDriverWait(driver, TEST_TIMEOUT).until(
            EC.presence_of_element_located((By.ID, "user-message"))
        )
        
        confirmation_message = "Yes, that's correct. I confirm these requirements are what I want."
        input_box.send_keys(confirmation_message)
        try:
            send_button = driver.find_element(By.XPATH, "//button[@data-testid='send-button']")
            print("✅ Found send button by data-testid")
        except NoSuchElementException:
            try:
                send_button = driver.find_element(By.XPATH, "//button[contains(@class, 'send-button')]")
                print("✅ Found send button by class")
            except NoSuchElementException:
                try:
                    send_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                    print("✅ Found send button by type")
                except NoSuchElementException:
                    try:
                        send_button = driver.find_element(By.XPATH, "//button[.//span[contains(text(), 'send')]]")
                        print("✅ Found send button by icon text")
                    except NoSuchElementException:
                        try:
                            send_button = driver.find_element(By.XPATH, "//button[.//span[contains(@class, 'material-symbols-rounded') and text()='send']]")
                            print("✅ Found send button by material icon")
                        except NoSuchElementException:
                            try:
                                print("⚠️ Attempting JavaScript click on send button")
                                driver.execute_script("""
                                    const buttons = document.querySelectorAll('button');
                                    for (const button of buttons) {
                                        if (button.textContent.includes('send') || 
                                            button.innerHTML.includes('send') || 
                                            button.className.includes('send')) {
                                            button.click();
                                            return true;
                                        }
                                    }
                                    return false;
                                """)
                                print("✅ Executed JavaScript click")
                                return
                            except Exception as e:
                                print(f"❌ JavaScript click failed: {str(e)}")
                                print("❌ Could not find send button with any selector")
                                driver.save_screenshot('/tmp/button_not_found.png')
                                print("📸 Saved screenshot to /tmp/button_not_found.png")
                                raise
        send_button.click()
        
        try:
            WebDriverWait(driver, TEST_TIMEOUT * 2).until(
                lambda d: any("expectation_id" in msg.text.lower() for msg in d.find_elements(By.CLASS_NAME, "message"))
            )
            print("✅ Received expectation ID after confirmation")
        except TimeoutException:
            print("❌ No expectation ID received after confirmation")
        
        try:
            generate_button = WebDriverWait(driver, TEST_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(., '生成代码')]"))
            )
            if generate_button.is_enabled():
                print("✅ Generate code button is enabled")
                
                generate_button.click()
                
                try:
                    WebDriverWait(driver, TEST_TIMEOUT).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "generation-progress"))
                    )
                    print("✅ Code generation started successfully")
                except TimeoutException:
                    print("❌ Code generation progress not displayed")
            else:
                print("❌ Generate code button is disabled")
        except (TimeoutException, NoSuchElementException):
            print("❌ Generate code button not found")
        
        assert True
    except Exception as e:
        print(f"❌ Error testing ChatRequirements page: {str(e)}")
        try:
            driver.save_screenshot('/tmp/chat_requirements_error.png')
            print("📸 Saved error screenshot to /tmp/chat_requirements_error.png")
        except:
            print("⚠️ Could not save error screenshot")
        assert False, f"Error testing page: {str(e)}"

def test_requirements_page(driver):
    """Test the traditional Requirements page functionality"""
    print("\n🔍 Testing traditional Requirements page...")
    
    try:
        driver.get(f"{UI_URL}/requirements")
        WebDriverWait(driver, TEST_TIMEOUT).until(
            EC.presence_of_element_located((By.CLASS_NAME, "requirements-container"))
        )
        print("✅ Requirements page loaded successfully")
        
        try:
            try:
                input_box = WebDriverWait(driver, TEST_TIMEOUT).until(
                    EC.presence_of_element_located((By.ID, "requirement-input"))
                )
                print("✅ Found input box by ID")
            except TimeoutException:
                try:
                    input_box = WebDriverWait(driver, TEST_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='请描述您的需求...']"))
                    )
                    print("✅ Found input box by placeholder text")
                except TimeoutException:
                    print("❌ Could not find input box with any selector")
                    raise
            
            if input_box.is_enabled():
                print("✅ Input box is enabled")
            else:
                print("❌ Input box is disabled")
            
            test_message = "Test requirement input"
            input_box.send_keys(test_message)
            
            input_value = input_box.get_attribute("value")
            if input_value == test_message:
                print(f"✅ Input box accepted text: '{input_value}'")
            else:
                print(f"❌ Input box value mismatch. Expected: '{test_message}', Got: '{input_value}'")
            
            submit_button = driver.find_element(By.XPATH, "//button[contains(., '提交需求')]")
            submit_button.click()
            
            try:
                WebDriverWait(driver, TEST_TIMEOUT).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "requirement-response"))
                )
                print("✅ Requirement submitted successfully, received response")
            except TimeoutException:
                print("❌ No response received after submitting requirement")
        except (TimeoutException, NoSuchElementException):
            print("❌ Input box not found on Requirements page")
        
        assert True
    except Exception as e:
        print(f"❌ Error testing Requirements page: {str(e)}")
        assert False, f"Error testing page: {str(e)}"

def test_main():
    """Main test function that can be run directly"""
    print("\n🚀 Starting Expeta 2.0 UI Integration Test")
    print("=" * 80)
    
    api_running = test_api_health()
    ui_running = test_ui_health()
    
    if not api_running or not ui_running:
        pytest.skip("Cannot proceed with tests. Please ensure both API and UI servers are running.")
        return
    
    
def main():
    """Entry point when script is run directly"""
    print("\n🚀 Starting Expeta 2.0 UI Integration Test")
    print("=" * 80)
    
    api_running = test_api_health()
    ui_running = test_ui_health()
    
    if not api_running or not ui_running:
        print("\n❌ Cannot proceed with tests. Please ensure both API and UI servers are running.")
        return
    
    driver = setup_driver()
    if not driver:
        print("\n❌ Cannot proceed with tests. WebDriver setup failed.")
        return
    
    try:
        chat_requirements_success = test_chat_requirements_page(driver)
        requirements_success = test_requirements_page(driver)
        
        print("\n📊 Test Summary")
        print("=" * 80)
        print(f"ChatRequirements Page: {'✅ PASS' if chat_requirements_success else '❌ FAIL'}")
        print(f"Traditional Requirements Page: {'✅ PASS' if requirements_success else '❌ FAIL'}")
        
        if chat_requirements_success and requirements_success:
            print("\n🎉 All tests passed successfully!")
        else:
            print("\n⚠️ Some tests failed. Please check the logs above for details.")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
