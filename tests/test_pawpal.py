import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

# Make pawpal_system importable when pytest is run from any directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

TODAY = date(2026, 10, 18)  # fixed, so results never change from day to day


def make_owner(minutes=300):
    """Return an owner with two pets, Rex and Luna, and no tasks."""
    owner = Owner("Jordan", minutes)
    owner.add_pet(Pet("Rex", "dog"))
    owner.add_pet(Pet("Luna", "cat"))
    return owner


def make_scheduler(owner):
    return Scheduler(owner, day_start="08:00", plan_date=TODAY)


def titles(tasks):
    return [t.title for t in tasks]


# --- Basics ---------------------------------------------------------------


def test_mark_complete_changes_task_status():
    task = Task("Morning walk", 30, Priority.HIGH)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Rex", "dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Morning walk", 30, Priority.HIGH))
    assert len(pet.get_tasks()) == 1

    pet.add_task(Task("Feed breakfast", 10, Priority.MEDIUM))
    assert len(pet.get_tasks()) == 2


def test_invalid_task_is_rejected():
    with pytest.raises(ValueError):
        Task("", 10, Priority.LOW)
    with pytest.raises(ValueError):
        Task("Walk", 0, Priority.LOW)


def test_duplicate_pending_title_is_rejected():
    pet = Pet("Rex", "dog")
    pet.add_task(Task("Walk", 30, Priority.HIGH))

    with pytest.raises(ValueError):
        pet.add_task(Task("Walk", 10, Priority.LOW))


# --- Multiple pets --------------------------------------------------------


def test_get_all_tasks_combines_every_pets_tasks():
    owner = make_owner()
    owner.get_pet("Rex").add_task(Task("Walk", 30, Priority.HIGH))
    owner.get_pet("Luna").add_task(Task("Meds", 5, Priority.HIGH))

    assert sorted(titles(owner.get_all_tasks())) == ["Meds", "Walk"]


def test_plan_includes_tasks_from_all_pets_with_pet_names():
    owner = make_owner()
    owner.get_pet("Rex").add_task(Task("Walk", 30, Priority.HIGH))
    owner.get_pet("Luna").add_task(Task("Meds", 5, Priority.HIGH))

    plan = make_scheduler(owner).generate_plan()

    assert {(i.pet_name, i.task.title) for i in plan.scheduled} == {
        ("Rex", "Walk"),
        ("Luna", "Meds"),
    }


# --- Sorting --------------------------------------------------------------


def test_sort_by_time_orders_tasks_added_out_of_order():
    owner = make_owner()
    luna = owner.get_pet("Luna")
    luna.add_task(Task("Evening feed", 10, Priority.MEDIUM, scheduled_time="18:00"))
    luna.add_task(Task("No time", 10, Priority.LOW))
    luna.add_task(Task("Medication", 5, Priority.HIGH, scheduled_time="08:30"))

    ordered = make_scheduler(owner).sort_by_time(owner.get_all_tasks())

    assert titles(ordered) == ["Medication", "Evening feed", "No time"]


def test_times_are_zero_padded_so_they_sort_correctly():
    assert Task("Walk", 10, Priority.LOW, scheduled_time="8:30").scheduled_time == "08:30"


# --- Filtering ------------------------------------------------------------


def make_filter_owner():
    owner = make_owner()
    rex, luna = owner.get_pet("Rex"), owner.get_pet("Luna")
    rex.add_task(Task("Walk", 30, Priority.HIGH))
    rex.add_task(Task("Groom", 20, Priority.LOW))
    luna.add_task(Task("Meds", 5, Priority.HIGH))
    luna.add_task(Task("Play", 10, Priority.LOW))
    rex.get_tasks()[0].mark_complete()  # Walk
    luna.get_tasks()[0].mark_complete()  # Meds
    return owner


def test_filter_by_pet_name():
    owner = make_filter_owner()

    assert titles(owner.filter_tasks(pet_name="Rex")) == ["Walk", "Groom"]


def test_filter_by_completion_status():
    owner = make_filter_owner()

    assert titles(owner.filter_tasks(completed=True)) == ["Walk", "Meds"]
    assert titles(owner.filter_tasks(completed=False)) == ["Groom", "Play"]


def test_filter_by_pet_and_status_together():
    owner = make_filter_owner()

    assert titles(owner.filter_tasks(pet_name="Luna", completed=False)) == ["Play"]


def test_filter_with_no_arguments_returns_everything():
    owner = make_filter_owner()

    assert len(owner.filter_tasks()) == 4


def test_filter_unknown_pet_raises_key_error():
    owner = make_filter_owner()

    with pytest.raises(KeyError):
        owner.filter_tasks(pet_name="Zed")


# --- Recurring tasks ------------------------------------------------------


def test_completing_daily_task_creates_next_day_copy():
    pet = Pet("Rex", "dog")
    pet.add_task(Task("Walk", 30, Priority.HIGH, Frequency.DAILY, scheduled_time="08:30"))

    new_task = pet.complete_task("Walk", today=TODAY)

    assert new_task.due_date == TODAY + timedelta(days=1)
    assert new_task.completed is False
    assert new_task.title == "Walk"
    assert new_task.scheduled_time == "08:30"
    assert len(pet.get_tasks()) == 2
    assert pet.get_tasks()[0].completed is True


def test_completing_weekly_task_creates_copy_seven_days_later():
    pet = Pet("Rex", "dog")
    pet.add_task(Task("Groom", 40, Priority.LOW, Frequency.WEEKLY))

    new_task = pet.complete_task("Groom", today=TODAY)

    assert new_task.due_date == TODAY + timedelta(days=7)


def test_completing_one_time_task_creates_no_copy():
    pet = Pet("Rex", "dog")
    pet.add_task(Task("Vet visit", 60, Priority.HIGH))

    assert pet.complete_task("Vet visit", today=TODAY) is None
    assert len(pet.get_tasks()) == 1


def test_finishing_a_recurring_task_early_keeps_its_rhythm():
    pet = Pet("Rex", "dog")
    due_in_three_days = TODAY + timedelta(days=3)
    pet.add_task(Task("Walk", 30, Priority.HIGH, Frequency.DAILY, due_date=due_in_three_days))

    new_task = pet.complete_task("Walk", today=TODAY)

    assert new_task.due_date == due_in_three_days + timedelta(days=1)


def test_complete_task_errors():
    pet = Pet("Rex", "dog")
    pet.add_task(Task("Vet visit", 60, Priority.HIGH))
    pet.complete_task("Vet visit", today=TODAY)

    with pytest.raises(KeyError):
        pet.complete_task("Missing", today=TODAY)
    with pytest.raises(ValueError):
        pet.complete_task("Vet visit", today=TODAY)  # already completed


def test_task_due_tomorrow_is_not_in_todays_plan():
    owner = make_owner()
    owner.get_pet("Rex").add_task(
        Task("Walk", 30, Priority.HIGH, due_date=TODAY + timedelta(days=1))
    )

    assert make_scheduler(owner).generate_plan().scheduled == []


# --- Conflict detection ---------------------------------------------------


def test_same_start_time_for_same_pet_gives_a_warning():
    owner = make_owner()
    rex = owner.get_pet("Rex")
    rex.add_task(Task("Walk", 30, Priority.HIGH, scheduled_time="08:30"))
    rex.add_task(Task("Bath", 20, Priority.LOW, scheduled_time="08:30"))

    plan = make_scheduler(owner).generate_plan()

    assert len(plan.warnings) == 1
    assert "Walk" in plan.warnings[0] and "Bath" in plan.warnings[0]
    assert len(plan.scheduled) == 2  # nothing is removed or moved


def test_overlap_between_different_pets_gives_a_warning():
    owner = make_owner()
    owner.get_pet("Rex").add_task(Task("Walk", 30, Priority.HIGH, scheduled_time="08:30"))
    owner.get_pet("Luna").add_task(Task("Meds", 5, Priority.HIGH, scheduled_time="08:45"))

    plan = make_scheduler(owner).generate_plan()

    assert len(plan.warnings) == 1
    assert "Rex" in plan.warnings[0] and "Luna" in plan.warnings[0]


def test_back_to_back_tasks_do_not_conflict():
    owner = make_owner()
    rex = owner.get_pet("Rex")
    rex.add_task(Task("Walk", 30, Priority.HIGH, scheduled_time="08:30"))
    rex.add_task(Task("Feed", 10, Priority.MEDIUM, scheduled_time="09:00"))

    assert make_scheduler(owner).generate_plan().warnings == []


# --- Scheduling -----------------------------------------------------------


def test_higher_priority_task_is_placed_first():
    owner = make_owner()
    rex = owner.get_pet("Rex")
    rex.add_task(Task("Low", 20, Priority.LOW))
    rex.add_task(Task("High", 10, Priority.HIGH))

    plan = make_scheduler(owner).generate_plan()

    assert [(i.task.title, i.start_time) for i in plan.scheduled] == [
        ("High", "08:00"),
        ("Low", "08:10"),
    ]


def test_tasks_that_do_not_fit_are_skipped_with_a_reason():
    owner = make_owner(minutes=30)
    rex = owner.get_pet("Rex")
    rex.add_task(Task("Big", 25, Priority.HIGH))
    rex.add_task(Task("Medium", 20, Priority.MEDIUM))
    rex.add_task(Task("Small", 10, Priority.LOW))

    plan = make_scheduler(owner).generate_plan()

    assert titles(i.task for i in plan.scheduled) == ["Big"]
    assert plan.total_minutes == 25
    assert titles(i.task for i in plan.skipped) == ["Medium", "Small"]
    assert all(i.reason for i in plan.skipped)


def test_completed_tasks_are_not_scheduled():
    owner = make_owner()
    rex = owner.get_pet("Rex")
    rex.add_task(Task("Done", 10, Priority.HIGH))
    rex.add_task(Task("Todo", 10, Priority.HIGH))
    rex.get_tasks()[0].mark_complete()

    plan = make_scheduler(owner).generate_plan()

    assert titles(i.task for i in plan.scheduled) == ["Todo"]


def test_untimed_task_is_placed_after_a_fixed_task_it_would_collide_with():
    owner = make_owner()
    rex = owner.get_pet("Rex")
    rex.add_task(Task("Bath", 40, Priority.HIGH))
    rex.add_task(Task("Vet", 30, Priority.HIGH, scheduled_time="08:30"))

    plan = make_scheduler(owner).generate_plan()
    starts = {i.task.title: i.start_time for i in plan.scheduled}

    assert starts == {"Vet": "08:30", "Bath": "09:00"}
    assert plan.warnings == []


def test_untimed_task_uses_a_gap_before_a_fixed_task():
    owner = make_owner()
    rex = owner.get_pet("Rex")
    rex.add_task(Task("Feed", 20, Priority.HIGH))
    rex.add_task(Task("Vet", 30, Priority.HIGH, scheduled_time="08:30"))

    plan = make_scheduler(owner).generate_plan()
    starts = {i.task.title: i.start_time for i in plan.scheduled}

    assert starts["Feed"] == "08:00"
    assert plan.warnings == []


def test_owner_with_no_pets_gets_an_empty_plan():
    plan = make_scheduler(Owner("Jordan", 60)).generate_plan()

    assert plan.scheduled == [] and plan.skipped == [] and plan.total_minutes == 0
