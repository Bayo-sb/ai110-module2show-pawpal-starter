import streamlit as st

from datetime import time

from pawpal_system import (
    Frequency,
    Owner,
    Pet,
    Priority,
    Scheduler,
    Task,
    format_clock,
    parse_clock,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption(
    "A daily care planner for your pets. Add pets and tasks, then build a schedule "
    "that fits your day and flags any time conflicts."
)

st.divider()

st.subheader("Owner and Pets")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes_per_day=90)
owner = st.session_state.owner

owner_col, minutes_col = st.columns(2)
with owner_col:
    owner.name = st.text_input("Owner name", value=owner.name)
with minutes_col:
    owner.available_minutes_per_day = st.number_input(
        "Minutes available per day",
        min_value=0,
        max_value=1440,
        value=owner.available_minutes_per_day,
    )

pet_col, species_col = st.columns(2)
with pet_col:
    pet_name = st.text_input("Pet name", value="Mochi")
with species_col:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    try:
        owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added {pet_name} the {species}.")
    except ValueError as e:
        st.error(str(e))

if owner.pets:
    st.caption("Your pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))

st.divider()

st.subheader("Add a Task")

if not owner.pets:
    st.info("Add a pet first.")
else:
    target = st.selectbox("Pet", [p.name for p in owner.pets])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", [p.name for p in Priority], index=2)
    with col4:
        frequency = st.selectbox("Repeats", [f.value for f in Frequency])

    start_time = None
    if st.checkbox("Fixed start time"):
        start_time = st.time_input("Start time", value=time(8, 30), step=300).strftime("%H:%M")

    if st.button("Add task"):
        try:
            owner.get_pet(target).add_task(
                Task(
                    task_title,
                    int(duration),
                    Priority[priority],
                    Frequency(frequency),
                    scheduled_time=start_time,
                )
            )
            st.success(f"Added '{task_title}' for {target}.")
        except ValueError as e:
            st.error(str(e))

scheduler = Scheduler(owner)

st.divider()

st.subheader("Task List")

all_tasks = owner.get_all_tasks()
if all_tasks:
    total_col, pending_col, done_col = st.columns(3)
    total_col.metric("Total tasks", len(all_tasks))
    pending_col.metric("Pending", len(owner.filter_tasks(completed=False)))
    done_col.metric("Completed", len(owner.filter_tasks(completed=True)))

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        pet_filter = st.selectbox("Show pet", ["All"] + [p.name for p in owner.pets])
    with filter_col2:
        status_filter = st.selectbox("Show status", ["All", "Pending", "Completed"])

    shown = owner.filter_tasks(
        pet_name=None if pet_filter == "All" else pet_filter,
        completed={"All": None, "Pending": False, "Completed": True}[status_filter],
    )
    shown = scheduler.sort_by_time(shown)

    if shown:
        st.dataframe(
            [
                {
                    "Time": t.scheduled_time or "any time",
                    "Pet": t.pet_name,
                    "Task": t.title,
                    "Minutes": t.duration_minutes,
                    "Priority": t.priority.name.title(),
                    "Repeats": t.frequency.value,
                    "Done": t.completed,
                }
                for t in shown
            ],
            hide_index=True,
            column_config={"Done": st.column_config.CheckboxColumn("Done", disabled=True)},
        )
        st.caption(f"Showing {len(shown)} of {len(all_tasks)} tasks, sorted by time.")
    else:
        st.info("No tasks match these filters.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Today's Schedule")

if st.button("Generate schedule", type="primary"):
    plan = scheduler.generate_plan()
    free = owner.available_minutes_per_day - plan.total_minutes

    scheduled_col, planned_col, free_col, conflict_col = st.columns(4)
    scheduled_col.metric("Tasks scheduled", len(plan.scheduled))
    planned_col.metric("Minutes planned", plan.total_minutes)
    free_col.metric("Minutes free", free)
    conflict_col.metric("Conflicts", len(plan.warnings))

    if plan.warnings:
        for warning in plan.warnings:
            st.warning(warning)
    elif plan.scheduled:
        st.success("No scheduling conflicts.")

    if plan.scheduled:
        st.dataframe(
            [
                {
                    "Time": (
                        f"{item.start_time} - "
                        f"{format_clock(parse_clock(item.start_time) + item.task.duration_minutes)}"
                    ),
                    "Pet": item.pet_name,
                    "Task": item.task.title,
                    "Minutes": item.task.duration_minutes,
                    "Why": item.reason,
                }
                for item in plan.scheduled
            ],
            hide_index=True,
        )
    else:
        st.info("Nothing to schedule. Add some tasks first.")

    if plan.skipped:
        st.warning(f"{len(plan.skipped)} task(s) did not fit in the available time.")
        st.dataframe(
            [
                {
                    "Task": item.task.title,
                    "Pet": item.pet_name,
                    "Minutes": item.task.duration_minutes,
                    "Priority": item.task.priority.name.title(),
                    "Reason": item.reason.removeprefix("Skipped: "),
                }
                for item in plan.skipped
            ],
            hide_index=True,
        )
