with open("worker/Dockerfile", "r") as f:
    content = f.read()

content = content.replace("COPY worker/parser.py /app/parser.py\n", "COPY worker/parser.py /app/parser.py\nCOPY worker/scripts /app/scripts\n")

with open("worker/Dockerfile", "w") as f:
    f.write(content)
