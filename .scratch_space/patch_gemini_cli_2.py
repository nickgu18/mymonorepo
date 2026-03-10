import re

file_path = "/usr/local/google/home/guyu/Desktop/mymonorepo/projects/harbor/src/harbor/agents/installed/gemini_cli.py"
with open(file_path, "r") as f:
    content = f.read()

start_marker = "<<<<<<< HEAD"
mid_marker = "======="
end_marker = ">>>>>>> upstream/main"

# We'll extract blocks and print them to see what needs to be kept.
parts = content.split(start_marker)
for i, part in enumerate(parts[1:], 1):
    mid_idx = part.find(mid_marker)
    end_idx = part.find(end_marker)
    if mid_idx != -1 and end_idx != -1:
        head_block = part[:mid_idx]
        upstream_block = part[mid_idx + len(mid_marker):end_idx]
        print(f"--- BLOCK {i} HEAD ---")
        print(head_block[:200])
        print("...")
        print(f"--- BLOCK {i} UPSTREAM ---")
        print(upstream_block[:200])
        print("...\n")
