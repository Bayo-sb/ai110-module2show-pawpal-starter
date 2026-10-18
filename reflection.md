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

The classes connect in a clear chain. An Owner has one Pet, and a Pet has many Tasks. The Scheduler depends on the Owner and the Pet to read their information, and it creates the PlannedTasks. Each PlannedTask wraps one Task. This design keeps each class focused on one job, which makes the app easier to understand and change later.


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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
