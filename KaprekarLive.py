import streamlit as st

# European Roulette Wheel layout
wheel_order = [
    32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27,
    13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1,
    20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
]

# Create 12 groups from wheel order (3 numbers per group)
group_map = {i + 1: wheel_order[i * 3:(i + 1) * 3] for i in range(12)}

def map_to_groups(numbers):
    groups = []
    for num in numbers:
        if num == 0:
            continue  # Zero is wild
        for group, values in group_map.items():
            if num in values:
                groups.append(group)
                break
    return groups

def generate_seed(groups):
    seed_digits = [str(g) for g in groups[-4:]]
    seed = int("".join(seed_digits))
    return seed

def kaprekar_steps(number):
    steps = []
    current = number
    seen = set()

    while current != 6174:
        digits = f"{current:04d}"
        asc = int("".join(sorted(digits)))
        desc = int("".join(sorted(digits, reverse=True)))
        current = desc - asc

        if current in seen or current == 0:
            return steps, False
        seen.add(current)
        steps.append((desc, asc, current))

    return steps, True

def predict_bets(seed):
    digits = [int(d) for d in str(seed)]
    return [((d % 12) + 1) for d in digits[:3]]

# Streamlit app
def main():
    st.set_page_config(page_title="Kaprekar Roulette", layout="wide")

    # Sidebar setup
    initial_bankroll = st.sidebar.number_input("Bankroll (units)", min_value=0, value=120)
    st.sidebar.write("Payout Rate: 36 to 1")
    st.sidebar.write("Seed Cost: 12 units")

    # Session state
    if "spin_count" not in st.session_state:
        st.session_state.spin_count = 0
    if "hit_count" not in st.session_state:
        st.session_state.hit_count = 0
    if "loss_count" not in st.session_state:
        st.session_state.loss_count = 0
    if "balance" not in st.session_state:
        st.session_state.balance = initial_bankroll

    # Header
    st.title("Kaprekar Roulette")

    # Input
    numbers_input = st.text_input("Enter 12 numbers", "32,15,19,4,21,2,25,17,34,6,27,13")
    numbers = [int(n.strip()) for n in numbers_input.split(",") if n.strip().isdigit()]

    if st.button("Spin"):
        if len(numbers) != 12:
            st.error("Enter exactly 12 roulette numbers.")
            return

        groups = map_to_groups(numbers)

        if len(groups) < 4:
            st.warning("Insufficient valid group mappings. Try again.")
            return

        seed = generate_seed(groups)
        st.markdown(f"Seed: **{seed}**")

        steps, success = kaprekar_steps(seed)

        st.markdown("Steps:")
        for i, (desc, asc, result) in enumerate(steps, 1):
            st.write(f"{i}. {desc} - {asc} = {result}")

        st.session_state.spin_count += 1

        if success:
            prediction = predict_bets(steps[-1][2])
            st.markdown(f"Prediction Groups: **{prediction}**")

            # Simulated hit logic — if any prediction matches last 3 groups
            hit = any(p in groups[-3:] for p in prediction)

            if hit:
                payout = 36
                st.session_state.hit_count += 1
                st.session_state.balance += payout - 12
                st.success(f"Hit! Won {payout} units. Net: +{payout - 12}")
            else:
                st.session_state.loss_count += 1
                st.session_state.balance -= 12
                st.error("Missed. Lost 12 units.")
        else:
            st.warning("Dead end. Restart session with new input.")

        # Stats
        st.markdown("---")
        st.markdown(f"Balance: **{st.session_state.balance} units**")
        st.markdown(f"Spins: {st.session_state.spin_count} | Hits: {st.session_state.hit_count} | Losses: {st.session_state.loss_count}")

if __name__ == "__main__":
    main()
