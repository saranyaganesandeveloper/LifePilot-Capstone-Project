✔️ LifePilot Test Cases (Functional Coverage)
### 1. Meal Planning Tests
Test 1 — Multi-day

Input:

Plan a 4-day vegetarian South Indian meal plan.


Expected:

4 day–structured plan

No non-vegetarian items

Must apply preferences & allergies

Test 2 — Single meal

Input:

What should I cook tonight?


Expected:

Only 1 meal, no Day 1/2 format

Should trigger meal agent only

2. Shopping List Tests
Test 3 — Only shopping list

Input:

Make a shopping list for this:
Day 1: Veggie fried rice
Day 2: Paneer tikka and roti


Expected:

NO meal plan agent run

Only shopping agent

Clean JSON output

3. Travel Planning Tests
Test 4 — Restaurant-only travel

Input:

Plan a 2-day trip to Dallas with vegetarian restaurants.


Expected:

Travel = true

Meal = false

Shopping = false

Test 5 — Exact-day inference

Input:

Plan a one day trip to Austin.


Expected:

1-day itinerary only

Travel agent detects "one day" correctly

4. Multi-intent
Test 6 — Meals + Shopping + Travel

Input:

Plan next week: meals, groceries, and a 1-day trip to Austin.


Expected:

meal = true

shopping = true

travel = true

5. Preference Memory
Test 7 — Long-term user food preferences

Step 1:

I am allergic to peanuts.


Step 2:

Plan meals for 2 days.


Expected:

No peanut/pb oil items

Validators scrub risky suggestions