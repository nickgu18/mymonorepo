DEST_DIR := $(abspath ../.gemini/skills)
SKILLS := $(patsubst %/,%,$(wildcard */))

.PHONY: all install clean

all: install

install:
	@echo "Installing skills to $(DEST_DIR)..."
	@mkdir -p $(DEST_DIR)
	@for skill in $(SKILLS); do \
		echo "  Installing $$skill..."; \
		rm -rf $(DEST_DIR)/$$skill; \
		cp -r $$skill $(DEST_DIR)/; \
	done
	@echo "Installation complete."

clean:
	@echo "Removing installed skills from $(DEST_DIR)..."
	@for skill in $(SKILLS); do \
		if [ -d "$(DEST_DIR)/$$skill" ]; then \
			echo "  Removing $$skill..."; \
			rm -rf $(DEST_DIR)/$$skill; \
		fi \
	done
	@echo "Clean complete."
