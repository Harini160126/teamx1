// JavaScript for Placement Support System
document.addEventListener('DOMContentLoaded', function() {
    // Hamburger Menu Functionality
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const navMenu = document.getElementById('navMenu');
    
    if (hamburgerBtn && navMenu) {
        // Create overlay element
        const overlay = document.createElement('div');
        overlay.className = 'nav-overlay';
        document.body.appendChild(overlay);
        
        function toggleMenu() {
            hamburgerBtn.classList.toggle('active');
            navMenu.classList.toggle('active');
            overlay.classList.toggle('active');
            document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
        }
        
        function closeMenu() {
            hamburgerBtn.classList.remove('active');
            navMenu.classList.remove('active');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
        
        hamburgerBtn.addEventListener('click', toggleMenu);
        overlay.addEventListener('click', closeMenu);
        
        // Close menu when clicking on a link
        navMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', closeMenu);
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && navMenu.classList.contains('active')) {
                closeMenu();
            }
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Add loading state to buttons
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Processing...';
                
                // Re-enable after 3 seconds (or when form submission completes)
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = submitBtn.dataset.originalText || 'Submit';
                }, 3000);
            }
        });
    });

    // Auto-hide flash messages after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 500);
        });
    }, 5000);

    // Toggle password visibility
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(input => {
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.innerHTML = '👁️';
        toggleBtn.style.position = 'absolute';
        toggleBtn.style.right = '10px';
        toggleBtn.style.top = '50%';
        toggleBtn.style.transform = 'translateY(-50%)';
        toggleBtn.style.background = 'none';
        toggleBtn.style.border = 'none';
        toggleBtn.style.cursor = 'pointer';
        
        if (input.parentNode && input.parentNode.tagName === 'LABEL') {
            input.style.paddingRight = '40px';
            input.parentNode.style.position = 'relative';
            input.parentNode.appendChild(toggleBtn);
            
            toggleBtn.addEventListener('click', () => {
                if (input.type === 'password') {
                    input.type = 'text';
                    toggleBtn.innerHTML = '🙈';
                } else {
                    input.type = 'password';
                    toggleBtn.innerHTML = '👁️';
                }
            });
        }
    });

    // Add loading animation to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.classList.contains('loading')) return;
            
            this.classList.add('loading');
            setTimeout(() => {
                this.classList.remove('loading');
            }, 1000);
        });
    });

    // Filter functionality for student lists
    const filterInputs = document.querySelectorAll('.filter-input');
    filterInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const container = document.querySelector(this.dataset.target);
            if (!container) return;

            const items = container.querySelectorAll('[data-search]');
            items.forEach(item => {
                const itemText = item.dataset.search.toLowerCase();
                if (itemText.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });

    // Modal functionality
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const modalId = this.dataset.modalTarget;
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'flex';
                document.body.style.overflow = 'hidden';
            }
        });
    });

    // Close modals
    const closeButtons = document.querySelectorAll('.close-modal, .modal-overlay');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal') || document.querySelector('.modal[style*="flex"]');
            if (modal) {
                modal.style.display = 'none';
                document.body.style.overflow = '';
            }
        });
    });

    // Prevent modal content from closing when clicked
    const modalContents = document.querySelectorAll('.modal-content');
    modalContents.forEach(content => {
        content.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });

    // Handle ESC key to close modals
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal[style*="flex"]');
            openModals.forEach(modal => {
                modal.style.display = 'none';
            });
            document.body.style.overflow = '';
        }
    });

    // Add tooltips to elements with title attributes
    const tooltipElements = document.querySelectorAll('[title]:not([data-tooltip-initialized])');
    tooltipElements.forEach(element => {
        element.setAttribute('data-tooltip-initialized', 'true');
        
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.title;
            tooltip.style.cssText = `
                position: absolute;
                bottom: 100%;
                left: 50%;
                transform: translateX(-50%);
                background: #333;
                color: white;
                padding: 0.5rem 0.75rem;
                border-radius: 4px;
                font-size: 0.875rem;
                white-space: nowrap;
                z-index: 1000;
                margin-bottom: 0.25rem;
            `;
            
            this.appendChild(tooltip);
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltip = this.querySelector('.tooltip');
            if (tooltip) tooltip.remove();
        });
    });

    // Animate counters on scroll
    const animateCounter = (element) => {
        const target = +element.getAttribute('data-target');
        const duration = 2000;
        const increment = target / (duration / 16);
        let current = 0;
        
        const updateCount = () => {
            current += increment;
            if (current < target) {
                element.textContent = Math.ceil(current);
                setTimeout(updateCount, 16);
            } else {
                element.textContent = target;
            }
        };
        
        updateCount();
    };

    // Intersection Observer for counter animations
    const observerOptions = {
        threshold: 0.5
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target.querySelector('[data-target]');
                if (counter) {
                    animateCounter(counter);
                    observer.unobserve(entry.target);
                }
            }
        });
    }, observerOptions);

    // Observe elements with counter class
    document.querySelectorAll('.stat-card').forEach(card => {
        observer.observe(card);
    });

    // Add ripple effect to buttons
    const rippleButtons = document.querySelectorAll('.btn:not(.no-ripple)');
    rippleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            let x = e.clientX - e.target.getBoundingClientRect().left;
            let y = e.clientY - e.target.getBoundingClientRect().top;
            
            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add ripple CSS dynamically
    const style = document.createElement('style');
    style.textContent = `
        .ripple {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.7);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
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
});

// Utility functions
const Utils = {
    // Show loading spinner
    showLoading: function(element) {
        element.innerHTML = '<span class="loading-spinner">⏳</span>';
    },
    
    // Hide loading spinner
    hideLoading: function(element, originalContent) {
        element.innerHTML = originalContent;
    },
    
    // Format currency
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },
    
    // Format date
    formatDate: function(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    },
    
    // Debounce function
    debounce: function(func, wait) {
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
};