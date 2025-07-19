// Main application initialization
console.log('Family Platform - Loading...');

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Family Platform - Initialized');
    
    // Initialize smooth scrolling for anchor links
    initSmoothScrolling();
    
    // Initialize mobile menu toggle
    initMobileMenu();
    
    // Initialize newsletter form
    initNewsletterForm();
});

function initSmoothScrolling() {
    // Handle smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function initMobileMenu() {
    const toggle = document.querySelector('.mobile-menu-toggle');
    const menu = document.querySelector('.nav-menu');
    
    if (toggle && menu) {
        toggle.addEventListener('click', () => {
            menu.classList.toggle('active');
            toggle.classList.toggle('active');
        });
    }
}

function initNewsletterForm() {
    const form = document.querySelector('.newsletter-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = form.querySelector('input[type="email"]').value;
            const button = form.querySelector('button');
            const originalText = button.textContent;
            
            // Simple validation
            if (!email || !email.includes('@')) {
                alert('Please enter a valid email address');
                return;
            }
            
            // Update button state
            button.textContent = 'Subscribing...';
            button.disabled = true;
            
            try {
                // Simulate API call (replace with actual endpoint)
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                alert('Thank you for subscribing! We\'ll keep you updated on our progress.');
                form.reset();
            } catch (error) {
                alert('Subscription failed. Please try again later.');
            } finally {
                button.textContent = originalText;
                button.disabled = false;
            }
        });
    }
}