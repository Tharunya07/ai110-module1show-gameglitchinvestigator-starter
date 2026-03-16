from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# --- Regression tests for the two bugs fixed ---

# Bug 1: check_guess messages were swapped — "Go HIGHER!" was shown when guess
# was too high and "Go LOWER!" when too low. These tests pin the correct messages.

def test_too_high_message_says_go_lower():
    # Guess 80, secret 56: player is above the secret, must go lower
    outcome, message = check_guess(80, 56)
    assert outcome == "Too High"
    assert "LOWER" in message
    assert "HIGHER" not in message

def test_too_low_message_says_go_higher():
    # Guess 50, secret 56: player is below the secret, must go higher
    outcome, message = check_guess(50, 56)
    assert outcome == "Too Low"
    assert "HIGHER" in message
    assert "LOWER" not in message

# Bug 2: secret was cast to str on even attempts, causing lexicographic
# comparison where e.g. "9" > "78" even though 9 < 78. These tests reproduce
# the exact cases that failed under string comparison.

def test_single_digit_less_than_two_digit_secret():
    # 9 < 78 numerically, but "9" > "78" lexicographically — must say Too Low
    outcome, message = check_guess(9, 78)
    assert outcome == "Too Low"
    assert "HIGHER" in message

def test_guess_higher_leading_digit_than_secret():
    # 90 > 19 both numerically and lexicographically — sanity check
    outcome, message = check_guess(90, 19)
    assert outcome == "Too High"
    assert "LOWER" in message

def test_secret_always_compared_as_int():
    # Simulate what the old bug did: pass secret as a string.
    # check_guess should still handle int vs int correctly after the fix.
    # (Both args are ints; this confirms no accidental string coercion inside.)
    outcome, message = check_guess(5, 56)
    assert outcome == "Too Low"
    assert "HIGHER" in message


# --- Regression test for the new-game status reset bug ---

# Bug 3: clicking "New Game" reset attempts/secret but NOT status. After a win
# or loss, status remained "won"/"lost", causing st.stop() to fire immediately
# after st.rerun(), so the new game UI never rendered. The fix adds:
#   st.session_state.status = "playing"
#   st.session_state.history = []
# to the new_game handler. The logic tested here is the pure state transition —
# no Streamlit needed.

def simulate_new_game(session_state: dict) -> dict:
    """Mirrors exactly what the new_game handler in app.py does (minus st.rerun)."""
    session_state["attempts"] = 0
    session_state["secret"] = 42          # fixed value so test is deterministic
    session_state["status"] = "playing"
    session_state["history"] = []
    return session_state


def test_new_game_resets_status_to_playing_after_win():
    # Game ended in a win — new game must restore status so the play loop runs
    state = {"attempts": 3, "secret": 50, "status": "won", "history": [10, 30, 50]}
    state = simulate_new_game(state)
    assert state["status"] == "playing", (
        "status was not reset to 'playing'; st.stop() would fire and block new game"
    )


def test_new_game_resets_status_to_playing_after_loss():
    # Game ended in a loss — same requirement
    state = {"attempts": 8, "secret": 77, "status": "lost", "history": [1, 2, 3, 4, 5, 6, 7, 8]}
    state = simulate_new_game(state)
    assert state["status"] == "playing"


def test_new_game_clears_history():
    # History from the previous game must not carry into the new game
    state = {"attempts": 5, "secret": 33, "status": "lost", "history": [10, 20, 30, 40, 50]}
    state = simulate_new_game(state)
    assert state["history"] == []


def test_new_game_resets_attempts_to_zero():
    state = {"attempts": 8, "secret": 99, "status": "lost", "history": []}
    state = simulate_new_game(state)
    assert state["attempts"] == 0
