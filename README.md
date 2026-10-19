# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```

 90 min available · 65 min planned · 25 min free

 TIME           PET    TASK              MIN  PRIORITY  REPEATS
 ─────────────  ─────  ────────────────  ───  ────────  ───────
 08:00 – 08:05  Luna   Give medication     5  HIGH      daily
 08:05 – 08:35  Rex    Morning walk       30  HIGH      daily
 08:35 – 08:45  Luna   Feed breakfast     10  MEDIUM    daily
 08:45 – 09:05  Luna   Play session       20  LOW       once

 Skipped (1)
 - Grooming (Rex, 40 min, LOW) — low priority, but not enough time left after higher-priority tasks.

```

## Implementation summary

`pawpal_system.py` turns an owner's daily time budget and their pets' care tasks into a prioritized daily plan, with a reason for each choice.

- **Task**: a care item with a title, duration, priority, frequency, and completed flag.
- **Pet**: a name, species, and list of tasks.
- **Owner**: a name, daily time budget, and list of pets. `get_all_tasks()` returns every pet's tasks together.
- **Scheduler**: reads from `owner.get_all_tasks()`, skips completed tasks, sorts by priority (shorter first on ties), and fits tasks into the time available.
- **Plan**: the result. It holds the scheduled tasks (with start times and reasons), the skipped tasks (with reasons), and total minutes used.






## 🧪 Testing PawPal+

```bash
# Run the full test suite (from the project folder):
python3 -m pytest tests -v
```

The tests cover multiple pets, sorting by time, filtering, recurring tasks, conflict warnings, and scheduling (priority order, skipped tasks, gap placement). They use a fixed date, so results don't change from day to day.

Sample test output:

```
============================= test session starts ==============================
collected 28 items

tests/test_pawpal.py::test_mark_complete_changes_task_status PASSED      [  3%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [  7%]
tests/test_pawpal.py::test_invalid_task_is_rejected PASSED               [ 10%]
tests/test_pawpal.py::test_duplicate_pending_title_is_rejected PASSED    [ 14%]
tests/test_pawpal.py::test_get_all_tasks_combines_every_pets_tasks PASSED [ 17%]
tests/test_pawpal.py::test_plan_includes_tasks_from_all_pets_with_pet_names PASSED [ 21%]
tests/test_pawpal.py::test_sort_by_time_orders_tasks_added_out_of_order PASSED [ 25%]
tests/test_pawpal.py::test_times_are_zero_padded_so_they_sort_correctly PASSED [ 28%]
tests/test_pawpal.py::test_filter_by_pet_name PASSED                     [ 32%]
tests/test_pawpal.py::test_filter_by_completion_status PASSED            [ 35%]
tests/test_pawpal.py::test_filter_by_pet_and_status_together PASSED      [ 39%]
tests/test_pawpal.py::test_filter_with_no_arguments_returns_everything PASSED [ 42%]
tests/test_pawpal.py::test_filter_unknown_pet_raises_key_error PASSED    [ 46%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_day_copy PASSED [ 50%]
tests/test_pawpal.py::test_completing_weekly_task_creates_copy_seven_days_later PASSED [ 53%]
tests/test_pawpal.py::test_completing_one_time_task_creates_no_copy PASSED [ 57%]
tests/test_pawpal.py::test_finishing_a_recurring_task_early_keeps_its_rhythm PASSED [ 60%]
tests/test_pawpal.py::test_complete_task_errors PASSED                   [ 64%]
tests/test_pawpal.py::test_task_due_tomorrow_is_not_in_todays_plan PASSED [ 67%]
tests/test_pawpal.py::test_same_start_time_for_same_pet_gives_a_warning PASSED [ 71%]
tests/test_pawpal.py::test_overlap_between_different_pets_gives_a_warning PASSED [ 75%]
tests/test_pawpal.py::test_back_to_back_tasks_do_not_conflict PASSED     [ 78%]
tests/test_pawpal.py::test_higher_priority_task_is_placed_first PASSED   [ 82%]
tests/test_pawpal.py::test_tasks_that_do_not_fit_are_skipped_with_a_reason PASSED [ 85%]
tests/test_pawpal.py::test_completed_tasks_are_not_scheduled PASSED      [ 89%]
tests/test_pawpal.py::test_untimed_task_is_placed_after_a_fixed_task_it_would_collide_with PASSED [ 92%]
tests/test_pawpal.py::test_untimed_task_uses_a_gap_before_a_fixed_task PASSED [ 96%]
tests/test_pawpal.py::test_owner_with_no_pets_gets_an_empty_plan PASSED  [100%]

============================== 28 passed in 0.02s ==============================
```

## 📐 Smarter Scheduling

Each feature below names the method in `pawpal_system.py` that implements it.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Priority ordering | `Scheduler._sort_by_priority` | Highest priority first; shorter tasks first on ties. Decides which tasks get the limited time. |
| Time sorting | `Scheduler.sort_by_time` | Orders tasks by `scheduled_time`. Tasks with no time go last. Times are stored zero-padded (`08:30`) so they sort correctly. |
| Fitting to the time budget | `Scheduler.generate_plan`, `Scheduler._fits_in_time` | Takes tasks in priority order until the owner's daily minutes run out. A task that doesn't fit is skipped and the scheduler keeps going, so a smaller task can still fit. |
| Gap placement | `Scheduler._place`, `Scheduler._first_gap` | Tasks with a fixed time keep it. Tasks without one go in the earliest free gap from the day's start, so the scheduler never creates a conflict itself. |
| Filtering | `Owner.filter_tasks` | Filters across all pets by pet name, completion status, or both. An unknown pet name raises `KeyError`. |
| Multi-pet task access | `Owner.get_all_tasks` | Returns every pet's tasks in one list. The scheduler reads only from this method. |
| Conflict handling | `Scheduler.detect_conflicts` | Returns a warning message for every pair of planned tasks whose time ranges overlap, for the same pet or different pets. Back-to-back tasks are not conflicts. It only warns: nothing is moved or removed, and the program does not crash. Warnings are stored in `Plan.warnings`. |
| Recurring tasks | `Pet.complete_task`, `Task.next_occurrence` | Completing a daily or weekly task creates a new pending copy with the next due date (`timedelta` of 1 or 7 days). One-time tasks create no copy. |
| Due-date check | `Task.is_due` | A task is planned only if it is not done and due on or before the plan date. |
| Explanations | `Scheduler._explain` | Gives a short reason each task was scheduled or skipped. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
