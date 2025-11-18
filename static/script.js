document.addEventListener('DOMContentLoaded', () => {
    // --- Global Theme & Language Handling ---

    const body = document.body;
    const themeToggle = document.querySelector('.theme-toggle');

    function applyTheme(theme) {
        body.classList.remove('light', 'dark');
        body.classList.add(theme);
        localStorage.setItem('sct_theme', theme);
        // Update the toggle icon
        if (themeToggle) {
            themeToggle.innerHTML = theme === 'dark' ? '&#9728;' : '&#9729;'; // Sun or Moon icons
            themeToggle.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`);
        }
    }

    // Initialize theme from local storage or server-provided setting
    const initialTheme = body.getAttribute('data-initial-theme') || localStorage.getItem('sct_theme') || 'light';
    applyTheme(initialTheme);

    // Theme Toggle Handler
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = body.classList.contains('dark') ? 'dark' : 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            applyTheme(newTheme);

            // If on settings page, update setting in backend
            if (window.location.pathname.includes('/settings')) {
                updateBackendSetting('theme', newTheme);
            }
        });
    }

    // Function to update backend settings (used in settings page)
    async function updateBackendSetting(key, value) {
        try {
            const response = await fetch('/update_settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ [key]: value })
            });
            if (!response.ok) {
                console.error('Failed to update backend setting.');
            }
        } catch (error) {
            console.error('Network error during settings update:', error);
        }
    }

    // --- Setup Wizard Logic (Only on setup.html) ---

    const setupWizard = document.querySelector('.setup-wizard');
    if (setupWizard) {
        let currentStep = 1;
        const steps = document.querySelectorAll('.setup-step');
        
        // State variables for setup
        let selectedLang = document.getElementById('lang-select').value;
        let selectedTheme = document.querySelector('input[name="theme"]:checked').value;

        // Function to show a specific step
        function showStep(stepNum) {
            const newStep = document.getElementById(`step-${stepNum}`);
            if (!newStep) return;

            steps.forEach(step => {
                const stepElement = step; // Use a distinct variable for clarity
                const stepIndex = parseInt(stepElement.dataset.step);

                if (stepIndex === currentStep) {
                    stepElement.classList.remove('active');
                    stepElement.classList.add('leaving');
                } else if (stepIndex === stepNum) {
                    stepElement.classList.remove('leaving', 'entering');
                    // Set a slight delay before adding 'active' to ensure 'leaving' transition starts
                    setTimeout(() => {
                        stepElement.classList.add('active', 'entering');
                        setTimeout(() => stepElement.classList.remove('entering'), 300); // Remove entering class after transition
                    }, 50);
                } else {
                    stepElement.classList.remove('active', 'leaving', 'entering');
                }
            });

            currentStep = stepNum;
        }

        // Helper function to display non-blocking messages within setup steps
        function displaySetupMessage(stepNum, message, type = 'error') {
            const msgElement = document.getElementById(`step-${stepNum}-message`);
            if (msgElement) {
                msgElement.textContent = message;
                // Use CSS variables for consistent theming
                msgElement.style.color = type === 'error' ? '#DC2626' : 'var(--color-primary-dark)';
                msgElement.style.display = message ? 'block' : 'none';
            }
        }

        // Initialize Step 1
        document.getElementById('step-1').classList.add('active');

        // --- Step 1 Handlers ---
        
        document.getElementById('lang-select').addEventListener('change', (e) => {
            selectedLang = e.target.value;
        });

        document.querySelectorAll('input[name="theme"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                selectedTheme = e.target.value;
                applyTheme(selectedTheme); // Immediate theme application
            });
        });

        // Navigation from Step 1 to Step 2
        document.getElementById('next-step-2').addEventListener('click', () => {
             showStep(2);
        });

        // --- Step 2 Handlers (Login/Signup) ---
        
        // Back to Step 1
        document.getElementById('back-step-1').addEventListener('click', () => {
            showStep(1);
        });

        // Submit (Login/Signup) and Continue to Step 3 or Dashboard
        document.getElementById('submit-step-2').addEventListener('click', async () => {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            displaySetupMessage(2, '', 'error'); // Clear previous message

            if (!email || !password) {
                 displaySetupMessage(2, 'Email and password are required.', 'error');
                 return;
            }

            try {
                const response = await fetch('/login_or_signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password, lang: selectedLang, theme: selectedTheme })
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    // Update theme based on final state from backend (if provided)
                    applyTheme(result.theme || selectedTheme); 
                    
                    // Note: Language is saved but requires a full page reload (dashboard redirect) to apply 
                    // since the app text is rendered server-side in the template.

                    if (result.setup_complete) {
                        window.location.href = '/dashboard';
                    } else {
                        showStep(3);
                    }
                } else {
                    displaySetupMessage(2, result.message || 'Login/Signup failed.', 'error');
                }
            } catch (error) {
                displaySetupMessage(2, 'A network error occurred. Please try again.', 'error');
                console.error('Login/Signup error:', error);
            }
        });

        // --- Step 3 Handlers (Number of Plants) ---

        // Back to Step 2
        document.getElementById('back-step-2').addEventListener('click', () => {
            showStep(2);
        });
        
        // Dynamic Plant Input Generation
        const numPlantsInput = document.getElementById('num-plants');
        const plantInputsContainer = document.getElementById('plant-inputs-container');

        numPlantsInput.addEventListener('input', () => {
            const num = parseInt(numPlantsInput.value);
            plantInputsContainer.innerHTML = '';
            document.getElementById('next-step-4').disabled = true;
            if (num > 0 && num <= 10) { // Limit to 10 for sanity
                for (let i = 0; i < num; i++) {
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.name = `plant-${i}`;
                    // The placeholder text is still English in JS, as dynamic JS messages are complex to localize fully on the client side
                    input.placeholder = `Name of Plant ${i + 1}`; 
                    input.required = true;
                    plantInputsContainer.appendChild(input);
                }
                document.getElementById('next-step-4').disabled = false;
            }
        });
        
        // Navigation from Step 3 to Step 4
        document.getElementById('next-step-4').addEventListener('click', () => {
            displaySetupMessage(3, '', 'error');
            if (plantInputsContainer.children.length > 0) {
                showStep(4);
            } else {
                displaySetupMessage(3, 'Please enter the number of plants.', 'error');
            }
        });

        // --- Step 4 Handlers (Plant Names) ---
        
        // Back to Step 3
        document.getElementById('back-step-3').addEventListener('click', () => {
            showStep(3);
        });

        // Navigation from Step 4 to Step 5
        document.getElementById('next-step-5').addEventListener('click', () => {
            displaySetupMessage(4, '', 'error');
            const plantInputs = plantInputsContainer.querySelectorAll('input[type="text"]');
            let allValid = true;
            plantInputs.forEach(input => {
                if (input.value.trim() === '') {
                    allValid = false;
                    input.focus();
                }
            });
            if (allValid) {
                showStep(5);
            } else {
                displaySetupMessage(4, 'Please name all your plants.', 'error');
            }
        });

        // --- Step 5 Handlers (Land Size & Completion) ---

        // Back to Step 4
        document.getElementById('back-step-4').addEventListener('click', () => {
            showStep(4);
        });

        // Complete Setup API call
        document.getElementById('complete-setup').addEventListener('click', async () => {
            displaySetupMessage(5, '', 'error');
            const numPlants = parseInt(document.getElementById('num-plants').value);
            const acres = parseFloat(document.getElementById('acres').value);
            
            if (isNaN(acres) || acres <= 0) {
                displaySetupMessage(5, 'Please enter a valid land size in acres (must be > 0).', 'error');
                return;
            }

            const plantInputs = plantInputsContainer.querySelectorAll('input[type="text"]');
            const plantNames = Array.from(plantInputs).map(input => input.value.trim());

            try {
                const response = await fetch('/complete_setup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        num_plants: numPlants,
                        plant_names: plantNames,
                        acres: acres
                    })
                });

                const contentType = response.headers.get("content-type");
                
                // IMPORTANT: Check for JSON content type
                if (contentType && contentType.includes("application/json")) {
                    const result = await response.json();

                    if (result.success) {
                        window.location.href = '/dashboard';
                    } else if (response.status === 401 || response.status === 403) {
                        // Handle explicit JSON errors from the server (e.g., Session Expired from updated app.py)
                        displaySetupMessage(5, result.message || 'Authentication required. Please return to Step 2.', 'error');
                    } else {
                        // Display generic error message from server's JSON response
                        displaySetupMessage(5, result.message || 'Failed to complete setup.', 'error');
                    }
                } else {
                    // This block still catches non-JSON, but the app.py update should prevent it now.
                    const responseText = await response.text();
                    displaySetupMessage(5, 'A server error occurred, possibly due to a session timeout. Please try again from Step 2.', 'error');
                    // CRITICAL DEBUGGING STEP: Log the actual content returned by the server
                    console.error('Setup completion error: Received unexpected response.', { status: response.status, responseText });
                }
            } catch (error) {
                displaySetupMessage(5, 'A network error occurred while completing setup. Please try again.', 'error');
                console.error('Setup completion (Network) error:', error);
            }
        });
    }


    // --- Dashboard Logic (Vitals) ---

    const pHValue = 6.5 + (Math.random() * 1.5 - 0.75); // Range 5.75 to 7.25
    const moistureValue = 40 + (Math.random() * 40); // Range 40 to 80

    function updateVitals(elementId, value, max, unit) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const percent = (value / max) * 100;
        const progressValue = element.querySelector('.progress-value');
        const progressBar = element.querySelector('.progress-bar');
        
        if (progressValue) {
             progressValue.textContent = `${value.toFixed(1)}${unit}`;
        }
        
        if (progressBar) {
            // Determine the color based on the current theme applied to the body
            const isDark = body.classList.contains('dark');
            const primaryColor = isDark ? 'var(--color-primary-dark)' : 'var(--color-primary)';
            const trackColor = isDark ? 'var(--color-bg-dark)' : 'var(--color-card-light)';
            
            // Update the CSS conic gradient for the progress bar animation
            progressBar.style.background = `conic-gradient(${primaryColor} ${percent}%, ${trackColor} ${percent}%)`;
        }
    }

    if (document.getElementById('ph-vital')) {
        updateVitals('ph-vital', pHValue, 14, ''); // pH scale 0-14, though soil range is tighter
        updateVitals('moisture-vital', moistureValue, 100, '%');
    }

    // --- Settings Page Logic ---
    
    // Custom Confirmation Modal Logic
    const confirmModal = document.getElementById('confirmation-modal');
    const confirmText = document.getElementById('confirm-text');
    const confirmBtn = document.getElementById('confirm-action-btn');
    const cancelBtn = document.getElementById('cancel-action-btn');
    let confirmationCallback = null;

    function showCustomConfirmation(message, callback) {
        // Message text is retrieved via Jinja, so we only need to show the modal
        confirmationCallback = callback;
        confirmModal.classList.remove('hidden');
    }

    if (confirmModal) {
        cancelBtn.addEventListener('click', () => confirmModal.classList.add('hidden'));
        confirmBtn.addEventListener('click', () => {
            confirmModal.classList.add('hidden');
            if (confirmationCallback) {
                confirmationCallback(true);
            }
        });
    }


    const settingsForm = document.getElementById('settings-form');
    if (settingsForm) {
        settingsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const newLang = document.getElementById('setting-lang-select').value;
            const newTheme = document.getElementById('setting-theme-select').value;

            // Theme change is already handled by the toggle, but we explicitly send both here
            await updateBackendSetting('lang', newLang);
            await updateBackendSetting('theme', newTheme);
            
            // Reload to apply new language settings (server-side text update)
            window.location.reload();
        });

        // Reset Setup Confirmation
        document.getElementById('reset-setup-btn').addEventListener('click', () => {
            // Message is now retrieved from the HTML via Jinja, not passed dynamically
            showCustomConfirmation('', async (isConfirmed) => {
                if (isConfirmed) {
                    try {
                        const response = await fetch('/reset_setup', { method: 'POST' });
                        const result = await response.json();
                        if (result.success) {
                            window.location.href = '/setup';
                        } else {
                            // Use a simple error display if the modal is closed
                            console.error('Failed to reset setup.');
                        }
                    } catch (error) {
                        console.error('Network error during reset:', error);
                    }
                }
            });
        });
    }

});
