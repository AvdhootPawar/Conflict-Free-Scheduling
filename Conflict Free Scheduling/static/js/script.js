/**
 * Schedule Master - Main JavaScript File
 * Handles dynamic form updates and global UI functions like Tabs
 */

// ==========================================
// Tab Functionality (Now Global)
// ==========================================
function openTab(event, tabId) {
    const tabContents = document.getElementsByClassName('tab-content');
    if (tabContents) {
        for (let i = 0; i < tabContents.length; i++) {
            if (tabContents[i]) {
                tabContents[i].classList.remove('active');
            }
        }
    }

    const tabLinks = document.getElementsByClassName('tab-link');
    if (tabLinks) {
        for (let i = 0; i < tabLinks.length; i++) {
            if (tabLinks[i]) {
                tabLinks[i].classList.remove('active');
            }
        }
    }

    const selectedTab = document.getElementById(tabId);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }

    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    } else {
        const links = document.querySelectorAll(`.tab-link[onclick*="'${tabId}'"]`);
        if (links && links.length > 0) {
            links[0].classList.add('active');
        }
    }
}

// ==========================================
// Dynamic Form Field Generators
// ==========================================

// Subject Fields
window.updateSubjectFields = function() {
    const numSubjectsInput = document.getElementById('num_subjects');
    const container = document.getElementById('subjectContainer');

    if (!numSubjectsInput || !container) return;

    const numSubjects = parseInt(numSubjectsInput.value) || 0;
    container.innerHTML = '';

    for (let i = 0; i < numSubjects; i++) {
        const subjectGroup = document.createElement('div');
        subjectGroup.className = 'subject-item';

        subjectGroup.innerHTML = `
            <div class="form-group">
                <label for="subject_${i}">Subject ${i+1} Name:</label>
                <input type="text" id="subject_${i}" name="subject_${i}" class="form-control" required placeholder="Enter Subject Name">
            </div>
            <div class="form-group">
                <label for="faculty_${i}">Faculty Name:</label>
                <input type="text" id="faculty_${i}" name="faculty_${i}" class="form-control" required placeholder="Enter Faculty Name">
            </div>
        `;

        container.appendChild(subjectGroup);
    }
};

// Club Fields
window.updateClubFields = function() {
    const numClubsInput = document.getElementById('num_clubs');
    const container = document.getElementById('clubContainer');

    if (!numClubsInput || !container) return;

    const numClubs = parseInt(numClubsInput.value) || 0;
    container.innerHTML = '';

    for (let i = 0; i < numClubs; i++) {
        const clubItem = document.createElement('div');
        clubItem.className = 'form-group club-item';

        clubItem.innerHTML = `
            <label for="club_${i}">Club ${i+1} Name:</label>
            <input type="text" id="club_${i}" name="club_${i}" class="form-control" required placeholder="Enter Club Name">
        `;

        container.appendChild(clubItem);
    }
};

// Venue Fields
window.updateVenueFields = function() {
    const numVenuesInput = document.getElementById('num_venues');
    const container = document.getElementById('venueContainer');

    if (!numVenuesInput || !container) return;

    const numVenues = parseInt(numVenuesInput.value) || 0;
    container.innerHTML = '';

    for (let i = 0; i < numVenues; i++) {
        const venueItem = document.createElement('div');
        venueItem.className = 'form-group venue-item';

        venueItem.innerHTML = `
            <label for="venue_${i}">Venue ${i+1} Name:</label>
            <input type="text" id="venue_${i}" name="venue_${i}" class="form-control" required placeholder="Enter Venue Name">
        `;

        container.appendChild(venueItem);
    }
};

// ==========================================
// DOMContentLoaded Listener
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    const academicYearSelect = document.getElementById('academic_year');
    if (academicYearSelect) {
        academicYearSelect.addEventListener('change', function() {
            const year = parseInt(this.value);
            const defaultTimes = {
                1: "08:00",
                2: "09:00",
                3: "09:00",
                4: "10:00"
            };
            const startTimeField = document.getElementById('start_time');
            if (startTimeField) {
                startTimeField.value = defaultTimes[year] || "09:00";
            }
        });
        academicYearSelect.dispatchEvent(new Event('change'));
    }

    if (typeof window.updateSubjectFields === 'function' && document.getElementById('subjectContainer')) {
        window.updateSubjectFields();
    }
    if (typeof window.updateClubFields === 'function' && document.getElementById('clubContainer')) {
        window.updateClubFields();
    }
    if (typeof window.updateVenueFields === 'function' && document.getElementById('venueContainer')) {
        window.updateVenueFields();
    }
});
