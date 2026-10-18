from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Optional


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


@dataclass
class Task:
    """One care item (walk, feeding, meds, ...). Holds data and can be edited."""

    title: str
    duration_minutes: int
    priority: Priority
    frequency: Frequency = Frequency.ONCE
    completed: bool = False
    pet_name: str = field(default="", init=False)  # set by Pet.add_task

    def __post_init__(self) -> None:
        """Validate the task's fields when it is created."""
        self._validate(self.title, self.duration_minutes, self.priority)

    @staticmethod
    def _validate(title: str, duration_minutes: int, priority: Priority) -> None:
        """Raise ValueError if the title, duration, or priority is invalid."""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty.")
        if duration_minutes <= 0:
            raise ValueError("Task duration must be greater than 0 minutes.")
        if not isinstance(priority, Priority):
            raise ValueError("Task priority must be a Priority value.")

    def update(
        self,
        title: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        priority: Optional[Priority] = None,
        frequency: Optional[Frequency] = None,
    ) -> None:
        """Change any of the task's fields; leave the rest as they are."""
        new_title = self.title if title is None else title
        new_duration = self.duration_minutes if duration_minutes is None else duration_minutes
        new_priority = self.priority if priority is None else priority
        # Validate everything first so a bad value never leaves the task half-edited.
        self._validate(new_title, new_duration, new_priority)
        self.title = new_title
        self.duration_minutes = new_duration
        self.priority = new_priority
        if frequency is not None:
            self.frequency = frequency

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


@dataclass
class Pet:
    """A pet and the list of care tasks that belong to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's list. Titles must be unique per pet."""
        if self._find(task.title) is not None:
            raise ValueError(f"A task titled '{task.title}' already exists.")
        task.pet_name = self.name
        self.tasks.append(task)

    def edit_task(self, title: str, updates: dict) -> None:
        """Find the task by title and apply the given updates."""
        task = self._find(title)
        if task is None:
            raise KeyError(f"No task titled '{title}'.")
        new_title = updates.get("title")
        if new_title is not None and new_title != title and self._find(new_title) is not None:
            raise ValueError(f"A task titled '{new_title}' already exists.")
        task.update(**updates)

    def remove_task(self, title: str) -> None:
        """Remove the task with the given title."""
        task = self._find(title)
        if task is None:
            raise KeyError(f"No task titled '{title}'.")
        self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return all of this pet's tasks (a copy, so callers can't alter the list)."""
        return list(self.tasks)

    def _find(self, title: str) -> Optional[Task]:
        """Return the task with the given title, or None."""
        for task in self.tasks:
            if task.title == title:
                return task
        return None


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


class Scheduler:
    """Builds an ordered daily plan from the owner's time limit and their pet's tasks."""

    def __init__(self, owner: Owner, day_start: str = "08:00") -> None:
        """Set up the scheduler for an owner and validate the day's start time."""
        self.owner = owner  # tasks for all pets come from owner.get_all_tasks()
        self.day_start = day_start
        self._start_minutes = self._parse_clock(day_start)

    @staticmethod
    def _parse_clock(value: str) -> int:
        """Convert 'HH:MM' into minutes after midnight, or raise ValueError."""
        try:
            hours, minutes = value.split(":")
            h, m = int(hours), int(minutes)
        except ValueError:
            raise ValueError(f"day_start must look like 'HH:MM', got '{value}'.") from None
        if not (0 <= h < 24 and 0 <= m < 60):
            raise ValueError(f"day_start is not a valid time: '{value}'.")
        return h * 60 + m

    def generate_plan(self) -> Plan:
        """Sort tasks, fit them into the available time, and return a fresh Plan."""
        plan = Plan()
        pending = [t for t in self.owner.get_all_tasks() if not t.completed]

        for task in self._sort_by_priority(pending):
            if self._fits_in_time(task, plan.total_minutes):
                plan.scheduled.append(
                    PlannedTask(
                        task=task,
                        start_time=self._clock(plan.total_minutes),
                        reason=self._explain(task, scheduled=True),
                    )
                )
                plan.total_minutes += task.duration_minutes
            else:
                # Keep going: a shorter, lower-priority task may still fit.
                plan.skipped.append(
                    SkippedTask(task=task, reason=self._explain(task, scheduled=False))
                )
        return plan

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
        total = (self._start_minutes + minutes_from_start) % (24 * 60)
        return f"{total // 60:02d}:{total % 60:02d}"
