# Makefile for symbolic conversion of GSM8K dataset

PYTHON := python3
VENV := venv
ARROW_INSTALLED := .arrow_installed

.PHONY: all clean light-run install-deps help

all: $(VENV)
	$(VENV)/bin/python symbolize_gsm8k.py

light-run: $(VENV)
	$(VENV)/bin/python symbolize_gsm8k.py --light-run

$(VENV): requirements.in
	$(PYTHON) -m venv --clear $(VENV)
	$(VENV)/bin/pip install pip-tools
	$(VENV)/bin/pip-compile requirements.in
	$(VENV)/bin/pip install -r requirements.txt

clean:
	rm -rf $(VENV) datasets/gsm8k-symbolic-reconstruction .intermediate requirements.txt $(ARROW_INSTALLED)

$(ARROW_INSTALLED):
	@echo "Installing Apache Arrow C++ library..."
	@if [ "$$(uname)" = "Darwin" ]; then \
		brew install apache-arrow; \
	elif [ "$$(uname)" = "Linux" ]; then \
		sudo apt-get update && sudo apt-get install -y libarrow-dev; \
	else \
		echo "Unsupported operating system. Please install Apache Arrow manually."; \
		exit 1; \
	fi
	@echo "Apache Arrow installed successfully."
	@touch $(ARROW_INSTALLED)

install-deps: $(ARROW_INSTALLED)
	@echo "Installing OS-dependent dependencies..."
	@if [ "$$(uname)" = "Linux" ]; then \
		sudo apt update && \
		sudo apt install -y python3-venv python3-pip jq nodejs npm golang-go && \
		sudo npm install -g promptfoo; \
	elif [ "$$(uname)" = "Darwin" ]; then \
		brew update && \
		brew install python jq node go promptfoo; \
	else \
		echo "Unsupported operating system. Please install dependencies manually."; \
		exit 1; \
	fi
	@echo "Installing Go dependencies..."
	@go install github.com/tmc/misc/template-populator@latest
	@go install github.com/tmc/cgpt/cmd/cgpt@latest
	@go install github.com/tmc/xq@add-json-mode
	@echo "If Go binaries are not found after installation, add $$(go env GOPATH)/bin to your PATH:"
	@echo "export PATH=\$$PATH:$$(go env GOPATH)/bin"

requirements.txt: requirements.in
	$(VENV)/bin/pip-compile requirements.in

update-deps: $(VENV)
	$(VENV)/bin/pip-compile --upgrade requirements.in
	$(VENV)/bin/pip install -r requirements.txt

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  all	   Run the full symbolic conversion pipeline"
	@echo "  light-run     Run the pipeline on a small subset of data"
	@echo "  clean	 Remove generated files and virtual environment"
	@echo "  install-deps  Install system dependencies (including Arrow)"
	@echo "  update-deps   Update Python dependencies"
	@echo "  help	  Show this help message"

convert: ## Convert a word problem to symbolic template
	@echo "Converting word problem to symbolic template..."
	@template-populator -verbose -template convert.prompt.txt <<< "{\"question\": \"$(QUESTION)\", \"answer\": \"$(ANSWER)\"}" | cgpt | xq -j | jq '{question: .symbolic_template_question, answer: .symbolic_template_answer}'
