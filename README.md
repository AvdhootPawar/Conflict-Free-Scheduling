Conflict-Free Scheduling System
Academic Timetable Generator and Club Event Scheduler

This project is a comprehensive scheduling tool designed to assist academic institutions in generating structured, conflict-free timetables for both classroom instruction and extracurricular club activities. It features intelligent logic, customizable inputs, and multi-format output capabilities to meet diverse scheduling requirements.

Core Functionalities
Academic Timetable Generator
Generates weekly class schedules based on configurable inputs.

Supports different types of sessions: theory lectures, labs, and tutorials with varied durations.

Balances faculty workload throughout the week.

Automatically inserts breaks based on consecutive teaching hours.

Customizable Parameters:

Number of working days.

Start and end times.

Weekly lecture frequency per subject.

Subject-faculty assignments.

Lecture types and durations.

Club Event Scheduler
Organizes club events across multiple venues and days.

Ensures no overlapping events for any club or venue.

Distributes events evenly across available slots.

Customizable Parameters:

Number of clubs and venues.

Event duration and events per club.

Daily time slots.

Key Features
Intelligent Scheduling Algorithms
Allocates time slots to minimize conflicts and maximize balance.

Applies progressive difficulty reduction strategies.

Includes safety checks to prevent infinite loops and deadlocks.

Multi-Format Output
Web view with dynamically generated tables.

Downloadable CSV files for spreadsheet compatibility.

Professionally formatted PDFs for print or documentation.

Error Handling
Validates all user inputs for correctness.

Detects and handles scheduling conflicts gracefully.

Provides meaningful error messages to guide corrections.

Technical Implementation
Backend
Developed using the Flask web framework (Python).

Custom scheduling logic with time slot and conflict management.

Utilizes randomization for varied yet valid schedules.

Frontend
HTML templates with responsive design and clean user interface.

Form validation for input consistency.

Real-time rendering of generated schedules.

Export Capabilities
CSV export using Python's built-in csv module.

PDF export using the ReportLab library.

Base64 encoding for in-browser file downloads.

Architectural Highlights
Time Management
Handles string-time conversions, calculates custom durations, and supports overnight slots.

Data Structures
Uses dictionaries for day-wise schedules, lists for ordered slot management, and object-oriented representations for scheduled items.

Scheduling Logic
Implements a multi-pass scheduling algorithm with configurable fallback options and constraint handling.
