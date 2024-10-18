import os
import subprocess
import json
import argparse
import pandas as pd

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(f"Error message: {stderr.decode('utf-8')}")
        exit(1)
    return stdout.decode('utf-8')

def clone_dataset():
    if not os.path.exists('datasets/openai-gsm8k'):
        run_command('git submodule update --init datasets/openai-gsm8k')

def convert_to_jsonl(input_file, output_file):
    df = pd.read_parquet(input_file)
    with open(output_file, 'w') as f:
        for _, row in df.iterrows():
            json.dump({'question': row.question, 'answer': row.answer}, f)
            f.write('\n')

def process_data(input_file, output_file, light_run=False):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for i, line in enumerate(f_in):
            if light_run and i >= 2:
                break
            data = json.loads(line)
            prompt = open('convert.prompt.txt', 'r').read().format(**data)
            result = run_command(f'echo "{prompt}" | cgpt --model gpt-3.5-turbo --temperature 0.7 --max-tokens 150')

            f_out.write(result)

def convert_to_parquet(input_file, output_file):
    df = pd.read_json(input_file, lines=True)
    df.to_parquet(output_file, index=False)

def main(light_run=False):
    clone_dataset()

    for dataset in ['train', 'test']:
        input_parquet = f'datasets/openai-gsm8k/main/{dataset}-00000-of-00001.parquet'
        intermediate_jsonl = f'.intermediate/{dataset}.jsonl'
        output_jsonl = f'datasets/gsm8k-symbolic-reconstruction/main/{dataset}-00000-of-00001.jsonl'
        output_parquet = f'datasets/gsm8k-symbolic-reconstruction/main/{dataset}-00000-of-00001.parquet'

        convert_to_jsonl(input_parquet, intermediate_jsonl)
        process_data(intermediate_jsonl, output_jsonl, light_run)
        convert_to_parquet(output_jsonl, output_parquet)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate symbolic reconstruction dataset")
    parser.add_argument('--light-run', action='store_true', help='Run on a small subset of data')
    args = parser.parse_args()

    main(light_run=args.light_run)
