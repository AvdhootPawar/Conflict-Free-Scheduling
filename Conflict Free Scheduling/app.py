from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta, time
import random
import csv
import io
import base64
import json
import traceback
import math # Import math for ceiling function

# --- PDF Generation (Basic using ReportLab) ---
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
# --- End PDF Generation ---

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_here_CHANGE_ME' # Change this!

# --- Helper Functions (remain the same) ---
def format_time(dt_time):
    return dt_time.strftime("%H:%M")

def add_hours_to_time(t, hours_to_add):
    start_dt = datetime.combine(datetime.min, t) # Use datetime.min for date part
    end_dt = start_dt + timedelta(hours=hours_to_add)
    return end_dt.time()

def generate_time_slots(start_time_str, slots_per_day, event_duration_hours):
    slots = []
    try:
        current_time = datetime.strptime(start_time_str, "%H:%M").time()
        for _ in range(int(slots_per_day)): # Ensure integer
            end_time = add_hours_to_time(current_time, event_duration_hours)
            slots.append((format_time(current_time), format_time(end_time)))
            current_time = end_time
            # Safety break if time calculation goes wrong (e.g., duration is 0)
            if _ > 0 and slots[-1] == slots[-2]: break
    except ValueError:
        print(f"Error parsing start time: {start_time_str}")
    return slots

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/academic_timetable', methods=['GET', 'POST'])
def academic_timetable():
    if request.method == 'POST':
        try:
            # --- Extract Data (same as before) ---
            academic_year = request.form.get('academic_year', '1')
            start_time_str = request.form.get('start_time', '08:00')
            working_days = int(request.form.get('working_days', 5))
            num_subjects = int(request.form.get('num_subjects', 5))
            theory_duration = float(request.form.get('theory_duration', 1.0))
            lab_duration = float(request.form.get('lab_duration', 2.0))
            tutorial_duration = float(request.form.get('tutorial_duration', 1.0))
            theory_per_week = int(request.form.get('theory_lectures', 2))
            lab_per_week = int(request.form.get('lab_lectures', 1))
            tutorial_per_week = int(request.form.get('tutorial_lectures', 1))
            break_duration = float(request.form.get('break_duration', 0.5))
            subjects = [request.form.get(f'subject_{i}', f'Subject {i+1}') for i in range(num_subjects)]
            faculties = [request.form.get(f'faculty_{i}', f'Prof. {chr(65+i)}') for i in range(num_subjects)]

            all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            days = all_days[:working_days]
            start_time_obj = datetime.strptime(start_time_str, "%H:%M").time()
            end_of_day_time = time(17, 0) # Example: 5 PM cutoff

            # --- New Scheduling Logic ---
            timetable_data = []
            scheduled_periods_by_day = {day: [] for day in days} # Tracks {'start': time, 'end': time}

            # 1. Create list of all class sessions needed for the week
            class_requests = []
            for i in range(num_subjects):
                subj = subjects[i]
                fac = faculties[i]
                class_requests.extend([{'type': 'Theory', 'duration': theory_duration, 'subject': subj, 'faculty': fac}] * theory_per_week)
                class_requests.extend([{'type': 'Lab', 'duration': lab_duration, 'subject': subj, 'faculty': fac}] * lab_per_week)
                class_requests.extend([{'type': 'Tutorial', 'duration': tutorial_duration, 'subject': subj, 'faculty': fac}] * tutorial_per_week)

            random.shuffle(class_requests) # Shuffle for variety

            # 2. Distribute classes across days
            day_cursors = {day: {'current_time': start_time_obj, 'consecutive_hours': 0.0, 'periods_today': 0} for day in days}
            max_periods_per_day = 6 # Limit to avoid packing days too much (adjust as needed)
            passes = 0
            max_passes = len(days) * 2 # Safety break for loop

            while class_requests and passes < max_passes:
                request_scheduled_this_pass = False
                for day in days:
                    if not class_requests: break # Exit if all scheduled

                    cursor = day_cursors[day]
                    current_time = cursor['current_time']
                    consecutive_hours = cursor['consecutive_hours']

                    # Check if day is already full for reasonable load or past end time
                    if cursor['periods_today'] >= max_periods_per_day or current_time >= end_of_day_time:
                        continue

                    # Potential candidate class
                    potential_request = class_requests[0]
                    potential_duration = potential_request['duration']

                    # Check for mandatory break *before* scheduling next class
                    break_needed = (consecutive_hours + potential_duration > 3.0) and consecutive_hours > 0 # Need > 0 to avoid break at start
                    break_inserted = False
                    if break_needed:
                        break_start_time = current_time
                        break_end_time = add_hours_to_time(break_start_time, break_duration)
                        # Check if break fits within day and doesn't overlap
                        if break_end_time < end_of_day_time:
                             is_overlap = any(p['start'] < break_end_time and p['end'] > break_start_time for p in scheduled_periods_by_day[day])
                             if not is_overlap:
                                timetable_data.append({
                                    "Day": day, "Start Time": format_time(break_start_time), "End Time": format_time(break_end_time),
                                    "Subject": "Break", "Faculty": "-"
                                })
                                scheduled_periods_by_day[day].append({'start': break_start_time, 'end': break_end_time})
                                current_time = break_end_time # Update current time
                                consecutive_hours = 0.0    # Reset consecutive hours
                                cursor['periods_today'] += 1 # Count break as a "period" for daily limit? Optional.
                                break_inserted = True
                             # else: cannot fit break here, will try next day/pass

                    # If break was inserted, update cursor and continue day check if needed
                    if break_inserted:
                        cursor['current_time'] = current_time
                        cursor['consecutive_hours'] = consecutive_hours
                        # If day is now full after break, skip to next day
                        if cursor['periods_today'] >= max_periods_per_day or current_time >= end_of_day_time:
                            continue

                    # Try scheduling the actual class request
                    class_start_time = current_time # Use potentially updated time after break
                    class_end_time = add_hours_to_time(class_start_time, potential_duration)

                    if class_end_time <= end_of_day_time:
                        is_overlap = any(p['start'] < class_end_time and p['end'] > class_start_time for p in scheduled_periods_by_day[day])
                        if not is_overlap:
                            # Schedule it!
                            scheduled_class = class_requests.pop(0) # Remove from list
                            timetable_data.append({
                                "Day": day, "Start Time": format_time(class_start_time), "End Time": format_time(class_end_time),
                                "Subject": f"{scheduled_class['subject']} ({scheduled_class['type']})", "Faculty": scheduled_class['faculty']
                            })
                            scheduled_periods_by_day[day].append({'start': class_start_time, 'end': class_end_time})

                            # Update day cursor state
                            cursor['current_time'] = class_end_time
                            cursor['consecutive_hours'] = consecutive_hours + potential_duration # Update consecutive hours
                            cursor['periods_today'] += 1
                            request_scheduled_this_pass = True
                        # else: Cannot fit class due to overlap, will try next day/pass

                passes += 1
                # If no request was scheduled in a full pass through all days, something is wrong (stuck)
                if not request_scheduled_this_pass and class_requests:
                    print(f"Warning: No classes scheduled in pass {passes}. Possible scheduling conflict or issue. Remaining: {len(class_requests)}")
                    # Optional: Implement more advanced conflict resolution or break loop
                    if passes > max_passes // 2: # Break early if stuck for multiple passes
                         break


            # --- Final Steps ---
            if class_requests:
                print(f"Warning: Could not schedule {len(class_requests)} class requests. Check constraints.")
                # Consider adding error to template

            timetable_data.sort(key=lambda x: (all_days.index(x["Day"]), x["Start Time"]))

            return render_template('result.html',
                                  result_type='timetable', academic_year=academic_year, mode="Balanced",
                                  title=f"Academic Timetable - Year {academic_year}", days=days, data=timetable_data)

        except ValueError as ve:
            # ... (error handling as before) ...
            print(f"Value Error: {ve}")
            traceback.print_exc()
            return render_template('timetable.html', error=f"Invalid input: Please check number formats (e.g., durations, lectures per week). {ve}")
        except Exception as e:
            # ... (error handling as before) ...
            print(f"Error generating timetable: {e}")
            traceback.print_exc()
            return render_template('timetable.html', error=f"An unexpected error occurred: {str(e)}. Please check your inputs or contact support.")

    # GET request
    return render_template('timetable.html', error=None)


@app.route('/club_scheduler', methods=['GET', 'POST'])
def club_scheduler():
    if request.method == 'POST':
        try:
            # --- Extract Data (same as before) ---
            num_clubs = int(request.form.get('num_clubs', 0))
            num_venues = int(request.form.get('num_venues', 0))
            num_days = int(request.form.get('num_days', 1))
            slots_per_day = int(request.form.get('slots_per_day', 1))
            event_duration = float(request.form.get('event_duration', 1.0))
            start_time_str = request.form.get('start_time', '09:00')
            events_per_club = int(request.form.get('events_per_club', 1))
            clubs = [request.form.get(f'club_{i}', f'Club {i+1}') for i in range(num_clubs)]
            venues = [request.form.get(f'venue_{i}', f'Venue {i+1}') for i in range(num_venues)]

            # --- Validation (same as before) ---
            if num_clubs <= 0 or num_venues <= 0 or num_days <= 0 or slots_per_day <= 0 or event_duration <= 0 or events_per_club <= 0:
                raise ValueError("Counts must be positive.")
            if not all(clubs) or not all(venues):
                 raise ValueError("Club and Venue names cannot be empty.")

            # --- New Scheduling Logic ---
            schedule_data = []
            day_names = [f"Day {i+1}" for i in range(num_days)]

            # 1. Generate all available slots with state
            available_slots = []
            daily_time_slots = generate_time_slots(start_time_str, slots_per_day, event_duration)
            for day in day_names:
                for venue in venues:
                    for start_t, end_t in daily_time_slots:
                        available_slots.append({
                            "Day": day, "Venue": venue, "Start Time": start_t, "End Time": end_t,
                            "Occupied": False, "OccupyingClub": None
                        })

            # 2. Generate event requests
            events_needed = []
            for club in clubs:
                for i in range(events_per_club):
                    events_needed.append({"Club": club, "EventNum": i+1})

            random.shuffle(events_needed)

            # 3. Assign events, trying to balance across days
            events_scheduled_per_day = {day: 0 for day in day_names}
            total_events_to_schedule = len(events_needed)
            target_per_day = math.ceil(total_events_to_schedule / num_days) if num_days > 0 else total_events_to_schedule
            print(f"Target events per day (approx): {target_per_day}")

            unscheduled_events = []
            scheduled_count = 0
            passes = 0
            max_passes = 3 # Allow a few passes to fill remaining slots

            current_events_list = list(events_needed) # Work with a copy

            while current_events_list and passes < max_passes:
                print(f"--- Scheduling Pass {passes + 1} ---")
                remaining_after_pass = []
                pass_scheduled_count = 0

                for event in current_events_list:
                    assigned = False
                    # Separate slots by day preference
                    preferred_slots = []
                    other_slots = []

                    random.shuffle(available_slots) # Shuffle slots within the pass

                    for slot in available_slots:
                        if not slot["Occupied"]:
                             # Check club conflict at this specific time slot across all venues
                             is_club_busy = any(
                                s["OccupyingClub"] == event["Club"] and s["Day"] == slot["Day"] and s["Start Time"] == slot["Start Time"]
                                for s in available_slots if s["Occupied"]
                             )
                             if not is_club_busy:
                                # Prioritize days below target only on the first pass
                                if passes == 0 and events_scheduled_per_day.get(slot["Day"], 0) < target_per_day:
                                    preferred_slots.append(slot)
                                else:
                                    other_slots.append(slot)

                    # Try preferred slots first, then others
                    for slot_to_try in preferred_slots + other_slots:
                        # Re-check occupancy just in case (though unlikely needed with this structure)
                        if not slot_to_try["Occupied"]:
                             # Check club conflict again (safer)
                             is_club_busy = any(
                                s["OccupyingClub"] == event["Club"] and s["Day"] == slot_to_try["Day"] and s["Start Time"] == slot_to_try["Start Time"]
                                for s in available_slots if s["Occupied"]
                             )
                             if not is_club_busy:
                                slot_to_try["Occupied"] = True
                                slot_to_try["OccupyingClub"] = event["Club"]
                                schedule_data.append({
                                    "Day": slot_to_try["Day"], "Start Time": slot_to_try["Start Time"], "End Time": slot_to_try["End Time"],
                                    "Club": event["Club"], "Venue": slot_to_try["Venue"]
                                })
                                events_scheduled_per_day[slot_to_try["Day"]] = events_scheduled_per_day.get(slot_to_try["Day"], 0) + 1
                                scheduled_count += 1
                                pass_scheduled_count += 1
                                assigned = True
                                break # Event assigned, move to next event

                    if not assigned:
                        remaining_after_pass.append(event) # Keep unassigned for next pass

                current_events_list = remaining_after_pass # Update list for next pass
                passes += 1
                if pass_scheduled_count == 0 and current_events_list:
                     print(f"Warning: No events scheduled in pass {passes}. Stopping.")
                     break # Stop if a pass yields no results

            unscheduled_events = current_events_list # Final remaining list

            # --- Post-Scheduling Checks ---
            if unscheduled_events:
                 warning_message = f"Warning: Could only schedule {scheduled_count} out of {total_events_to_schedule} events. {len(unscheduled_events)} could not be placed."
                 print(warning_message)
                 # Pass warning to template if desired

            # --- Final Steps ---
            schedule_data.sort(key=lambda x: (int(x["Day"].split(" ")[1]), x["Start Time"]))

            return render_template('result.html',
                                   result_type='club', title="Generated Club Event Schedule (Balanced)",
                                   days=day_names, data=schedule_data)

        except ValueError as ve:
             # ... (error handling as before) ...
            print(f"Value Error: {ve}")
            traceback.print_exc()
            return render_template('clubs.html', error=f"Invalid input: {str(ve)}")
        except Exception as e:
             # ... (error handling as before) ...
            print(f"Error generating club schedule: {e}")
            traceback.print_exc()
            return render_template('clubs.html', error=f"An unexpected error occurred: {str(e)}. Please check inputs.")

    # GET request
    return render_template('clubs.html', error=None)


# --- Download Endpoints (remain the same as the corrected version) ---

@app.route('/download_csv', methods=['POST'])
def download_csv():
    try:
        payload = request.get_json()
        if not payload:
             return jsonify({'success': False, 'error': 'No JSON payload received.'}), 400
        schedule_data = payload.get('data')
        if schedule_data is None:
            return jsonify({'success': False, 'error': 'Missing "data" key in JSON payload.'}), 400
        if not isinstance(schedule_data, list):
            if not schedule_data: schedule_data = []
            else: return jsonify({'success': False, 'error': 'Value for "data" key is not a list.'}), 400

        output = io.StringIO()
        writer = csv.writer(output)
        if schedule_data:
            headers = schedule_data[0].keys()
            writer.writerow(headers)
            for row_dict in schedule_data:
                writer.writerow([str(row_dict.get(h, '')) for h in headers])
        else:
             writer.writerow(["No Data Available"])
        csv_data = output.getvalue()
        output.close()
        return jsonify({'success': True, 'data': csv_data})
    except Exception as e:
        print(f"Error generating CSV: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Failed to generate CSV: {str(e)}'}), 500


@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    try:
        payload = request.get_json()
        if not payload:
             return jsonify({'success': False, 'error': 'No JSON payload received.'}), 400
        schedule_data = payload.get('data')
        title = payload.get('title', 'Schedule')
        result_type = payload.get('type', 'timetable')
        if schedule_data is None:
            return jsonify({'success': False, 'error': 'Missing "data" key in JSON payload.'}), 400
        if not isinstance(schedule_data, list):
            if not schedule_data: schedule_data = []
            else: return jsonify({'success': False, 'error': 'PDF data value is not a list.'}), 400

        # --- PDF Generation Logic (same as before) ---
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph(title, styles['h1']))
        story.append(Spacer(1, 0.2*inch))
        data_by_day = {}
        days_ordered = []
        for item in schedule_data:
            day = item.get('Day')
            if day is None: continue
            if day not in data_by_day:
                data_by_day[day] = []
                days_ordered.append(day)
            data_by_day[day].append(item)
        if result_type == 'timetable':
            headers = ['Start Time', 'End Time', 'Subject', 'Faculty']
            data_keys = ['Start Time', 'End Time', 'Subject', 'Faculty']
            colWidths = [1.5*inch, 1.5*inch, 3*inch, 3*inch]
        else:
            headers = ['Start Time', 'End Time', 'Club', 'Venue']
            data_keys = ['Start Time', 'End Time', 'Club', 'Venue']
            colWidths = [1.5*inch, 1.5*inch, 3*inch, 3*inch]
        try:
            if result_type == 'timetable':
                all_days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                days_ordered.sort(key=lambda d: all_days_order.index(d) if d in all_days_order else 99)
            else:
                days_ordered.sort(key=lambda d: int(d.split(" ")[1]) if d and d.startswith("Day ") and len(d.split(" ")) > 1 and d.split(" ")[1].isdigit() else 99)
        except Exception as sort_e:
             print(f"Warning: Could not sort days - {sort_e}")
        for day in days_ordered:
            story.append(Paragraph(f"<b>{day}</b>", styles['h3']))
            story.append(Spacer(1, 0.1*inch))
            table_data = [headers]
            day_items = sorted(data_by_day.get(day, []), key=lambda x: x.get('Start Time', ''))
            for item in day_items:
                row = [str(item.get(key, 'N/A')) for key in data_keys]
                table_data.append(row)
            if len(table_data) > 1:
                 table = Table(table_data, colWidths=colWidths)
                 table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))
                 story.append(table)
                 story.append(Spacer(1, 0.2*inch))
            else:
                story.append(Paragraph("No events scheduled for this day.", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        return jsonify({'success': True, 'data': pdf_base64})

    except Exception as e:
        print(f"Error generating PDF: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Failed to generate PDF: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True)