import json
import sys
import subprocess

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}", file=sys.stderr)
        print(f"Error message: {stderr.decode('utf-8')}", file=sys.stderr)
        sys.exit(1)
    return stdout.decode('utf-8')

def convert_problem(question, answer):
    prompt = json.dumps({"question": question, "answer": answer})
    
    template_command = f"template-populator -template convert.prompt.txt -strict -verbose '{prompt}'"
    template_output = run_command(f"{template_command}")
    print(f"Template output: {template_output}", file=sys.stderr)

    import time
    time.sleep(4)
    
    # Escape special characters and newlines for shell
    escaped_template_output = template_output.replace("'", "'\\''").replace('\n', '\\n')
    
    cgpt_output = run_command(f"cgpt -i '{escaped_template_output}'")
    print(f"CGPT output: {cgpt_output}", file=sys.stderr)
    
    # Escape special characters for echo
    escaped_cgpt_output = cgpt_output.replace("'", "'\\''")
    
    xq_command = "xq -j"
    xq_output = run_command(f"echo '{escaped_cgpt_output}' | {xq_command}")
    print(f"XQ output: {xq_output}", file=sys.stderr)
    
    # Escape special characters for echo
    escaped_xq_output = xq_output.replace("'", "'\\''")
    
    jq_command = "jq -c '{question: .symbolic_template_question, answer: .symbolic_template_answer}'"
    final_output = run_command(f"echo '{escaped_xq_output}' | {jq_command}")
    print(f"Final output: {final_output}", file=sys.stderr)
    
    return final_output

def main():
    # print to stderr:
    print("Starting conversion...", file=sys.stderr)
    for line in sys.stdin:
        print(line, file=sys.stderr)
        data = json.loads(line)
        result = convert_problem(data['question'], data['answer'])
        sys.stdout.write(result)

if __name__ == "__main__":
    main()
