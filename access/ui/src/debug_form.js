console.log('Debug form script loaded');

document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, setting up form tracking');
  
  document.addEventListener('submit', function(e) {
    console.log('Form submission detected:', e);
    console.log('Form target:', e.target);
    console.log('Form action:', e.target.action);
    console.log('Form method:', e.target.method);
    
    e.preventDefault();
    e.stopPropagation();
    console.log('Default form submission prevented');
    
    return false;
  }, true);
  
  document.addEventListener('click', function(e) {
    console.log('Click detected on:', e.target);
    console.log('Target tag:', e.target.tagName);
    console.log('Target id:', e.target.id);
    console.log('Target class:', e.target.className);
  }, true);
  
  document.addEventListener('keydown', function(e) {
    console.log('Keydown detected:', e.key);
    console.log('Target:', e.target);
    
    if (e.key === 'Enter' && !e.shiftKey) {
      console.log('Enter key detected, checking if in form');
      
      let element = e.target;
      while (element && element.tagName !== 'FORM') {
        element = element.parentElement;
      }
      
      if (element) {
        console.log('Enter key in form, preventing default');
        e.preventDefault();
        e.stopPropagation();
      }
    }
  }, true);
  
  window.addEventListener('beforeunload', function(e) {
    console.log('Navigation detected');
    console.log('Current URL:', window.location.href);
    console.log('Referrer:', document.referrer);
    
    const logData = {
      timestamp: new Date().toISOString(),
      url: window.location.href,
      referrer: document.referrer
    };
    
    console.log('Navigation log:', JSON.stringify(logData));
    
  });
  
  const originalSubmit = HTMLFormElement.prototype.submit;
  HTMLFormElement.prototype.submit = function() {
    console.log('Form submit method called directly');
    console.log('Form:', this);
    console.log('Form action:', this.action);
    
    
    return originalSubmit.apply(this, arguments);
  };
  
  console.log('Form tracking setup complete');
});
