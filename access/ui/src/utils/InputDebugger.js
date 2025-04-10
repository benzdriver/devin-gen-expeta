/**
 * InputDebugger utility to help diagnose and fix input element issues
 */

export const setupInputDebugger = () => {
  console.log('[InputDebugger] Setting up input debugger utility');
  
  document.addEventListener('input', function(e) {
    const target = e.target;
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
      console.log(`[InputDebugger] Input event on ${target.tagName}#${target.id || 'unknown'}: "${e.target.value}"`);
    }
  }, true);
  
  document.addEventListener('submit', function(e) {
    console.log(`[InputDebugger] Form submission detected: ${e.target.id || 'unknown form'}`);
  }, true);
  
  document.addEventListener('click', function(e) {
    if (e.target.tagName === 'BUTTON' || 
        (e.target.tagName === 'SPAN' && e.target.parentElement.tagName === 'BUTTON')) {
      const button = e.target.tagName === 'BUTTON' ? e.target : e.target.parentElement;
      console.log(`[InputDebugger] Button click detected: ${button.textContent.trim() || 'unknown button'}`);
    }
  }, true);
  
  const originalFetch = window.fetch;
  window.fetch = function(url, options) {
    console.log(`[InputDebugger] Fetch API call to: ${url}`);
    if (options && options.body) {
      try {
        console.log(`[InputDebugger] Request body: ${options.body}`);
      } catch (e) {
        console.log(`[InputDebugger] Could not log request body: ${e.message}`);
      }
    }
    return originalFetch.apply(this, arguments)
      .then(response => {
        console.log(`[InputDebugger] Fetch response status: ${response.status}`);
        return response;
      })
      .catch(error => {
        console.error(`[InputDebugger] Fetch error: ${error.message}`);
        throw error;
      });
  };
  
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'childList' && mutation.addedNodes.length) {
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === 1) { // Element node
            const inputs = node.querySelectorAll('input, textarea');
            if (inputs.length) {
              console.log(`[InputDebugger] New input elements added to DOM: ${inputs.length}`);
              inputs.forEach(input => {
                console.log(`[InputDebugger] New input: ${input.tagName}#${input.id || 'unknown'}`);
              });
            }
          }
        });
      }
    });
  });
  
  observer.observe(document.body, { childList: true, subtree: true });
  
  console.log('[InputDebugger] Setup complete');
  
  return function checkAllInputs() {
    const inputs = document.querySelectorAll('input, textarea');
    console.log(`[InputDebugger] Found ${inputs.length} input elements on the page`);
    
    inputs.forEach((input, index) => {
      console.log(`[InputDebugger] Input ${index + 1}: ${input.tagName}#${input.id || 'unknown'}, type=${input.type}, value="${input.value}"`);
      
      const originalValue = input.value;
      input.value = `test-${Date.now()}`;
      input.dispatchEvent(new Event('input', { bubbles: true }));
      console.log(`[InputDebugger] Set test value: "${input.value}"`);
      
      setTimeout(() => {
        input.value = originalValue;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        console.log(`[InputDebugger] Restored original value: "${input.value}"`);
      }, 100);
    });
    
    return inputs.length;
  };
};

export default setupInputDebugger;
