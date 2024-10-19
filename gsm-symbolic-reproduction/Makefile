# Makefile for symbolic conversion of GSM8K dataset

PYTHON := python3
VENV := venv
ARROW_INSTALLED := .arrow_installed
DATASETS_DIR := datasets/openai-gsm8k/main
OUTPUT_DIR := datasets/gsm8k-symbolic-reconstruction/main
INTERMEDIATE_DIR := .intermediate

.PHONY: all clean light-run install-deps help convert process-dataset parquet-to-jsonl jsonl-to-parquet

all: process-dataset

light-run: $(VENV) parquet-to-jsonl
	@echo "Processing a small subset of the dataset..."
	@mkdir -p $(OUTPUT_DIR)
	@head -n 10 $(INTERMEDIATE_DIR)/train-00000-of-00001.jsonl | \
	go run symbolize_gsm8k.go > $(OUTPUT_DIR)/train-light-run.jsonl
	@echo "Light run complete. Output saved to $(OUTPUT_DIR)/train-light-run.jsonl"

light-run-py: $(VENV) parquet-to-jsonl
	@echo "Processing a small subset of the dataset..."
	@mkdir -p $(OUTPUT_DIR)
	@head -n 10 $(INTERMEDIATE_DIR)/train-00000-of-00001.jsonl | \
	$(VENV)/bin/python symbolize_gsm8k.py > $(OUTPUT_DIR)/train-light-run.jsonl
	@echo "Light run complete. Output saved to $(OUTPUT_DIR)/train-light-run.jsonl"

$(VENV): requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

clean:
	rm -rf $(VENV) $(OUTPUT_DIR) $(INTERMEDIATE_DIR) requirements.txt $(ARROW_INSTALLED)

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

requirements.txt: requirements.in
	$(VENV)/bin/pip-compile requirements.in

update-deps: $(VENV)
	$(VENV)/bin/pip-compile --upgrade requirements.in
	$(VENV)/bin/pip install -r requirements.txt

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  all               Process the entire dataset"
	@echo "  light-run         Process a small subset of the dataset"
	@echo "  clean             Remove generated files and virtual environment"
	@echo "  install-deps      Install system dependencies (including Arrow)"
	@echo "  update-deps       Update Python dependencies"
	@echo "  process-dataset   Convert the entire dataset to symbolic form"
	@echo "  parquet-to-jsonl  Convert Parquet files to JSONL"
	@echo "  jsonl-to-parquet  Convert JSONL files to Parquet"
	@echo "  help              Show this help message"

convert:
	@echo "Converting word problem to symbolic template..."
	@template-populator -verbose -template convert.prompt.txt <<< "{\"question\": \"$(QUESTION)\", \"answer\": \"$(ANSWER)\"}" | cgpt | xq -j | jq -c '{q: .symbolic_template_question, a: .symbolic_template_answer}'

process-dataset: $(VENV) parquet-to-jsonl
	@echo "Processing GSM8K dataset..."
	@mkdir -p $(OUTPUT_DIR)
	@for dataset in train test; do \
		echo "Processing $$dataset set..."; \
		cat $(INTERMEDIATE_DIR)/$$dataset-00000-of-00001.jsonl | \
		$(VENV)/bin/python symbolize_gsm8k.py > $(OUTPUT_DIR)/$$dataset-00000-of-00001.jsonl; \
	done
	@echo "Dataset processing complete."
	@$(MAKE) jsonl-to-parquet

parquet-to-jsonl: $(VENV)
	@echo "Converting Parquet files to JSONL..."
	@mkdir -p $(INTERMEDIATE_DIR)
	@for dataset in train test; do \
		echo "Converting $$dataset set..."; \
		$(VENV)/bin/python -c "import pandas as pd; df = pd.read_parquet('$(DATASETS_DIR)/$$dataset-00000-of-00001.parquet', engine='pyarrow'); df.to_json('$(INTERMEDIATE_DIR)/$$dataset-00000-of-00001.jsonl', orient='records', lines=True)"; \
	done

jsonl-to-parquet: $(VENV)
	@echo "Converting JSONL files to Parquet..."
	@for dataset in train test; do \
		echo "Converting $$dataset set..."; \
		$(VENV)/bin/python -c "import pandas as pd; df = pd.read_json('$(OUTPUT_DIR)/$$dataset-00000-of-00001.jsonl', lines=True); df.to_parquet('$(OUTPUT_DIR)/$$dataset-00000-of-00001.parquet', engine='pyarrow', index=False)"; \
	done
