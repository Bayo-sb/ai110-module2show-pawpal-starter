import streamlit as st

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner and Pets")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes_per_day=90)
owner = st.session_state.owner

owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes_per_day = st.number_input(
    "Minutes available per day",
    min_value=0,
    max_value=1440,
    value=owner.available_minutes_per_day,
)

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    try:
        owner.add_pet(Pet(name=pet_name, species=species))
    except ValueError as e:
        st.error(str(e))

if owner.pets:
    st.write("Pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))

st.markdown("### Tasks")

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

    if st.button("Add task"):
        try:
            owner.get_pet(target).add_task(
                Task(task_title, int(duration), Priority[priority], Frequency(frequency))
            )
        except ValueError as e:
            st.error(str(e))

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.table(
        [
            {
                "pet": t.pet_name,
                "task": t.title,
                "minutes": t.duration_minutes,
                "priority": t.priority.name,
                "repeats": t.frequency.value,
                "done": t.completed,
            }
            for t in all_tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    plan = Scheduler(owner).generate_plan()

    st.write(f"{plan.total_minutes} of {owner.available_minutes_per_day} minutes planned")
    st.table(
        [
            {
                "time": item.start_time,
                "pet": item.pet_name,
                "task": item.task.title,
                "minutes": item.task.duration_minutes,
                "why": item.reason,
            }
            for item in plan.scheduled
        ]
    )
    if plan.skipped:
        st.warning("Skipped tasks")
        for item in plan.skipped:
            st.write(f"- {item.task.title} ({item.pet_name}): {item.reason}")
