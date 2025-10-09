// Add login/signup buttons to header
(function() {
  'use strict';
  
  function addAuthButtons() {
    // Check if buttons already exist
    if (document.querySelector('.auth-button')) {
      console.log('Auth buttons already exist');
      return;
    }
    
    // Find the header toolbar
    const toolbar = document.querySelector('.md-header__inner.md-grid');
    if (!toolbar) {
      console.log('Toolbar not found');
      return;
    }
    
    // Find the source/repository link or create a container
    const sourceLink = toolbar.querySelector('.md-header__source');
    const targetElement = sourceLink || toolbar.lastElementChild;
    
    if (!targetElement) {
      console.log('No target element found');
      return;
    }
    
    // Create login button
    const loginBtn = document.createElement('a');
    loginBtn.href = 'https://dash.truledgr.app/login';
    loginBtn.className = 'md-header__button md-icon auth-button login';
    loginBtn.textContent = 'Login';
    loginBtn.setAttribute('title', 'Login to TruLedgr');
    
    // Create signup button
    const signupBtn = document.createElement('a');
    signupBtn.href = 'https://dash.truledgr.app/signup';
    signupBtn.className = 'md-header__button md-icon auth-button signup';
    signupBtn.textContent = 'Sign Up';
    signupBtn.setAttribute('title', 'Create your TruLedgr account');
    
    // Insert buttons before the target
    targetElement.parentNode.insertBefore(loginBtn, targetElement);
    targetElement.parentNode.insertBefore(signupBtn, targetElement);
    
    console.log('Auth buttons added successfully!');
  }
  
  // Wait for DOM and try to add buttons
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      setTimeout(addAuthButtons, 100);
    });
  } else {
    setTimeout(addAuthButtons, 100);
  }
  
  // For Material theme's instant navigation
  document$.subscribe(function() {
    setTimeout(addAuthButtons, 100);
  });
  
})();
