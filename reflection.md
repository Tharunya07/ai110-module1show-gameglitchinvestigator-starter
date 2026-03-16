# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- A: It looked stable, until I got the answer and it did not match the guesses.
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").
  - A: the hints were the opposite ; the UI didn't refresh on its own- new game does not load until refershing the page ; the mode didn't actually change ; the UI text was stagnent saying 1-100 for all; took numbers not in the range ; submit guess does not give a "correct or incorrect" so when hiding hint you do not get feedback on if it is correct or incorrect; press enter to apply does not work.

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- A: Claude
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- A: I found the bug that the app was giving oppostie hints. I asked AI to understand why that is happenign and reason it out. This is what the AI said 
`The bug is on app.py lines 161–164:


if st.session_state.attempts % 2 == 0:
    secret = str(st.session_state.secret)  # converts to string!
else:
    secret = st.session_state.secret       # keeps as int
Why this causes inverted hints:

On even-numbered attempts, secret is converted to a string. When check_guess then falls into the except TypeError branch (line 42 in app.py), it compares str(guess) vs str(secret) using lexicographic (alphabetical) string comparison instead of numeric comparison.

With string comparison, "80" > "78" is True (since "8" == "8", then "0" < "8"... wait, actually "80" > "78" lexicographically because "8" == "7"... let me be precise):

"80" vs "78": compares char by char — "8" > "7", so "80" > "78" → this is actually correct for this pair.
But the real problem shows up for cases like guessing 9 when the secret is 78:

Lexicographically "9" > "78" (because "9" > "7") → reports "Too High"
But numerically 9 < 78 → should report "Too Low"
Root cause summary: On even attempts, the secret is cast to a string, causing check_guess to do string (lexicographic) comparison instead of numeric comparison. String ordering does not match numeric ordering whenever the digits have different leading characters (e.g., "9" > "78" even though 9 < 78), producing incorrect and seemingly inverted hints depending on the specific numbers involved.`

I checked those lines of code, understood that what the Ai said, and found it to be true. I later corrected it using the help of AI.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
- A: When I was writing the tests for the bug checks, AI suggested I put the test file in the root directory, so the ptest would recognise improts instead of changing the way we import. This would have ruined the structure abstract of the codebase.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- First, I analyzed the code canges, and tried to understand if the AI suggestion was in fact true fix and if it mattered. Later, after implementing the changes I tested using pytest, and then I manually played the app to check if it actually fixed the bug.
- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.
- I ran the test to check if the opposite hints were fixed, by running pytest for few numbers by passing it to check_guess function. Then, I manually played the game to check the logic was fixed.
- Did AI help you design or understand any tests? How?
- Yes, I initally did understand what tests meant, in pytest. I assumed it would run the app to test it, but I got to know it runs the function in a controlled environement to check the variables passed gets the desired output. That was way simple making us check if the function logic was the issue or if something else was interferring in this logical output. 

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
