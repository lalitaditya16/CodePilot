import sys
from dotenv import load_dotenv
from langgraph.types import Command

from graph import build_graph

load_dotenv()

SAMPLE_CODE = """
def process_user_data(user_id, data):
    query = "SELECT * FROM users WHERE id = " + user_id
    result = db.execute(query)

    for i in range(len(data)):
        if data[i] > 0:
            process(data[i])

    password = "admin123"
    return result


def calculate_stats(numbers):
    total = 0
    for i in range(len(numbers) + 1):
        total += numbers[i]
    avg = total / len(numbers)
    return total, avg
"""


def run(code: str):
    graph = build_graph()
    config = {"configurable": {"thread_id": "review"}}

    print("\nStarting CodePilot analysis...\n")

    # Run until the human_review interrupt fires
    for event in graph.stream({"code": code}, config, stream_mode="updates"):
        for node in event:
            if node not in ("__interrupt__",):
                print(f"  [{node}] done")

    # Check if paused at human_review
    snapshot = graph.get_state(config)
    if snapshot.next:
        # Print the review summary once — passed as the interrupt value
        for task in snapshot.tasks:
            for intr in getattr(task, "interrupts", []):
                print(intr.value)

        feedback = input("\nEnter feedback (or 'approve'): ").strip() or "approve"
        for event in graph.stream(Command(resume=feedback), config, stream_mode="updates"):
            for node in event:
                if node not in ("__interrupt__",):
                    print(f"  [{node}] done")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            code = f.read()
    else:
        code = SAMPLE_CODE
        print("No file provided — using sample code.\n")

    run(code)
