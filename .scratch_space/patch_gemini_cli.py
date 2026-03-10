import re

file_path = "/usr/local/google/home/guyu/Desktop/mymonorepo/projects/harbor/src/harbor/agents/installed/gemini_cli.py"
with open(file_path, "r") as f:
    content = f.read()

# I will replace each conflict block using precise string replacement.

# Conflict 1
c1 = """<<<<<<< HEAD
import asyncio
=======
import base64
>>>>>>> upstream/main"""
content = content.replace(c1, "import asyncio\nimport base64")

# Conflict 2
c2 = """<<<<<<< HEAD
from typing import Any
import warnings

from harbor.agents.installed.base import BaseInstalledAgent, ExecInput
from harbor.environments.base import BaseEnvironment
from harbor.environments.docker.docker import DockerEnvironment
=======
from typing import Any, Literal

from harbor.agents.installed.base import BaseInstalledAgent, CliFlag, ExecInput
>>>>>>> upstream/main"""
content = content.replace(c2, """from typing import Any, Literal
import warnings

from harbor.agents.installed.base import BaseInstalledAgent, CliFlag, ExecInput
from harbor.environments.base import BaseEnvironment
from harbor.environments.docker.docker import DockerEnvironment""")

with open(file_path, "w") as f:
    f.write(content)
