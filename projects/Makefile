GOOGLE3_BASE := /google/src/cloud/guyu/theg/google3/experimental/users/guyu

# Get the project name from the command line arguments
# We filter out the known targets to find the project name argument
TARGETS := release dry-release release-skills dry-release-skills
PROJECT := $(firstword $(filter-out $(TARGETS),$(MAKECMDGOALS)))

# Find all subdirectories to register them as phony targets
# This prevents "No rule to make target 'g3lobster'" errors
PROJECTS := $(patsubst %/,%,$(wildcard */))

.PHONY: $(TARGETS) $(PROJECTS)

# No-op rule for project names so make doesn't complain
$(PROJECTS):
	@:

# Helper to construct rsync options
# Dynamic check for .gitignore to avoid errors if it doesn't exist
RSYNC_EXCLUDES = --exclude=.git --exclude=.DS_Store --exclude=.venv --exclude=__pycache__ --exclude=*.pyc
RSYNC_FLAGS = -avh --delete $(RSYNC_EXCLUDES)

GOOGLE3_SKILLS_BASE := /google/src/cloud/guyu/theg/google3/devtools/devassist/gemini_cli_for_google/extensions/coding/skills

release-skills:
	@echo "Syncing custom skills to $(GOOGLE3_SKILLS_BASE)..."
	cp -RLf ../.gemini/skills/* $(GOOGLE3_SKILLS_BASE)/

dry-release-skills:
	@echo "[DRY RUN] Syncing custom skills to $(GOOGLE3_SKILLS_BASE)..."
	@echo "cp -RLf ../.gemini/skills/* $(GOOGLE3_SKILLS_BASE)/"

release:
	@if [ -z "$(PROJECT)" ]; then \
		echo "Usage: make release <project_name>"; \
		echo "Available projects: $(PROJECTS)"; \
		exit 1; \
	fi
	@if [ "$(PROJECT)" = "cdw-2026" ]; then \
		echo "Syncing $(PROJECT) site to CNS..."; \
		fileutil mkdir -p /cns/yv-d/home/guyu/projects/$(PROJECT); \
		fileutil cp -f -R $(PROJECT)/site/* /cns/yv-d/home/guyu/projects/$(PROJECT)/; \
		fileutil chmod -R a+rx /cns/yv-d/home/guyu/projects/$(PROJECT); \
		echo "Sync complete. Accessible to all Googlers at /cns/yv-d/home/guyu/projects/$(PROJECT)/index.html"; \
	else \
		echo "Syncing $(PROJECT) to $(GOOGLE3_BASE)/$(PROJECT)..."; \
		mkdir -p $(GOOGLE3_BASE)/$(PROJECT); \
		IGNORE_FLAG=""; \
		if [ -f "$(PROJECT)/.gitignore" ]; then \
			IGNORE_FLAG="--exclude-from=$(PROJECT)/.gitignore"; \
		fi; \
		rsync $(RSYNC_FLAGS) $$IGNORE_FLAG $(PROJECT)/ $(GOOGLE3_BASE)/$(PROJECT)/; \
	fi

dry-release:
	@if [ -z "$(PROJECT)" ]; then \
		echo "Usage: make dry-release <project_name>"; \
		exit 1; \
	fi
	@if [ "$(PROJECT)" = "cdw-2026" ]; then \
		echo "[DRY RUN] Syncing $(PROJECT) site to CNS..."; \
		echo "fileutil mkdir -p /cns/yv-d/home/guyu/projects/$(PROJECT)"; \
		echo "fileutil cp -f -R $(PROJECT)/site/* /cns/yv-d/home/guyu/projects/$(PROJECT)/"; \
		echo "fileutil chmod -R a+rx /cns/yv-d/home/guyu/projects/$(PROJECT)"; \
	else \
		echo "[DRY RUN] Syncing $(PROJECT) to $(GOOGLE3_BASE)/$(PROJECT)..."; \
		IGNORE_FLAG=""; \
		if [ -f "$(PROJECT)/.gitignore" ]; then \
			IGNORE_FLAG="--exclude-from=$(PROJECT)/.gitignore"; \
		fi; \
		rsync -n $(RSYNC_FLAGS) $$IGNORE_FLAG $(PROJECT)/ $(GOOGLE3_BASE)/$(PROJECT)/; \
	fi
