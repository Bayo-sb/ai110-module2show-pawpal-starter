from datetime import date
import os
import sys

from pawpal_system import Frequency, Owner, Pet, PlannedTask, Priority, Scheduler, Task


def colorize(text: str, color_code: str) -> str:
    """Add ANSI color in interactive terminals unless NO_COLOR is set."""
    if not sys.stdout.isatty() or "NO_COLOR" in os.environ:
        return text
    return f"\033[{color_code}m{text}\033[0m"


def priority_label(priority: Priority, width: int = 8) -> str:
    """Return a priority label colored by urgency when supported."""
    colors = {Priority.HIGH: "31", Priority.MEDIUM: "33", Priority.LOW: "32"}
    return colorize(f"{priority.name:<{width}}", colors[priority])


def end_time(item: PlannedTask) -> str:
    """Return the 'HH:MM' a planned task finishes (start time plus its duration)."""
    hours, minutes = map(int, item.start_time.split(":"))
    total = (hours * 60 + minutes + item.task.duration_minutes) % (24 * 60)
    return f"{total // 60:02d}:{total % 60:02d}"


def print_schedule(owner: Owner, plan) -> None:
    free = owner.available_minutes_per_day - plan.total_minutes
    print(f"\nToday's Schedule — {owner.name}")
    print(
        f"   {owner.available_minutes_per_day} min available · "
        f"{plan.total_minutes} min planned · {free} min free\n"
    )

    header = f" {'TIME':<13}  {'PET':<5}  {'TASK':<16}  {'MIN':>3}  {'PRIORITY':<8}  REPEATS"
    print(header)
    print(f" {'─' * 13}  {'─' * 5}  {'─' * 16}  {'─' * 3}  {'─' * 8}  {'─' * 7}")
    for item in plan.scheduled:
        task = item.task
        print(
            f" {colorize('[PLAN]', '32')} {item.start_time} – {end_time(item)}  "
            f"{item.pet_name:<5}  {task.title:<16}  {task.duration_minutes:>3}  "
            f"{priority_label(task.priority)}  {task.frequency.value}"
        )

    if plan.skipped:
        print(f"\n Skipped ({len(plan.skipped)})")
        for item in plan.skipped:
            task = item.task
            reason = item.reason.removeprefix("Skipped: ")
            print(
                f" {colorize('[SKIP]', '33')} {task.title} ({item.pet_name}, "
                f"{task.duration_minutes} min, {priority_label(task.priority, width=0)}) — {reason}"
            )

    if plan.warnings:
        print(f"\n Warnings ({len(plan.warnings)})")
        for warning in plan.warnings:
            print(f" {colorize('[WARN]', '31')} {warning}")
    print()


def print_tasks(heading: str, tasks) -> None:
    print(f"\n{heading}")
    if not tasks:
        print("   (none)")
    for t in tasks:
        when = t.scheduled_time or "any time"
        due = t.due_date.isoformat() if t.due_date else "-"
        status = colorize("[DONE]", "32") if t.completed else colorize("[PENDING]", "33")
        print(f"   {t.pet_name:<5} {t.title:<16} {when:<9} due {due:<10} {status}")


def main() -> None:
    today = date.today()
    owner = Owner(name="Jordan", available_minutes_per_day=90)

    rex = Pet(name="Rex", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(rex)
    owner.add_pet(luna)

    # Added out of order on purpose, to show sorting by time.
    luna.add_task(Task("Evening feed", 10, Priority.MEDIUM, Frequency.DAILY, scheduled_time="18:00"))
    luna.add_task(Task("Give medication", 5, Priority.HIGH, Frequency.DAILY, scheduled_time="08:30"))
    luna.add_task(Task("Feed breakfast", 10, Priority.MEDIUM, Frequency.DAILY))
    luna.add_task(Task("Play session", 20, Priority.LOW))
    rex.add_task(Task("Morning walk", 30, Priority.HIGH, Frequency.DAILY, scheduled_time="08:30"))
    rex.add_task(Task("Grooming", 40, Priority.LOW, Frequency.WEEKLY))

    scheduler = Scheduler(owner, day_start="08:00", plan_date=today)

    # 1. Sort by time
    print_tasks("1. All tasks sorted by time:", scheduler.sort_by_time(owner.get_all_tasks()))

    # 2. Filter by pet / status
    print_tasks("2a. Luna's tasks:", owner.filter_tasks(pet_name="Luna"))
    print_tasks("2b. Pending tasks for all pets:", owner.filter_tasks(completed=False))

    # 3. Plan, including conflict detection (walk and medication both start at 08:30)
    print_schedule(owner, scheduler.generate_plan())

    # 4. Recurring tasks: finishing a daily task creates tomorrow's copy
    next_walk = rex.complete_task("Morning walk", today=today)
    print(
        f"{colorize('[DONE]', '32')} Completed 'Morning walk'. "
        f"Next one is due {next_walk.due_date}."
    )
    print_tasks(
        "Rex's pending tasks after completing the walk:",
        owner.filter_tasks(pet_name="Rex", completed=False),
    )
    print_tasks("Finished tasks for all pets:", owner.filter_tasks(completed=True))


if __name__ == "__main__":
    main()