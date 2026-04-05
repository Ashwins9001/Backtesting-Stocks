import time

def simulate_live(data, strategy):
    for i in range(len(data)):
        current_slice = data.iloc[:i+1]
        signal = strategy.generate_signals(current_slice).iloc[-1]

        print(f"Step {i}: Signal = {signal}")
        time.sleep(0.1)  # simulate time passing