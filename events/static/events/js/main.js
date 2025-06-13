// Main JavaScript for Event Management System

document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for event cards
    const eventCards = document.querySelectorAll('.event-card');
    eventCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Only navigate if the click wasn't on a button or link
            if (!e.target.closest('a.btn')) {
                const detailLink = this.querySelector('a[href*="event_detail"]');
                if (detailLink) {
                    window.location.href = detailLink.getAttribute('href');
                }
            }
        });
    });

    // Form validation
    const registrationForm = document.querySelector('.registration-form');
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(e) {
            const nameInput = document.getElementById('id_name');
            const emailInput = document.getElementById('id_email');
            let isValid = true;

            // Simple validation
            if (nameInput.value.trim() === '') {
                createErrorMessage(nameInput, 'Name is required');
                isValid = false;
            }

            if (emailInput.value.trim() === '') {
                createErrorMessage(emailInput, 'Email is required');
                isValid = false;
            } else if (!isValidEmail(emailInput.value.trim())) {
                createErrorMessage(emailInput, 'Please enter a valid email address');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();
            }
        });
    }

    // Helper functions
    function createErrorMessage(input, message) {
        // Remove any existing error messages
        const parent = input.parentElement;
        let errorDiv = parent.querySelector('.js-form-error');
        
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'form-errors js-form-error';
            parent.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
        input.classList.add('error-input');
    }

    function isValidEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email);
    }
});
