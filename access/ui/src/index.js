import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './styles.css';
import './token-styles.css';
import { setupInputFix } from './utils/InputFix';

setupInputFix();

window.debugInputs = () => {
  console.log('[InputDebug] Checking all input elements on page');
  const inputs = document.querySelectorAll('input, textarea');
  console.log(`[InputDebug] Found ${inputs.length} input elements`);
  
  inputs.forEach((input, index) => {
    console.log(`[InputDebug] Input ${index + 1}: ${input.tagName}#${input.id || 'unknown'}, value="${input.value}"`);
  });
  
  return inputs.length;
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
