// Add login/signup buttons to header
document.addEventListener('DOMContentLoaded', function() {
  // Wait for header to be available
  const header = document.querySelector('.md-header__inner');
  if (!header) return;
  
  // Check if buttons already exist
  if (document.querySelector('.auth-buttons')) return;
  
  // Create button container
  const authButtons = document.createElement('div');
  authButtons.className = 'auth-buttons';
  authButtons.style.cssText = 'display: flex; gap: 0.5rem; margin-left: auto; align-items: center;';
  
  // Create login button
  const loginBtn = document.createElement('a');
  loginBtn.href = 'https://app.truledgr.app/login';
  loginBtn.className = 'md-header__button auth-button login';
  loginBtn.textContent = 'Login';
  loginBtn.setAttribute('title', 'Login to TruLedgr');
  
  // Create signup button
  const signupBtn = document.createElement('a');
  signupBtn.href = 'https://app.truledgr.app/signup';
  signupBtn.className = 'md-header__button auth-button signup';
  signupBtn.textContent = 'Sign Up';
  signupBtn.setAttribute('title', 'Create your TruLedgr account');
  
  // Add buttons to container
  authButtons.appendChild(loginBtn);
  authButtons.appendChild(signupBtn);
  
  // Insert before the last child (usually the search button)
  const nav = header.querySelector('.md-header__option');
  if (nav && nav.parentNode) {
    nav.parentNode.insertBefore(authButtons, nav);
  } else {
    header.appendChild(authButtons);
  }
});
