GOOGLE3_BASE := /google/src/cloud/guyu/theg/google3/experimental/users/guyu

# Get the project name from the command line arguments
# We filter out the known targets to find the project name argument
TARGETS := release dry-release
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

release:
	@if [ -z "$(PROJECT)" ]; then \
		echo "Usage: make release <project_name>"; \
		echo "Available projects: $(PROJECTS)"; \
		exit 1; \
	fi
	@echo "Syncing $(PROJECT) to $(GOOGLE3_BASE)/$(PROJECT)..."
	@mkdir -p $(GOOGLE3_BASE)/$(PROJECT)
	@IGNORE_FLAG=""; \
	if [ -f "$(PROJECT)/.gitignore" ]; then \
		IGNORE_FLAG="--exclude-from=$(PROJECT)/.gitignore"; \
	fi; \
	rsync $(RSYNC_FLAGS) $$IGNORE_FLAG $(PROJECT)/ $(GOOGLE3_BASE)/$(PROJECT)/

dry-release:
	@if [ -z "$(PROJECT)" ]; then \
		echo "Usage: make dry-release <project_name>"; \
		exit 1; \
	fi
	@echo "[DRY RUN] Syncing $(PROJECT) to $(GOOGLE3_BASE)/$(PROJECT)..."
	@IGNORE_FLAG=""; \
	if [ -f "$(PROJECT)/.gitignore" ]; then \
		IGNORE_FLAG="--exclude-from=$(PROJECT)/.gitignore"; \
	fi; \
	rsync -n $(RSYNC_FLAGS) $$IGNORE_FLAG $(PROJECT)/ $(GOOGLE3_BASE)/$(PROJECT)/
