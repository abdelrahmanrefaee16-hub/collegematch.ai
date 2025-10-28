// Global state
let userData = {
    name: '',
    email: ''
};

let questionnaireData = {};
let predictionResult = null;

// Page Navigation
function navigateTo(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    // Scroll to top
    window.scrollTo(0, 0);
}

// Sign Up Form Handler
document.getElementById('signup-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    userData.name = document.getElementById('name').value;
    userData.email = document.getElementById('email').value;
    
    // Update user name in questionnaire
    document.getElementById('user-name').textContent = userData.name;
    
    navigateTo('questionnaire');
});

// Questionnaire Form Handler
document.getElementById('questionnaire-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Collect all form data
    questionnaireData = {
        nationality: document.getElementById('nationality').value,
        gender: document.querySelector('input[name="gender"]:checked').value,
        parentOccupation: document.getElementById('parentOccupation').value,
        maritalStatus: document.getElementById('maritalStatus').value,
        studentType: document.querySelector('input[name="studentType"]:checked').value,
        previousQualification: document.getElementById('previousQualification').value,
        enrollmentAge: document.getElementById('enrollmentAge').value,
        tuitionUpToDate: document.querySelector('input[name="tuitionUpToDate"]:checked').value,
        displaced: document.querySelector('input[name="displaced"]:checked').value,
        specialNeeds: document.querySelector('input[name="specialNeeds"]:checked').value,
        firstSemesterGrade: document.getElementById('firstSemesterGrade').value,
        secondSemesterGrade: document.getElementById('secondSemesterGrade').value
    };
    
    // Calculate prediction
    predictionResult = calculatePrediction(questionnaireData);
    
    // Display results
    displayResults();
    
    navigateTo('results');
});

// Prediction Algorithm
function calculatePrediction(data) {
    let score = 0;
    
    // First Semester Grade (0-20) - 35 points
    const firstSemester = parseFloat(data.firstSemesterGrade) || 0;
    score += (firstSemester / 20) * 35;
    
    // Second Semester Grade (0-20) - 35 points
    const secondSemester = parseFloat(data.secondSemesterGrade) || 0;
    score += (secondSemester / 20) * 35;
    
    // Previous Qualification - 8 points
    if (data.previousQualification === 'bachelor' || data.previousQualification === 'masters') {
        score += 8;
    } else if (data.previousQualification === 'high-school') {
        score += 5;
    } else {
        score += 3;
    }
    
    // Tuition Up To Date - 7 points
    if (data.tuitionUpToDate === 'yes') {
        score += 7;
    } else if (data.tuitionUpToDate === 'scholarship') {
        score += 6;
    } else {
        score += 2;
    }
    
    // Parent Occupation - 5 points
    if (data.parentOccupation === 'professional' || data.parentOccupation === 'manager') {
        score += 5;
    } else if (data.parentOccupation === 'skilled') {
        score += 3;
    } else {
        score += 2;
    }
    
    // Enrollment Age - 4 points (ideal: 18-22)
    const age = parseFloat(data.enrollmentAge) || 0;
    if (age >= 18 && age <= 22) {
        score += 4;
    } else if (age < 18 || (age > 22 && age <= 25)) {
        score += 2;
    } else {
        score += 1;
    }
    
    // Student Type - 3 points
    if (data.studentType === 'national') {
        score += 3;
    } else {
        score += 2;
    }
    
    // Marital Status - 2 points
    if (data.maritalStatus === 'single') {
        score += 2;
    } else {
        score += 1;
    }
    
    // Displaced - 1 point
    if (data.displaced === 'no') {
        score += 1;
    }
    
    // Calculate percentage and determine outcome
    const percentage = Math.min(Math.round(score), 100);
    
    let outcome;
    if (percentage >= 70) {
        outcome = 'Graduate';
    } else if (percentage >= 45) {
        outcome = 'Remain Enrolled';
    } else {
        outcome = 'Drop Out';
    }
    
    return { outcome, percentage };
}

// Display Results
function displayResults() {
    const { outcome, percentage } = predictionResult;
    
    // Update user name
    document.getElementById('results-user-name').textContent = userData.name;
    
    // Update outcome icon
    const outcomeIcon = document.getElementById('outcome-icon');
    const outcomeClass = outcome === 'Graduate' ? 'graduate' : outcome === 'Remain Enrolled' ? 'enrolled' : 'dropout';
    
    let iconSVG = '';
    if (outcome === 'Graduate') {
        iconSVG = '<svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="color: #16a34a;"><path stroke-linecap="round" stroke-linejoin="round" d="M12 14l9-5-9-5-9 5 9 5z"/><path stroke-linecap="round" stroke-linejoin="round" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z"/><path stroke-linecap="round" stroke-linejoin="round" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222"/></svg>';
    } else if (outcome === 'Remain Enrolled') {
        iconSVG = '<svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="color: #ca8a04;"><path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>';
    } else {
        iconSVG = '<svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="color: #dc2626;"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>';
    }
    outcomeIcon.innerHTML = iconSVG;
    
    // Update outcome title
    const outcomeTitle = document.getElementById('outcome-title');
    outcomeTitle.textContent = `Predicted Outcome: ${outcome}`;
    outcomeTitle.className = `outcome-title ${outcomeClass}`;
    
    // Update outcome message
    const outcomeMessage = document.getElementById('outcome-message');
    let message = '';
    if (outcome === 'Graduate') {
        message = 'Congratulations! Based on your responses, our analysis predicts that you are on track to successfully graduate.';
    } else if (outcome === 'Remain Enrolled') {
        message = 'Our analysis suggests you will likely remain enrolled, but there may be some challenges ahead. Let\'s work on improving your outcomes.';
    } else {
        message = 'Our analysis indicates some serious concerns. However, with the right changes and support, you can turn this around.';
    }
    outcomeMessage.textContent = message;
    
    // Update percentage
    const percentageValue = document.getElementById('percentage-value');
    percentageValue.textContent = `${percentage}%`;
    percentageValue.className = `percentage-value ${outcomeClass}`;
    
    // Update progress bar
    const progressFill = document.getElementById('progress-fill');
    progressFill.className = `progress-fill ${outcomeClass}`;
    setTimeout(() => {
        progressFill.style.width = `${percentage}%`;
    }, 100);
    
    // Generate recommendations
    generateRecommendations();
}

// Generate Recommendations
function generateRecommendations() {
    const recommendations = [];
    const data = questionnaireData;
    const { outcome } = predictionResult;
    
    // Grade-based recommendations
    const firstSemester = parseFloat(data.firstSemesterGrade) || 0;
    const secondSemester = parseFloat(data.secondSemesterGrade) || 0;
    const averageGrade = (firstSemester + secondSemester) / 2;
    
    if (averageGrade < 10) {
        recommendations.push({
            icon: '📚',
            title: 'Urgent: Seek Academic Support Immediately',
            description: 'Your grades are critically low. Schedule meetings with professors, join tutoring programs, and consider reducing course load if possible.',
            priority: 'high'
        });
    } else if (averageGrade < 14) {
        recommendations.push({
            icon: '📚',
            title: 'Improve Your Academic Performance',
            description: 'Focus on better study techniques, attend all classes, and don\'t hesitate to ask questions. Form study groups with high-performing peers.',
            priority: 'high'
        });
    } else if (averageGrade >= 16) {
        recommendations.push({
            icon: '🎓',
            title: 'Maintain Your Excellent Performance',
            description: 'You\'re doing great! Continue your current study habits and consider mentoring other students or pursuing advanced coursework.',
            priority: 'medium'
        });
    }
    
    // Grade improvement trend
    if (secondSemester > firstSemester + 1) {
        recommendations.push({
            icon: '📈',
            title: 'Keep Up Your Positive Trajectory',
            description: 'Your grades are improving! Whatever changes you made are working. Stay consistent with these successful strategies.',
            priority: 'medium'
        });
    } else if (firstSemester > secondSemester + 1) {
        recommendations.push({
            icon: '🎯',
            title: 'Address Your Declining Performance',
            description: 'Your grades dropped in the second semester. Identify what changed - are you facing new challenges? Seek help early.',
            priority: 'high'
        });
    }
    
    // Tuition recommendations
    if (data.tuitionUpToDate === 'no') {
        recommendations.push({
            icon: '💰',
            title: 'Resolve Tuition Issues Urgently',
            description: 'Outstanding tuition can lead to enrollment holds. Contact the financial aid office immediately to explore payment plans, scholarships, or emergency grants.',
            priority: 'high'
        });
    }
    
    // Age-based recommendations
    const age = parseFloat(data.enrollmentAge) || 0;
    if (age < 18) {
        recommendations.push({
            icon: '👥',
            title: 'Seek Additional Support Systems',
            description: 'As a younger student, connect with academic advisors regularly and consider finding a mentor to navigate college life.',
            priority: 'medium'
        });
    } else if (age > 25) {
        recommendations.push({
            icon: '👥',
            title: 'Connect with Non-Traditional Student Resources',
            description: 'Many universities have resources specifically for adult learners. Join support groups to balance education with other life responsibilities.',
            priority: 'medium'
        });
    }
    
    // Displaced status
    if (data.displaced === 'yes') {
        recommendations.push({
            icon: '❤️',
            title: 'Access Mental Health and Support Services',
            description: 'Displacement can be traumatic. Utilize counseling services, connect with student support programs, and don\'t hesitate to ask for accommodations.',
            priority: 'high'
        });
    }
    
    // Special needs
    if (data.specialNeeds === 'yes') {
        recommendations.push({
            icon: '💡',
            title: 'Utilize Disability Services',
            description: 'Register with your institution\'s disability services office to access accommodations, assistive technology, and specialized support.',
            priority: 'high'
        });
    }
    
    // International student
    if (data.studentType === 'international') {
        recommendations.push({
            icon: '👥',
            title: 'Engage with International Student Services',
            description: 'Connect with international student offices for visa support, cultural adjustment resources, and networking opportunities.',
            priority: 'medium'
        });
    }
    
    // Marital status
    if (data.maritalStatus !== 'single') {
        recommendations.push({
            icon: '❤️',
            title: 'Balance Family and Academic Commitments',
            description: 'Communicate with your family about study needs, establish clear boundaries for study time, and explore family-friendly campus resources.',
            priority: 'medium'
        });
    }
    
    // Previous qualification
    if (data.previousQualification === 'high-school' || data.previousQualification === 'vocational') {
        recommendations.push({
            icon: '📚',
            title: 'Build Strong Academic Foundations',
            description: 'As this may be your first university experience, take advantage of academic skills workshops, writing centers, and foundational courses.',
            priority: 'medium'
        });
    }
    
    // General recommendations
    if (outcome === 'Drop Out' || outcome === 'Remain Enrolled') {
        recommendations.push({
            icon: '🎯',
            title: 'Create a Structured Study Schedule',
            description: 'Develop a weekly schedule that includes dedicated study blocks for each course, breaks, and personal time. Stick to it consistently.',
            priority: 'high'
        });
    }
    
    // Display recommendations
    displayRecommendationsPage(recommendations);
}

// Display Recommendations Page
function displayRecommendationsPage(recommendations) {
    const highPriority = recommendations.filter(r => r.priority === 'high');
    const mediumPriority = recommendations.filter(r => r.priority === 'medium');
    
    // Outcome alert
    const outcomeAlert = document.getElementById('outcome-alert');
    let alertHTML = '';
    
    if (predictionResult.outcome === 'Graduate') {
        alertHTML = `
            <div class="card alert-box success">
                <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 14l9-5-9-5-9 5 9 5z"/>
                </svg>
                <div>
                    <h3>You're on the Right Track!</h3>
                    <p>Your current performance and circumstances indicate strong potential for graduation. 
                    The recommendations below will help you maintain your success and potentially achieve even greater outcomes.</p>
                </div>
            </div>
        `;
    } else if (predictionResult.outcome === 'Drop Out') {
        alertHTML = `
            <div class="card alert-box danger">
                <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
                <div>
                    <h3>Immediate Action Required</h3>
                    <p>Based on your responses, there are serious concerns about your academic progress. 
                    However, it's not too late to turn things around. Focus on the high-priority recommendations below.</p>
                </div>
            </div>
        `;
    }
    outcomeAlert.innerHTML = alertHTML;
    
    // High priority recommendations
    const highPrioritySection = document.getElementById('high-priority-recs');
    if (highPriority.length > 0) {
        let html = '<div class="recommendations-section"><h2>High Priority Actions</h2><div class="rec-grid">';
        highPriority.forEach(rec => {
            html += `
                <div class="card rec-card high">
                    <div class="card-header">
                        <span style="font-size: 1.5rem;">${rec.icon}</span>
                        <h3>${rec.title}</h3>
                    </div>
                    <div class="card-content">
                        <p>${rec.description}</p>
                    </div>
                </div>
            `;
        });
        html += '</div></div>';
        highPrioritySection.innerHTML = html;
    } else {
        highPrioritySection.innerHTML = '';
    }
    
    // Medium priority recommendations
    const mediumPrioritySection = document.getElementById('medium-priority-recs');
    if (mediumPriority.length > 0) {
        let html = '<div class="recommendations-section"><h2>Additional Recommendations</h2><div class="rec-grid">';
        mediumPriority.forEach(rec => {
            html += `
                <div class="card rec-card medium">
                    <div class="card-header">
                        <span style="font-size: 1.5rem;">${rec.icon}</span>
                        <h3>${rec.title}</h3>
                    </div>
                    <div class="card-content">
                        <p>${rec.description}</p>
                    </div>
                </div>
            `;
        });
        html += '</div></div>';
        mediumPrioritySection.innerHTML = html;
    } else {
        mediumPrioritySection.innerHTML = '';
    }
}

// Initialize - Show home page on load
window.addEventListener('DOMContentLoaded', function() {
    navigateTo('home');
});
