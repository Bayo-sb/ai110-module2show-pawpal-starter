import sys
from pathlib import Path

# Make pawpal_system importable when pytest is run from any directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Priority, Task


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
