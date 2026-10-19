from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum, IntEnum
from typing import Optional


def parse_clock(value: str, label: str = "time") -> int:
    """Convert 'HH:MM' into minutes after midnight, or raise ValueError."""
    try:
        hours, minutes = value.split(":")
        h, m = int(hours), int(minutes)
    except (ValueError, AttributeError):
        raise ValueError(f"{label} must look like 'HH:MM', got '{value}'.") from None
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError(f"{label} is not a valid time: '{value}'.")
    return h * 60 + m


def format_clock(total_minutes: int) -> str:
    """Convert minutes after midnight into 'HH:MM' (wraps past midnight)."""
    total_minutes %= 24 * 60
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


class Priority(IntEnum):
    """Task priority. Higher value means more important, so sorting is explicit."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(Enum):
    """How often a task recurs."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


# Days until the next occurrence of a recurring task. ONCE is not listed: it never repeats.
RECURRENCE_DAYS = {Frequency.DAILY: 1, Frequency.WEEKLY: 7}


@dataclass
class Task:
    """One care item (walk, feeding, meds, ...). Holds data and can be edited.

    scheduled_time: optional 'HH:MM' the owner wants the task done at. Without it the
        scheduler places the task wherever it fits.
    due_date: optional date the task is next due. None means "due whenever".
    """

    title: str
    duration_minutes: int
    priority: Priority
    frequency: Frequency = Frequency.ONCE
    completed: bool = False
    scheduled_time: Optional[str] = None
    due_date: Optional[date] = None
    pet_name: str = field(default="", init=False)  # set by Pet.add_task

    def __post_init__(self) -> None:
        """Validate the task's fields when it is created."""
        self._validate(self.title, self.duration_minutes, self.priority, self.scheduled_time)
        self.scheduled_time = self._normalize_time(self.scheduled_time)

    @staticmethod
    def _normalize_time(value: Optional[str]) -> Optional[str]:
        """Store times zero-padded ('8:30' -> '08:30') so plain string sorting is correct."""
        return None if value is None else format_clock(parse_clock(value, "scheduled_time"))

    @staticmethod
    def _validate(
        title: str,
        duration_minutes: int,
        priority: Priority,
        scheduled_time: Optional[str] = None,
    ) -> None:
        """Raise ValueError if the title, duration, priority, or time is invalid."""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty.")
        if duration_minutes <= 0:
            raise ValueError("Task duration must be greater than 0 minutes.")
        if not isinstance(priority, Priority):
            raise ValueError("Task priority must be a Priority value.")
        if scheduled_time is not None:
            parse_clock(scheduled_time, "scheduled_time")

    def update(
        self,
        title: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        priority: Optional[Priority] = None,
        frequency: Optional[Frequency] = None,
        scheduled_time: Optional[str] = None,
        due_date: Optional[date] = None,
    ) -> None:
        """Change any of the task's fields; leave the rest as they are."""
        new_title = self.title if title is None else title
        new_duration = self.duration_minutes if duration_minutes is None else duration_minutes
        new_priority = self.priority if priority is None else priority
        new_time = self.scheduled_time if scheduled_time is None else scheduled_time
        # Validate everything first so a bad value never leaves the task half-edited.
        self._validate(new_title, new_duration, new_priority, new_time)
        self.title = new_title
        self.duration_minutes = new_duration
        self.priority = new_priority
        self.scheduled_time = self._normalize_time(new_time)
        if frequency is not None:
            self.frequency = frequency
        if due_date is not None:
            self.due_date = due_date

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def is_due(self, on: date) -> bool:
        """Return True if the task is not done and is due on or before the given date."""
        return not self.completed and (self.due_date is None or self.due_date <= on)

    def next_occurrence(self, today: date) -> Optional[Task]:
        """Return a fresh copy of this task for its next due date, or None if it never repeats.

        The next date counts from the later of the task's due date and today, so finishing
        a task early keeps its rhythm and finishing it late restarts the rhythm from today.
        """
        step = RECURRENCE_DAYS.get(self.frequency)
        if step is None:
            return None
        base = max(self.due_date or today, today)
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            scheduled_time=self.scheduled_time,
            due_date=base + timedelta(days=step),
        )


@dataclass
class Pet:
    """A pet and the list of care tasks that belong to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's list. Pending task titles must be unique per pet."""
        existing = self._find(task.title)
        if existing is not None and not existing.completed:
            raise ValueError(f"A task titled '{task.title}' already exists.")
        task.pet_name = self.name
        self.tasks.append(task)

    def edit_task(self, title: str, updates: dict) -> None:
        """Find the task by title and apply the given updates."""
        task = self._find(title)
        if task is None:
            raise KeyError(f"No task titled '{title}'.")
        new_title = updates.get("title")
        if new_title is not None and new_title != title:
            clash = self._find(new_title)
            if clash is not None and not clash.completed:
                raise ValueError(f"A task titled '{new_title}' already exists.")
        task.update(**updates)

    def remove_task(self, title: str) -> None:
        """Remove the task with the given title."""
        task = self._find(title)
        if task is None:
            raise KeyError(f"No task titled '{title}'.")
        self.tasks.remove(task)

    def complete_task(self, title: str, today: Optional[date] = None) -> Optional[Task]:
        """Mark a task done. If it repeats, add its next occurrence and return it.

        Returns None for one-time tasks.
        """
        task = self._find(title)
        if task is None:
            raise KeyError(f"No task titled '{title}'.")
        if task.completed:
            raise ValueError(f"Task '{title}' is already completed.")
        task.mark_complete()
        next_task = task.next_occurrence(today or date.today())
        if next_task is not None:
            self.add_task(next_task)
        return next_task

    def get_tasks(self) -> list[Task]:
        """Return all of this pet's tasks (a copy, so callers can't alter the list)."""
        return list(self.tasks)

    def _find(self, title: str) -> Optional[Task]:
        """Return the task with the given title, or None.

        A pending task wins over completed ones with the same title (a repeating task
        leaves its finished copies behind).
        """
        match = None
        for task in self.tasks:
            if task.title == title:
                if not task.completed:
                    return task
                match = match or task
        return match


@dataclass
class Owner:
    """The pet owner: name, daily time budget, preferences, and their pets."""

    name: str
    available_minutes_per_day: int
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Reject a negative daily time budget."""
        if self.available_minutes_per_day < 0:
            raise ValueError("Available minutes per day cannot be negative.")

    def add_pet(self, pet: Pet) -> None:
        """Add a pet. Pet names must be unique per owner."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"A pet named '{pet.name}' already exists.")
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove the pet with the given name."""
        pet = self.get_pet(name)
        if pet is None:
            raise KeyError(f"No pet named '{name}'.")
        self.pets.remove(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return the pet with the given name, or None."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Return every pet's tasks together in a single list."""
        return [task for pet in self.pets for task in pet.get_tasks()]

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> list[Task]:
        """Return tasks matching the filters. A filter left as None is not applied.

        pet_name: only that pet's tasks (raises KeyError if there is no such pet).
        completed: True for finished tasks, False for pending ones.
        """
        if pet_name is not None:
            pet = self.get_pet(pet_name)
            if pet is None:
                raise KeyError(f"No pet named '{pet_name}'.")
            tasks = pet.get_tasks()
        else:
            tasks = self.get_all_tasks()
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def update_preferences(self, preferences: dict) -> None:
        """Merge new preferences into the owner's existing ones."""
        self.preferences.update(preferences)


@dataclass
class PlannedTask:
    """A task placed in the day's plan, with a start time and the reason it was chosen."""

    task: Task
    start_time: str
    reason: str

    @property
    def pet_name(self) -> str:
        """Return the name of the pet this task belongs to."""
        return self.task.pet_name


@dataclass
class SkippedTask:
    """A task that did not make it into the plan, with the reason why."""

    task: Task
    reason: str

    @property
    def pet_name(self) -> str:
        """Return the name of the pet this skipped task belongs to."""
        return self.task.pet_name


@dataclass
class Plan:
    """The result of scheduling: what was chosen, what was left out, and time used."""

    scheduled: list[PlannedTask] = field(default_factory=list)
    skipped: list[SkippedTask] = field(default_factory=list)
    total_minutes: int = 0
    warnings: list[str] = field(default_factory=list)  # e.g. time conflicts


class Scheduler:
    """Builds an ordered daily plan from the owner's time limit and their pet's tasks."""

    def __init__(
        self, owner: Owner, day_start: str = "08:00", plan_date: Optional[date] = None
    ) -> None:
        """Set up the scheduler for an owner, a start time, and the date being planned."""
        self.owner = owner  # tasks for all pets come from owner.get_all_tasks()
        self.day_start = day_start
        self.plan_date = plan_date or date.today()
        self._start_minutes = self._parse_clock(day_start)

    @staticmethod
    def _parse_clock(value: str) -> int:
        """Convert 'HH:MM' into minutes after midnight, or raise ValueError."""
        return parse_clock(value, "day_start")

    def generate_plan(self) -> Plan:
        """Pick the tasks due today that fit, place them in time order, and flag conflicts.

        Tasks with a scheduled_time start at that time. All other tasks go in the earliest
        free gap from day_start that avoids those fixed tasks. Overlaps that remain (two
        fixed tasks at the same time) are reported in plan.warnings, not fixed.
        """
        plan = Plan()
        due = [t for t in self.owner.get_all_tasks() if t.is_due(self.plan_date)]

        chosen = []
        for task in self._sort_by_priority(due):
            if self._fits_in_time(task, plan.total_minutes):
                chosen.append(task)
                plan.total_minutes += task.duration_minutes
            else:
                # Keep going: a shorter, lower-priority task may still fit.
                plan.skipped.append(
                    SkippedTask(task=task, reason=self._explain(task, scheduled=False))
                )

        plan.scheduled = self._place(chosen)
        plan.warnings = self.detect_conflicts(plan.scheduled)
        return plan

    def _place(self, tasks: list[Task]) -> list[PlannedTask]:
        """Give every chosen task a start time and return them in time order.

        Fixed-time tasks keep their time. The rest, taken in the order given (highest
        priority first), fill the earliest gap that avoids everything already placed.
        """
        busy = sorted(
            (parse_clock(t.scheduled_time), parse_clock(t.scheduled_time) + t.duration_minutes)
            for t in tasks
            if t.scheduled_time is not None
        )
        items = []
        for task in tasks:
            if task.scheduled_time is not None:
                start = parse_clock(task.scheduled_time)
            else:
                start = self._first_gap(task.duration_minutes, busy)
                busy.append((start, start + task.duration_minutes))
                busy.sort()
            items.append(
                PlannedTask(
                    task=task,
                    start_time=format_clock(start),
                    reason=self._explain(task, scheduled=True),
                )
            )
        items.sort(key=lambda item: item.start_time)
        return items

    def _first_gap(self, duration: int, busy: list[tuple[int, int]]) -> int:
        """Return the earliest start (minutes) from day_start where `duration` fits.

        busy is a sorted list of (start, end) spans that are already taken.
        """
        cursor = self._start_minutes
        for start, end in busy:
            if start - cursor >= duration:
                break  # the gap before this span is big enough
            cursor = max(cursor, end)
        return cursor

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by scheduled_time; tasks with no time go last.

        Ties keep their original order.
        """
        # Zero-padded "HH:MM" strings sort correctly as plain text ("08:30" < "18:00").
        # The tuple puts tasks with no time (None -> True) after all timed ones.
        return sorted(tasks, key=lambda t: (t.scheduled_time is None, t.scheduled_time or ""))

    def detect_conflicts(self, items: list[PlannedTask]) -> list[str]:
        """Return a warning for every pair of planned tasks whose times overlap.

        Back-to-back tasks (one ends exactly when the next starts) do not conflict.
        This only reports problems; it never moves or removes anything.
        """
        spans = []
        for item in items:
            start = parse_clock(item.start_time)
            spans.append((start, start + item.task.duration_minutes, item))

        warnings = []
        for i in range(len(spans)):
            for j in range(i + 1, len(spans)):
                start_a, end_a, a = spans[i]
                start_b, end_b, b = spans[j]
                if start_a < end_b and start_b < end_a:
                    warnings.append(
                        f"Conflict: '{a.task.title}' ({a.pet_name}, "
                        f"{format_clock(start_a)}-{format_clock(end_a)}) overlaps "
                        f"'{b.task.title}' ({b.pet_name}, "
                        f"{format_clock(start_b)}-{format_clock(end_b)})."
                    )
        return warnings

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered from highest to lowest priority (shorter first on ties)."""
        return sorted(tasks, key=lambda t: (-t.priority, t.duration_minutes))

    def _fits_in_time(self, task: Task, minutes_used: int) -> bool:
        """Return True if the task still fits in the owner's remaining time."""
        return minutes_used + task.duration_minutes <= self.owner.available_minutes_per_day

    def _explain(self, task: Task, scheduled: bool) -> str:
        """Return a short reason the task was scheduled or skipped."""
        level = task.priority.name.lower()
        if scheduled:
            return f"Scheduled because it is {level} priority and fits in the remaining time."
        if task.duration_minutes > self.owner.available_minutes_per_day:
            return (
                f"Skipped: needs {task.duration_minutes} min, more than the "
                f"{self.owner.available_minutes_per_day} min available in a day."
            )
        return f"Skipped: {level} priority, but not enough time left after higher-priority tasks."

    def _clock(self, minutes_from_start: int) -> str:
        """Convert minutes after day_start into an 'HH:MM' string (wraps past midnight)."""
        return format_clock(self._start_minutes + minutes_from_start)