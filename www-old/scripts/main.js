// TruLedgr Marketing Website JavaScript

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeAnimations();
    initializeScrollEffects();
    initializeCounters();
    initializeForms();
});

// Navigation functionality
function initializeNavigation() {
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const navbar = document.querySelector('.navbar');
    const navLinks = document.querySelectorAll('.nav-link');

    // Mobile menu toggle
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
            document.body.classList.toggle('nav-open');
        });

        // Close menu when clicking on links
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
                document.body.classList.remove('nav-open');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navbar.contains(e.target) && navMenu.classList.contains('active')) {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
                document.body.classList.remove('nav-open');
            }
        });
    }

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 70;
                const elementPosition = target.offsetTop;
                const offsetPosition = elementPosition - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Animation functionality
function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                
                // Trigger counter animation if element has data-counter
                if (entry.target.dataset.counter) {
                    animateCounter(entry.target);
                }
            }
        });
    }, observerOptions);

    // Observe elements with animation classes
    document.querySelectorAll('.feature-card, .platform-card, .pricing-card, .testimonial-card, .stat').forEach(el => {
        observer.observe(el);
    });
}

// Scroll effects
function initializeScrollEffects() {
    let lastScrollTop = 0;
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Auto-hide navbar on scroll down (on mobile)
        if (window.innerWidth <= 768) {
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                navbar.style.transform = 'translateY(-100%)';
            } else {
                navbar.style.transform = 'translateY(0)';
            }
        }
        
        lastScrollTop = scrollTop;
    });

    // Parallax effect for hero background
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            hero.style.transform = `translateY(${rate}px)`;
        });
    }
}

// Counter animation
function initializeCounters() {
    // This will be triggered by the intersection observer
}

function animateCounter(element) {
    const target = parseInt(element.dataset.counter);
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;

    const counter = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(counter);
        }
        
        // Format number with commas if needed
        const formatted = target >= 1000 ? 
            Math.floor(current).toLocaleString() : 
            Math.floor(current);
            
        element.textContent = formatted + (element.dataset.suffix || '');
    }, 16);
}

// Form functionality
function initializeForms() {
    // Newsletter signup form
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', handleNewsletterSignup);
    }

    // Contact form
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactForm);
    }
}

function handleNewsletterSignup(e) {
    e.preventDefault();
    const email = e.target.querySelector('input[type="email"]').value;
    
    // Show loading state
    const button = e.target.querySelector('button');
    const originalText = button.textContent;
    button.textContent = 'Signing up...';
    button.disabled = true;

    // Simulate API call (replace with actual endpoint)
    setTimeout(() => {
        button.textContent = 'Subscribed!';
        button.classList.add('success');
        
        setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
            button.classList.remove('success');
            e.target.reset();
        }, 2000);
    }, 1000);
}

function handleContactForm(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    // Show loading state
    const button = e.target.querySelector('button[type="submit"]');
    const originalText = button.textContent;
    button.textContent = 'Sending...';
    button.disabled = true;

    // Simulate API call (replace with actual endpoint)
    setTimeout(() => {
        button.textContent = 'Message Sent!';
        button.classList.add('success');
        
        setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
            button.classList.remove('success');
            e.target.reset();
        }, 2000);
    }, 1000);
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Performance optimizations
const debouncedResize = debounce(() => {
    // Handle resize events
    window.dispatchEvent(new Event('resize-complete'));
}, 250);

window.addEventListener('resize', debouncedResize);

// Loading state management
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
    
    // Initialize any components that need the page to be fully loaded
    initializeCarousels();
    initializeLazyLoading();
});

// Carousel functionality (if needed for testimonials or features)
function initializeCarousels() {
    const carousels = document.querySelectorAll('.carousel');
    
    carousels.forEach(carousel => {
        let currentSlide = 0;
        const slides = carousel.querySelectorAll('.carousel-slide');
        const totalSlides = slides.length;
        
        if (totalSlides <= 1) return;
        
        // Auto-advance carousel
        setInterval(() => {
            currentSlide = (currentSlide + 1) % totalSlides;
            carousel.style.transform = `translateX(-${currentSlide * 100}%)`;
        }, 5000);
    });
}

// Lazy loading for images
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers without IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
            img.classList.remove('lazy');
        });
    }
}

// Cookie consent (if needed)
function initializeCookieConsent() {
    const cookieConsent = document.querySelector('.cookie-consent');
    const acceptButton = document.querySelector('.cookie-accept');
    
    if (cookieConsent && acceptButton) {
        // Check if user has already consented
        if (localStorage.getItem('cookieConsent') !== 'true') {
            setTimeout(() => {
                cookieConsent.classList.add('show');
            }, 2000);
        }
        
        acceptButton.addEventListener('click', () => {
            localStorage.setItem('cookieConsent', 'true');
            cookieConsent.classList.remove('show');
        });
    }
}

// Analytics tracking (placeholder functions)
function trackEvent(event, category, label) {
    // Replace with actual analytics code
    console.log('Track Event:', { event, category, label });
}

function trackPageView() {
    // Replace with actual analytics code
    console.log('Track Page View:', window.location.pathname);
}

// Initialize analytics on load
trackPageView();

// Add event listeners for tracking
document.addEventListener('click', (e) => {
    // Track CTA button clicks
    if (e.target.matches('.btn-primary')) {
        trackEvent('click', 'cta', e.target.textContent.trim());
    }
    
    // Track navigation clicks
    if (e.target.matches('.nav-link')) {
        trackEvent('click', 'navigation', e.target.textContent.trim());
    }
    
    // Track platform links
    if (e.target.matches('.platform-link')) {
        trackEvent('click', 'platform', e.target.textContent.trim());
    }
});

// Export functions for external use
window.TruLedgr = {
    trackEvent,
    trackPageView,
    animateCounter
};
