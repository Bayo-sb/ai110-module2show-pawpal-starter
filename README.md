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
python -m pytest
```

Add `-v` to list each test. The suite lives in `tests/test_pawpal.py` (54 tests) and uses a fixed date, so results don't change from day to day.

Output of the sorting, recurrence, and conflict tests:

```
tests/test_pawpal.py::test_sort_by_time_orders_tasks_added_out_of_order PASSED                               [ 12%]
tests/test_pawpal.py::test_times_are_zero_padded_so_they_sort_correctly PASSED                               [ 25%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_day_copy PASSED                                [ 37%]
tests/test_pawpal.py::test_same_start_time_for_same_pet_gives_a_warning PASSED                               [ 50%]
tests/test_pawpal.py::test_sort_by_time_with_no_tasks_returns_empty_list PASSED                              [ 62%]
tests/test_pawpal.py::test_sort_by_time_keeps_original_order_for_equal_times PASSED                          [ 75%]
tests/test_pawpal.py::test_sort_by_time_handles_midnight_and_last_minute PASSED                              [ 87%]
tests/test_pawpal.py::test_daily_recurrence_rolls_over_the_year_end PASSED                                   [100%]
```

**Happy paths**
- **Sorting:** tasks added out of order come back chronologically, untimed tasks go last, and the generated plan is in time order.
- **Recurrence:** completing a daily or weekly task creates a pending copy due 1 or 7 days later. One-time tasks create no copy.
- **Conflicts:** same-start-time and overlapping tasks (same pet or different pets) produce a warning. Back-to-back tasks do not.
- **Scheduling:** priority order, skipped tasks with a reason, gap placement around fixed-time tasks, and tasks from several pets in one plan.
- **Filtering:** by pet, by completion status, both together, and no filter.

**Edge cases**
- **Empty input:** a pet or owner with no tasks, an empty list to sort, and an owner with no pets all give an empty result with no crash.
- **Ties and boundaries:** equal times keep their original order, `00:00` and `23:59` sort correctly, and invalid times (`25:00`, `12:60`, `abc`, ...) are rejected.
- **Recurrence dates:** year-end and leap-day rollover, finishing early keeps the rhythm, and finishing late restarts from today. A recurring task shows up in the plan only on its due day.
- **Conflict shapes:** a task fully inside another, a three-way overlap (one warning per pair), and conflicts are reported without moving or dropping tasks.
- **Time budget:** a task exactly filling the budget is scheduled, one minute over is skipped, and a zero budget skips everything.
- **Bad edits:** a failed `update` leaves the task unchanged, and editing, removing or completing a missing task raises an error.



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
