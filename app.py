import random
import streamlit as st
from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 1

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

attempts_left = attempt_limit - st.session_state.attempts
if attempts_left <= 1:
    st.error(f"🔥 Last chance! Guess a number between {low} and {high}. Attempts left: {attempts_left}")
elif attempts_left <= 2:
    st.warning(f"⚠️ Getting close! Guess a number between {low} and {high}. Attempts left: {attempts_left}")
else:
    st.info(f"🎯 Guess a number between {low} and {high}. Attempts left: {attempts_left}")

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# FIX (user + Claude): "New Game" wasn't resetting status/history, so st.stop()
# fired after st.rerun() and blocked the new game UI. Added status = "playing"
# and history = [] to the handler so the play loop runs cleanly on reload.
if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(1, 100)
    st.session_state.status = "playing"
    st.session_state.history = []
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")

    if st.session_state.history:
        st.subheader("📋 Game Summary")
        rows = []
        for i, g in enumerate(st.session_state.history):
            if not isinstance(g, int):
                rows.append({"#": i + 1, "Guess": g, "Result": "Invalid"})
                continue
            outcome, _ = check_guess(g, st.session_state.secret)
            if outcome == "Win":
                result = "✅ Correct!"
            elif outcome == "Too High":
                result = "🔺 Too High"
            else:
                result = "🔻 Too Low"
            rows.append({"#": i + 1, "Guess": g, "Result": result})
        st.table(rows)

    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(f"❌ {err}")
    else:
        st.session_state.history.append(guess_int)

        #FIX: Removed string cast of secret on even attempts fixing new game attempts, always pass int using Claude
        outcome, message = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            diff = abs(guess_int - st.session_state.secret)
            if outcome == "Win":
                st.success(f"🎉 {message}")
            elif diff <= 5:
                st.error(f"🔥 So close! {message}")
            elif diff <= 15:
                st.warning(f"🌡️ Warm! {message}")
            else:
                st.info(f"🧊 Cold! {message}")

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"🏆 You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"💀 Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

    # Live guess history during play
    if st.session_state.history:
        with st.expander("📜 Guess History", expanded=True):
            rows = []
            for i, g in enumerate(st.session_state.history):
                if not isinstance(g, int):
                    rows.append({"#": i + 1, "Guess": g, "Result": "Invalid"})
                    continue
                o, _ = check_guess(g, st.session_state.secret)
                if o == "Win":
                    result = "✅ Correct!"
                elif o == "Too High":
                    result = "🔺 Too High"
                else:
                    result = "🔻 Too Low"
                rows.append({"#": i + 1, "Guess": g, "Result": result})
            st.table(rows)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
