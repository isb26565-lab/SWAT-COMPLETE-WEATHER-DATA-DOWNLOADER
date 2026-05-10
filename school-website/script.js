// Set active navigation link based on current page
document.addEventListener('DOMContentLoaded', function() {
    const currentLocation = location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentLocation || 
            (currentLocation === '' && link.getAttribute('href') === 'index.html')) {
            link.classList.add('active');
        }
    });

    // Smooth scrolling for navigation links
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
});

// Handle contact form submission
function handleSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const name = form.querySelector('#name').value;
    const email = form.querySelector('#email').value;
    const subject = form.querySelector('#subject').value;
    const message = form.querySelector('#message').value;
    
    // Validate form
    if (!name || !email || !subject || !message) {
        showFormMessage('Please fill in all required fields.', 'error');
        return;
    }
    
    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showFormMessage('Please enter a valid email address.', 'error');
        return;
    }
    
    // Simulate form submission (in real application, this would send to a server)
    const formData = {
        name: name,
        email: email,
        subject: subject,
        message: message,
        timestamp: new Date().toISOString()
    };
    
    // Save to local storage for demonstration
    const submissions = JSON.parse(localStorage.getItem('contactSubmissions') || '[]');
    submissions.push(formData);
    localStorage.setItem('contactSubmissions', JSON.stringify(submissions));
    
    // Show success message
    showFormMessage('Thank you for your message! We will get back to you soon.', 'success');
    
    // Reset form
    form.reset();
    
    // Clear success message after 5 seconds
    setTimeout(() => {
        showFormMessage('', '');
    }, 5000);
}

// Show form message
function showFormMessage(message, type) {
    const messageElement = document.getElementById('form-message');
    if (!messageElement) return;
    
    if (message) {
        messageElement.textContent = message;
        messageElement.className = type === 'success' ? 'success-message' : 'error-message';
        messageElement.style.display = 'block';
        
        if (type === 'error') {
            messageElement.style.backgroundColor = '#e74c3c';
        } else {
            messageElement.style.backgroundColor = '#27ae60';
        }
    } else {
        messageElement.style.display = 'none';
    }
}

// Navbar scroll effect - adds shadow when scrolled
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.boxShadow = '0 5px 15px rgba(0,0,0,0.2)';
    } else {
        navbar.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
    }
});

// Intersection Observer for animations on scroll
if ('IntersectionObserver' in window) {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe all feature cards, course cards, and other elements
    const elementsToObserve = document.querySelectorAll(
        '.feature-card, .course-card, .team-member, .testimonial, .program'
    );
    
    elementsToObserve.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });
}

// Mobile menu toggle (for future mobile navigation enhancement)
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        navMenu.classList.toggle('active');
    }
}

// Utility function to get URL parameters
function getUrlParameter(name) {
    const url = new URL(window.location);
    return url.searchParams.get(name);
}

// Log analytics for page views (for future use with analytics service)
function logPageView() {
    const pageInfo = {
        page: document.title,
        url: window.location.href,
        timestamp: new Date().toISOString(),
        referrer: document.referrer
    };
    console.log('Page View:', pageInfo);
}

// Call logPageView on page load
window.addEventListener('load', logPageView);

// Counter animation for stats section
function animateCounters() {
    const stats = document.querySelectorAll('.stat-item h2');
    
    stats.forEach(stat => {
        const finalValue = parseInt(stat.textContent);
        const duration = 2000; // 2 seconds
        const steps = 60;
        const stepValue = finalValue / steps;
        let currentStep = 0;
        
        if (isNaN(finalValue)) return; // Skip non-numeric values
        
        const interval = setInterval(() => {
            currentStep++;
            const currentValue = Math.round(stepValue * currentStep);
            
            // Preserve original formatting (e.g., "95%")
            const originalText = stat.textContent;
            const suffix = originalText.replace(/[0-9]/g, '');
            
            stat.textContent = currentValue + suffix;
            
            if (currentStep >= steps) {
                stat.textContent = originalText;
                clearInterval(interval);
            }
        }, duration / steps);
    });
}

// Trigger counter animation when stats section is in view
if ('IntersectionObserver' in window) {
    const statsSection = document.querySelector('.stats');
    if (statsSection) {
        const statsObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.dataset.animated) {
                    animateCounters();
                    entry.target.dataset.animated = 'true';
                    statsObserver.unobserve(entry.target);
                }
            });
        });
        statsObserver.observe(statsSection);
    }
}

// Error handler for broken images
document.addEventListener('error', function(e) {
    if (e.target.tagName === 'IMG') {
        e.target.src = 'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22%3E%3Crect fill=%22%23ddd%22 width=%22400%22 height=%22300%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 font-family=%22sans-serif%22 font-size=%2220%22 fill=%22%23999%22%3EImage Not Found%3C/text%3E%3C/svg%3E';
    }
}, true);

// Add ripple effect on button clicks (for better UX)
document.addEventListener('click', function(e) {
    if (e.target.matches('button, .cta-button')) {
        const button = e.target;
        const rect = button.getBoundingClientRect();
        const circle = document.createElement('span');
        
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        circle.style.width = circle.style.height = size + 'px';
        circle.style.left = x + 'px';
        circle.style.top = y + 'px';
        circle.classList.add('ripple');
        
        button.appendChild(circle);
        
        setTimeout(() => circle.remove(), 600);
    }
}, false);

// Add ripple effect styles dynamically
const style = document.createElement('style');
style.textContent = `
    button, .cta-button {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.5);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

console.log('Elite Academy Website - All interactive features loaded');
