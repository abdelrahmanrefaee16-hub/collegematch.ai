// ===== PAGE NAVIGATION SYSTEM =====
// Function to show a specific page and hide others
function showPage(pageId) {
    // Hide all pages
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        page.classList.remove('active');
    });
    
    // Show the selected page
    const selectedPage = document.getElementById(pageId);
    if (selectedPage) {
        selectedPage.classList.add('active');
        // Scroll to top when changing pages
        window.scrollTo(0, 0);
    }
}

// ===== NAVIGATION LINKS EVENT LISTENERS =====
document.addEventListener('DOMContentLoaded', function() {
    // Get all navigation links
    const navLinks = document.querySelectorAll('[data-page]');
    
    // Add click event to each navigation link
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const pageId = this.getAttribute('data-page');
            showPage(pageId);
            
            // Close mobile menu if open
            const navLinksMenu = document.querySelector('.nav-links');
            navLinksMenu.classList.remove('active');
        });
    });
    
    // ===== MOBILE MENU TOGGLE =====
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinksMenu = document.querySelector('.nav-links');
    
    menuToggle.addEventListener('click', function() {
        navLinksMenu.classList.toggle('active');
    });
    
    // ===== SIGN UP FORM HANDLER =====
    const signupForm = document.getElementById('signupForm');
    
    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const fullname = document.getElementById('fullname').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // Basic validation
        if (fullname && email && password) {
            // Store user data (in a real app, this would be sent to a server)
            const userData = {
                fullname: fullname,
                email: email,
                timestamp: new Date().toISOString()
            };
            
            // Store in memory (could use localStorage in a real app)
            console.log('User registered:', userData);
            
            // Show success message (optional)
            alert('Account created successfully! Please complete the questionnaire.');
            
            // Navigate to questionnaire page
            showPage('questionnaire');
            
            // Reset form
            signupForm.reset();
        }
    });
    
    // ===== QUESTIONNAIRE FORM HANDLER =====
    const questionnaireForm = document.getElementById('questionnaireForm');
    
    questionnaireForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get all form values
        const formData = {
            gender: document.getElementById('gender').value,
            maritalStatus: document.getElementById('marital-status').value,
            studentType: document.getElementById('student-type').value,
            fatherOccupation: document.getElementById('father-occupation').value,
            motherOccupation: document.getElementById('mother-occupation').value,
            motivation: document.getElementById('motivation').value,
            parentEducation: document.getElementById('parent-education').value,
            tuition: document.getElementById('tuition').value
        };
        
        // Get extracurricular activities
        const extracurricular = [];
        document.querySelectorAll('input[name="extracurricular"]:checked').forEach(checkbox => {
            extracurricular.push(checkbox.value);
        });
        formData.extracurricular = extracurricular;
        
        // Calculate prediction based on form data
        const prediction = calculatePrediction(formData);
        
        // Update results page with prediction
        updateResultsPage(prediction);
        
        // Navigate to results page
        showPage('results');
        
        // Log data for debugging
        console.log('Questionnaire submitted:', formData);
        console.log('Prediction:', prediction);
    });
    
    // ===== HANDLE "NONE" CHECKBOX EXCLUSIVITY =====
    const noneCheckbox = document.getElementById('none');
    const otherCheckboxes = document.querySelectorAll('input[name="extracurricular"]:not(#none)');
    
    // When "None" is checked, uncheck all others
    noneCheckbox.addEventListener('change', function() {
        if (this.checked) {
            otherCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
        }
    });
    
    // When any other checkbox is checked, uncheck "None"
    otherCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                noneCheckbox.checked = false;
            }
        });
    });
});

// ===== PREDICTION CALCULATION ALGORITHM =====
function calculatePrediction(data) {
    let score = 50; // Base score
    
    // Motivation factor (highest impact)
    if (data.motivation === 'high') score += 25;
    else if (data.motivation === 'medium') score += 10;
    else if (data.motivation === 'low') score -= 15;
    
    // Parent education factor
    const educationScores = {
        'doctorate': 15,
        'master': 12,
        'bachelor': 10,
        'associate': 7,
        'high-school': 5,
        'less-than-high-school': 2
    };
    score += educationScores[data.parentEducation] || 0;
    
    // Extracurricular involvement
    if (data.extracurricular.length > 0 && !data.extracurricular.includes('none')) {
        score += data.extracurricular.length * 3;
    }
    
    // Parent occupation (combined impact)
    const occupationScores = {
        'professional': 8,
        'business': 7,
        'government': 7,
        'skilled-worker': 5,
        'self-employed': 5,
        'homemaker': 3,
        'retired': 3,
        'unemployed': 0,
        'other': 3
    };
    score += (occupationScores[data.fatherOccupation] || 0);
    score += (occupationScores[data.motherOccupation] || 0);
    
    // Tuition payment status
    if (data.tuition === 'fully-paid') score += 10;
    else if (data.tuition === 'partially-paid') score += 5;
    else if (data.tuition === 'loan') score -= 3;
    
    // Student type (international students often have additional support)
    if (data.studentType === 'international') score += 3;
    
    // Marital status (single students typically have more time for studies)
    if (data.maritalStatus === 'single') score += 5;
    else if (data.maritalStatus === 'married') score -= 5;
    
    // Ensure score is within 0-100 range
    score = Math.max(0, Math.min(100, score));
    
    // Determine outcome category
    let outcome, label, message;
    
    if (score >= 75) {
        outcome = 'graduate';
        label = 'Graduate';
        message = 'Your dedication is paying off! Keep up the great work and embrace every learning opportunity.';
    } else if (score >= 50) {
        outcome = 'enrolled';
        label = 'Stay Enrolled';
        message = 'You\'re on the right track! Focus on improving your study habits and seeking support when needed.';
    } else {
        outcome = 'at-risk';
        label = 'At Risk';
        message = 'Don\'t give up! Consider seeking academic support, improving time management, and connecting with advisors.';
    }
    
    return {
        percentage: score,
        outcome: outcome,
        label: label,
        message: message
    };
}

// ===== UPDATE RESULTS PAGE WITH PREDICTION =====
function updateResultsPage(prediction) {
    const percentageElement = document.getElementById('predictionPercentage');
    const labelElement = document.getElementById('predictionLabel');
    const messageElement = document.getElementById('predictionMessage');
    
    if (percentageElement) {
        percentageElement.textContent = prediction.percentage + '%';
        
        // Change color based on outcome
        if (prediction.outcome === 'graduate') {
            percentageElement.style.color = '#52a845';
            labelElement.style.backgroundColor = '#52a845';
        } else if (prediction.outcome === 'enrolled') {
            percentageElement.style.color = '#f39c12';
            labelElement.style.backgroundColor = '#f39c12';
        } else {
            percentageElement.style.color = '#e74c3c';
            labelElement.style.backgroundColor = '#e74c3c';
        }
    }
    
    if (labelElement) {
        labelElement.textContent = prediction.label;
    }
    
    if (messageElement) {
        messageElement.textContent = prediction.message;
    }
}

// ===== SMOOTH SCROLLING FOR ANCHOR LINKS =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// ===== FORM VALIDATION HELPERS =====
// Add real-time validation feedback
function addValidationListeners() {
    const inputs = document.querySelectorAll('input[required], select[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.style.borderColor = '#e74c3c';
            } else {
                this.style.borderColor = '#52a845';
            }
        });
        
        input.addEventListener('focus', function() {
            this.style.borderColor = '#52a845';
        });
    });
}

// Initialize validation when DOM is ready
document.addEventListener('DOMContentLoaded', addValidationListeners);

// ===== CONSOLE WELCOME MESSAGE =====
console.log('%c🎓 Academic Future Predictor', 'font-size: 20px; color: #52a845; font-weight: bold;');
console.log('%cWelcome! This application helps predict academic outcomes based on various factors.', 'font-size: 12px; color: #666;');
console.log('%cDeveloped with HTML, CSS, and JavaScript', 'font-size: 10px; color: #999;');
