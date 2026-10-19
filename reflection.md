# PawPal+ Project Reflection

## 1. System Design
User ashould be able to input the pet and their details
Users should be able to create  and edit tasks
Users should be able to generate and view tasks


**a. Initial design**

- Briefly describe your initial UML design.

My initial UML design has five classes: Owner, Pet, Task, Scheduler, and PlannedTask. Together they model a simple pet care app, where an owner with limited free time gets a daily plan for their pet's care tasks.


- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**
The first three classes store information. The Owner class holds the owner's name and the number of minutes they have free each day. Each owner has exactly one pet. The Pet class holds the pet's name and type of animal, and it keeps a list of care tasks. A pet can have no tasks or many, and it has methods to add, edit, and remove them. The Task class describes one care activity, such as a walk, a feeding, or medicine. Each task has a title, a length of time, and a priority.

The last two classes handle the planning. The Scheduler class is the part of the design that does the work. It reads the owner's free time and the pet's tasks, then sorts the tasks by priority. It goes through them in order and keeps only the ones that fit in the time available. It also writes a short reason for each choice, so the user can see why the plan looks the way it does. The PlannedTask class holds the result. Each PlannedTask contains one Task, along with the time it starts and the reason it was chosen. I kept PlannedTask separate from Task on purpose. A task is just an activity that can be reused, while a planned task is that activity placed at a certain time on a certain day.

The classes connect in a clear chain. An Owner has one Pet, and a Pet has no or many Tasks. The Scheduler depends on the Owner and the Pet to read their information, and it creates the PlannedTasks. Each PlannedTask wraps one Task. This design keeps each class focused on one job, which makes the app easier to understand and change later.


- Did your design change during implementation?


Yes, my design changed after I asked an AI assistant to review my class skeleton for missing relationships and logic problems. It pointed out three weaknesses, and I changed the design to fix them.




- If yes, describe at least one change and why you made it.


Redundant references. My Scheduler took both an Owner and a Pet, but the Owner already holds its pet, so the two could disagree. I changed the Scheduler to take only the Owner and read owner.pet.
Skipped tasks had no home. The Scheduler stored skipped tasks in a separate list, so a skip reason had nowhere to go. I added a Plan object that holds the scheduled tasks, the skipped tasks with their reasons, and the total minutes used.
Fragile priority values. Priority was a plain string, so a typo like "High" would silently break sorting. I replaced it with a Priority enum.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
My scheduler looks at a few things when it builds the daily plan. The first is time. The owner has a set number of minutes each day, and the scheduler adds up the length of each task until that time runs out. If a task doesn’t fit, it is skipped and given a reason, but the scheduler keeps going in case a shorter task can still fit. The second is priority. Every task is high, medium, or low, and the most important tasks get the limited time first. If two tasks have the same priority, the shorter one goes first. The third is fixed start times. If a task has a set time, like medicine at 8:30, it keeps that time. Tasks without a set time go into the earliest open gap in the day. The scheduler also skips tasks that are already done, and a repeating task only shows up on the day it is due. Last, it checks for overlaps. If two tasks happen at the same time, it shows a warning but does not move anything. Owner preferences are not used yet.



- How did you decide which constraints mattered most?

I decided which constraints mattered most by thinking about what would cause the most harm if the scheduler got it wrong. Time came first because it is a hard limit. The owner cannot spend time they do not have. Priority came second because when time is short, the scheduler has to choose, and a medication matters more than a play session. Fixed times came third because the owner already made that choice, so the scheduler should respect it instead of changing it. Conflict warnings came last because they do not change the plan. They only tell the owner about a problem, since the scheduler cannot know which of two overlapping tasks matters more.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

One tradeoff my scheduler makes is that it warns about conflicts but doesn't fix them. If two tasks at fixed times overlap, like a walk at 08:30 and a medication at 08:30, it prints a warning. It checks the full time ranges, not just the start times. Both tasks stay in the plan and nothing gets moved.
- Why is that tradeoff reasonable for this scenario?


I did it this way because the scheduler can't tell which task matters more to the owner. If it moved the medication on its own, the pet could get its medicine late, and the owner might never notice. So I let the owner decide. It also keeps the code simpler, and a conflict never crashes the program.

The downside is that the owner has to fix the conflict themselves, and the plan can still contain two things at the same time.

To make this less of a problem, tasks without a set time are put in the first open gap around the tasks that do have one. That way the scheduler never causes a conflict by itself. The only conflicts left are ones the owner set up.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used AI at several stages of the project.

Design review: After I wrote my class skeleton, I asked an AI assistant to look for missing relationships and logic problems. It found the redundant Owner and Pet references in the Scheduler, the missing place to store skip reasons, and the fragile string priorities. These led to my Plan object and Priority enum.
Gap checking: I pasted the assignment requirements and asked what I hadn't covered. That showed I was missing task frequency, completion status, multiple pets, and an Owner.get_all_tasks() method. I added all four.
Scaffolding and implementation: I used the AI to fill in the method bodies for my four classes, then write a main.py demo and two starter tests.
Readability: I asked for suggestions on formatting the terminal schedule, then picked the table layout and asked for the emoji to be removed.
Documentation: I used it to add docstrings and to draft a README summary.


- What kinds of prompts or questions were most helpful?

The most helpful prompts were specific and gave the AI something to check against. "Review my skeleton for missing relationships and logic bottlenecks" and "did we cover this?" 


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
When I asked the AI to suggest a clearer format for the terminal schedule, it proposed a table layout with an emoji in the title. I liked the table, with its aligned columns, time ranges and a separate skipped section. I didn't want the emoji, because they can render badly in some terminals and they added nothing to the information, so I removed it.



- How did you evaluate or verify what the AI suggested?

 I also didn't assume the AI's code matched the assignment. I took the specific requirements from the instructions and checked them one by one against what had been built: task frequency, completion status, multiple pets, and an Owner.get_all_tasks() method. That check showed that all four were missing. The biggest gap was that the design only supported one pet. Owner held a single pet, and the Scheduler read from that one pet, so the Scheduler couldn't plan across several pets. I had the AI change Owner to hold a list of pets, add get_all_tasks(), and make the Scheduler read from that method. I then ran a plan with two pets and checked that tasks from both appeared, each labeled with the right pet.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
 wrote two automated tests. One checks that mark_complete() changes a task's status from not done to done. The other checks that adding a task to a pet raises the pet's task count.

I also checked the scheduling behavior by running main.py and the Streamlit app. I looked at whether tasks come out sorted by time, whether filtering by pet and by status gives the right tasks, whether completing a daily task creates a new one for tomorrow, and whether two tasks at the same time produce a warning instead of crashing.

- Why were these tests important?
Everything else depends on these basics. If a task can't be marked complete, the recurring task logic can't work. If adding a task doesn't update the pet, the scheduler has nothing to plan. Running the full program also showed me that all the classes work together, not just on their own.



**b. Confidence**

- How confident are you that your scheduler works correctly?

Confident about the main behavior, and less sure about unusual cases. I wrote tests for the things the scheduler is supposed to do and all passes

- What edge cases would you test next if you had more time?

A task longer than the owner's whole day. It should be skipped with a clear reason. I haven't tested that this works.

Owner preferences. My Owner class stores preferences, but the scheduler doesn't use them yet. Once it does, I would test what happens when a preference conflicts with a task's fixed time. For example, if the owner prefers no tasks before 09:00 but a medication is set for 08:30, the scheduler has to decide which one wins.





---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The Schedular logic part

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
The first thing I’d change is how the scheduler handles conflicts. Right now it only warns. That was a deliberate choice, because the scheduler can’t know which task matters more to the owner and a medication shouldn’t be moved silently. But the owner is left to fix the overlap alone. I’d keep the “never move anything automatically” rule and have the scheduler suggest a fix, such as the next free gap for the lower-priority task, so the owner can accept it with one click.

I’d add persistence. The app keeps everything in st.session_state, so a refresh wipes the owner, pets, and tasks. Saving to a JSON file would make it usable day to day.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
AI can produce code quickly, but it doesn’t own the design, and I do. Its first-pass output matched the code I asked for, not necessarily the requirements, and the single-pet limitation only surfaced because I checked the build against the assignment line by line. My job was to decide what each class is responsible for, to judge which suggestions fit that design, and to verify behavior by running it. Examples are the two-pet plan and the same-time conflict that produces a warning instead of a crash. The best results came from specific prompts that gave the AI something to check against, with the final decisions staying with me.