// Main JavaScript file
document.addEventListener('DOMContentLoaded', () => {
  console.log('Page loaded');
  
  // Add any interactive functionality here
  const links = document.querySelectorAll('nav a');
  
  links.forEach(link => {
    if (link.getAttribute('href') === window.location.pathname) {
      link.classList.add('font-bold');
    }
  });
});

// Toast/notification function with dark mode support
function showToast(message, type = 'info') {
  const isInDarkMode = document.documentElement.classList.contains('dark');
  
  const toast = document.createElement('div');
  toast.className = `fixed bottom-4 right-4 p-4 rounded-md shadow-md text-white transition-opacity duration-300 fade-in`;
  
  // Set background color based on type and theme
  if (type === 'error') {
    toast.classList.add('bg-red-500');
  } else if (type === 'success') {
    toast.classList.add('bg-green-500');
  } else { // info
    toast.classList.add(isInDarkMode ? 'bg-blue-600' : 'bg-blue-500');
  }
  
  // Add dark mode specific styles
  if (isInDarkMode) {
    toast.classList.add('shadow-lg');
  }
  
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}