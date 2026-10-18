from pawpal_system import Frequency, Owner, Pet, PlannedTask, Priority, Scheduler, Task


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
            f" {item.start_time} – {end_time(item)}  {item.pet_name:<5}  {task.title:<16}  "
            f"{task.duration_minutes:>3}  {task.priority.name:<8}  {task.frequency.value}"
        )

    if plan.skipped:
        print(f"\n Skipped ({len(plan.skipped)})")
        for item in plan.skipped:
            task = item.task
            reason = item.reason.removeprefix("Skipped: ")
            print(
                f" - {task.title} ({item.pet_name}, {task.duration_minutes} min, "
                f"{task.priority.name}) — {reason}"
            )
    print()


def main() -> None:
    owner = Owner(name="Jordan", available_minutes_per_day=90)

    rex = Pet(name="Rex", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(rex)
    owner.add_pet(luna)

    rex.add_task(Task("Morning walk", 30, Priority.HIGH, Frequency.DAILY))
    rex.add_task(Task("Grooming", 40, Priority.LOW, Frequency.WEEKLY))
    luna.add_task(Task("Give medication", 5, Priority.HIGH, Frequency.DAILY))
    luna.add_task(Task("Feed breakfast", 10, Priority.MEDIUM, Frequency.DAILY))
    luna.add_task(Task("Play session", 20, Priority.LOW))

    plan = Scheduler(owner, day_start="08:00").generate_plan()
    print_schedule(owner, plan)


if __name__ == "__main__":
    main()
