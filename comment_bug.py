import urllib.request
import json
import sys

def comment_on_bug():
    url = "https://issuetracker.google.com/issues/484405237"
    print("Could not find a local buganizer cli. This would require authenticated API access.")

if __name__ == "__main__":
    comment_on_bug()
