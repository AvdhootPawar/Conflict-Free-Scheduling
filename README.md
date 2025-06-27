# Conflict-Free Scheduling System  
**Academic Timetable Generator and Club Event Scheduler**

This project is a comprehensive scheduling tool designed to assist academic institutions in generating structured, conflict-free timetables for both classroom instruction and extracurricular club activities. It features intelligent logic, customizable inputs, and multi-format output capabilities to meet diverse scheduling requirements.

---

## Core Functionalities

### Academic Timetable Generator
- Generates weekly class schedules based on configurable inputs.
- Supports different types of sessions: theory lectures, labs, and tutorials with varied durations.
- Balances faculty workload throughout the week.
- Automatically inserts breaks based on consecutive teaching hours.

**Customizable Parameters:**
- Number of working days
- Start and end times
- Weekly lecture frequency per subject
- Subject-faculty assignments
- Lecture types and durations

### Club Event Scheduler
- Organizes club events across multiple venues and days.
- Ensures no overlapping events for any club or venue.
- Distributes events evenly across available slots.

**Customizable Parameters:**
- Number of clubs and venues
- Event duration and events per club
- Daily time slots

---

## Key Features

### Intelligent Scheduling Algorithms
- Allocates time slots to minimize conflicts and maximize balance.
- Applies progressive difficulty reduction strategies.
- Includes safety checks to prevent infinite loops and deadlocks.

### Multi-Format Output
- Web view with dynamically generated tables
- Downloadable CSV files for spreadsheet compatibility
- Professionally formatted PDFs for print or documentation

### Error Handling
- Validates all user inputs for correctness
- Detects and handles scheduling conflicts gracefully
- Provides meaningful error messages to guide corrections

---

## Technical Implementation

### Backend
- Developed using the Flask web framework (Python)
- Custom scheduling logic with time slot and conflict management
- Utilizes randomization for varied yet valid schedules

### Frontend
- HTML templates with responsive design and clean user interface
- Form validation for input consistency
- Real-time rendering of generated schedules

### Export Capabilities
- CSV export using Python's built-in `csv` module
- PDF export using the `ReportLab` library
- Base64 encoding for in-browser file downloads

---

## Architectural Highlights

### Time Management
- Handles string-time conversions
- Calculates custom durations
- Supports overnight scheduling cases

### Data Structures
- Uses dictionaries for day-wise scheduling
- Lists for ordered time slot management
- Object-oriented representations for scheduled items

### Scheduling Logic
- Multi-pass algorithm for optimal slot placement
- Escalating fallback strategies
- Configurable constraints and safety limits

---
## Screenshots

### 1. Main Page
![Screenshot 2025-06-26 201142](https://github.com/user-attachments/assets/f481bf9f-9b8b-4e7b-8d7d-4f6e70974cd4)
![Screenshot 2025-06-27 121210](https://github.com/user-attachments/assets/adedeb37-7b1e-4acb-a687-d0ce6c80fa24)

### 2. Input Section
![Screenshot 2025-06-27 121509](https://github.com/user-attachments/assets/f1ca3f89-6a8e-4cfe-bb08-4aca247128fb)
![Screenshot 2025-06-27 121531](https://github.com/user-attachments/assets/0f1672af-a1e3-4823-ad50-938e42fb3ecd)

### 3. Output - Academic Timetable
![Screenshot 2025-06-27 121603](https://github.com/user-attachments/assets/f2bab835-e2cb-4f33-bd8c-89944b618aac)





