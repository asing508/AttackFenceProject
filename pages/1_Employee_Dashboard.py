import streamlit as st
import mysql.connector as connector
import datetime
import uuid
from notifications import notification_bell_component, add_notification
from core.auth import protect_page, render_logout_button, get_db_connection, get_token_store
from core.constants import (
    foundational_criteria,
    futuristic_criteria,
    development_criteria,
    other_aspects_criteria,
    all_criteria_names
)

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Employee Dashboard", page_icon="👤", layout="wide")

protect_page(allowed_roles=["employee"]) 

db = get_db_connection()
token_store = get_token_store()

name = st.session_state["name"]
role = st.session_state["role"]
cursor = db.cursor()

notification_bell_component(st.session_state.name)

# --- EMPLOYEE DASHBOARD UI ---
st.title("Employee Dashboard 👤")
st.write("---")
st.write(f"<center><h2>Welcome {name}!</h2></center>", unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

# Show ratings given to the employee by others
st.subheader("Ratings Received")
# Fetch all ratings for the employee
cursor.execute("""
    SELECT rater, role, criteria, score, rating_type, timestamp
    FROM user_ratings
    WHERE ratee = %s
    ORDER BY timestamp DESC
""", (name,))
ratings = cursor.fetchall()

# Separate ratings by admin and manager
admin_ratings = [r for r in ratings if r[4] == "admin"]
manager_ratings = [r for r in ratings if r[4] == "manager"]

foundational_criteria = ["Humility", "Integrity", "Collegiality", "Attitude", "Time Management", "Initiative", "Communication", "Compassion"]
futuristic_criteria = ["Knowledge & Awareness", "Future readiness", "Informal leadership", "Team Development", "Process adherence"]

# Manager Ratings/Remarks Dropdown (Changed from "Ratings" to "Remarks" as per requirements)
with st.expander("👔 Manager Remarks", expanded=False):
    development_criteria = [
        "Quality of Work", "Task Completion", "Timeline Adherence"
    ]
    other_aspects_criteria = [
        "Collaboration", "Innovation", "Special Situation"
    ]
    foundational_criteria = ["Humility", "Integrity", "Collegiality", "Attitude", "Time Management", "Initiative", "Communication", "Compassion"]
    futuristic_criteria = ["Knowledge & Awareness", "Future readiness", "Informal leadership", "Team Development", "Process adherence"]

    if manager_ratings:
        ratings_by_criteria = {r[2]: (r[3], r[5], r[0], r[1]) for r in manager_ratings}

        rater_name = manager_ratings[0][0]
        submission_date = manager_ratings[0][5]
        st.write(f"**Submitted by:** {rater_name} on {submission_date.strftime('%B %d, %Y')}")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h3>Development (70%)</h3>", unsafe_allow_html=True)
            for crit in development_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp, rater, r_role = ratings_by_criteria[crit]
                    st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)
            
            st.markdown("<h3>Foundational Progress</h3>", unsafe_allow_html=True)
            for crit in foundational_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp, rater, r_role = ratings_by_criteria[crit]
                    st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)

        with col2:
            st.markdown("<h3>Other Aspects (30%)</h3>", unsafe_allow_html=True)
            for crit in other_aspects_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp, rater, r_role = ratings_by_criteria[crit]
                    st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)

            st.markdown("<h3>Futuristic Progress</h3>", unsafe_allow_html=True)
            for crit in futuristic_criteria:
                if crit in ratings_by_criteria:
                    score, timestamp, rater, r_role = ratings_by_criteria[crit]
                    st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)
        # --- END OF MISSING LOGIC ---
        
        st.divider()
        cursor.execute("SELECT remark FROM remarks WHERE ratee = %s AND rating_type = 'manager';", (name, ))
        feedback = cursor.fetchone()
        st.subheader("Remark:")
        if feedback:
            st.write(feedback[0])
        else:
            st.write("No remarks found.")
    else:
        st.info("No manager remarks received yet.")

# Employee self-rating form
st.write("---")
st.subheader("Submit Your Self-Evaluation")
with st.expander("Open Self-Evaluation Form", expanded=False):
    # Your existing, detailed self-rating form logic goes here.
    # This includes checking if already submitted, showing sliders, and the submit button.
    # All of this is copied directly from your original file's "employee" section.
    # ...
    # (The full self-rating form code from your file is assumed here)
    # ...
    # Self-rating form in an expander (dropdown style)
    cursor.execute("""
        SELECT criteria, score, timestamp FROM user_ratings
        WHERE rater = %s AND ratee = %s AND rating_type = 'self'
        ORDER BY timestamp DESC
    """, (name, name))
    self_ratings = cursor.fetchall()
    
    foundational_criteria = [
        ("Humility", 12.5),
        ("Integrity", 12.5),
        ("Collegiality", 12.5),
        ("Attitude", 12.5),
        ("Time Management", 12.5),
        ("Initiative", 12.5),
        ("Communication", 12.5),
        ("Compassion", 12.5),
    ]
    futuristic_criteria = [
        ("Knowledge & Awareness", 20),
        ("Future readiness", 20),
        ("Informal leadership", 20),
        ("Team Development", 20),
        ("Process adherence", 20),
    ]
    development_criteria = [
        ("Quality of Work", 28),
        ("Task Completion", 14),
        ("Timeline Adherence", 28),
    ]
    other_aspects_criteria = [
        ("Collaboration", 10),
        ("Innovation", 10),
        ("Special Situation", 10),
    ]

    all_criteria = [crit for crit, _ in development_criteria + other_aspects_criteria + foundational_criteria + futuristic_criteria]
    submitted_criteria = set([crit for crit, _, _ in self_ratings])
    
    if set(all_criteria).issubset(submitted_criteria):
        st.info("You have already submitted your self-rating.")

        # ADD THIS BLOCK to show the date once
        if self_ratings:
            # Get the timestamp from the first record (they should all be the same)
            submission_date = self_ratings[0][2]
            st.write(f"**Submitted on:** {submission_date.strftime('%B %d, %Y')}")

        # Create columns for the summary view
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Development (70%)")
            for crit, _ in development_criteria:
                score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)
            
            st.markdown("### Foundational Progress")
            for crit, _ in foundational_criteria:
                score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Other Aspects (30%)")
            for crit, _ in other_aspects_criteria:
                score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)

            st.markdown("### Futuristic Progress")
            for crit, _ in futuristic_criteria:
                score, timestamp = next((s, t) for c, s, t in self_ratings if c == crit)
                st.markdown(f"**{crit}**: {score}/10", unsafe_allow_html=True)

    else:
        # Dictionary to hold all scores
        all_scores = {}

        st.markdown("#### Development (70%)")
        for crit, weight in development_criteria:
            if crit not in submitted_criteria:
                all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_dev_self")
        
        st.markdown("#### Other Aspects (30%)")
        for crit, weight in other_aspects_criteria:
            if crit not in submitted_criteria:
                all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_other_self")

        st.markdown("#### Foundational Progress")
        for crit, weight in foundational_criteria:
            if crit not in submitted_criteria:
                all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_found_self")

        st.markdown("#### Futuristic Progress")
        for crit, weight in futuristic_criteria:
            if crit not in submitted_criteria:
                all_scores[crit] = st.slider(f"{crit} ({weight}%)", 0, 10, 0, key=f"{name}_{crit}_fut_self")
        
        @st.dialog("Confirmation")
        def self_submit():
            st.success("Your self-rating has been submitted.")
            if st.button("Close"):
                st.rerun()

        if all_scores and st.button("Submit Your Self-Rating"):
            # Check for already submitted criteria one last time to prevent duplicates
            cursor.execute("SELECT criteria FROM user_ratings WHERE rater = %s AND rating_type = 'self'", (name,))
            already_submitted = {row[0] for row in cursor.fetchall()}
            quarter = datetime.datetime.now().month // 3 + 1 if datetime.datetime.now().month % 3 != 0 else datetime.datetime.now().month // 3
            # Insert all new scores in a single loop
            for crit, score in all_scores.items():
                if crit not in already_submitted:
                    cursor.execute(
                        "INSERT INTO user_ratings (rater, ratee, role, criteria, score, rating_type, quarter) VALUES (%s, %s, %s, %s, %s, %s,%s)",
                        (name, name, role, crit, score, "self",quarter)
                    )
            db.commit()
            # --- ADD THIS NOTIFICATION LOGIC ---
            cursor.execute("SELECT managed_by FROM users WHERE username = %s", (name,))
            manager_name_result = cursor.fetchone()
            if manager_name_result and manager_name_result[0]:
                manager_name = manager_name_result[0]
                add_notification(
                    recipient=manager_name,
                    sender=name,
                    message=f"{name} has completed their self-evaluation. Please complete your review.",
                    notification_type='self_evaluation_completed'
                )
            # --- END OF NOTIFICATION LOGIC ---
            self_submit()
            st.rerun()

render_logout_button()
