package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
)

type QAPair struct {
	Question string `json:"question"`
	Answer   string `json:"answer"`
}

func runCommand(command string, args ...string) (string, error) {
	cmd := exec.Command(command, args...)
	cmd.Stderr = os.Stderr
	output, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("error executing command '%s': %w", command, err)
	}
	return string(output), nil
}

func convertProblem(rowNumber int, question, answer string) (string, error) {
	example := QAPair{
		Question: question,
		Answer:   answer,
	}
	prompt, err := json.Marshal(example)
	if err != nil {
		errorInput, _ := json.Marshal(map[string]interface{}{"row": rowNumber, "input": example})
		fmt.Printf("\n%s\n", errorInput)
		return "", fmt.Errorf("error marshalling example: %w", err)
	}

	templateOutput, err := runCommand("template-populator", "-template", "convert.prompt.txt", "-strict", "-verbose", string(prompt))
	if err != nil {
		errorInput, _ := json.Marshal(map[string]interface{}{"row": rowNumber, "input": string(prompt)})
		fmt.Printf("\n%s\n", errorInput)
		return "", fmt.Errorf("template command failed: %w", err)
	}

	cgptCmd := exec.Command("cgpt")
	cgptCmd.Stdin = strings.NewReader(templateOutput)
	cgptCmd.Stderr = os.Stderr
	cgptOutput, err := cgptCmd.Output()
	if err != nil {
		errorInput, _ := json.Marshal(map[string]interface{}{"row": rowNumber, "input": templateOutput})
		fmt.Printf("\n%s\n", errorInput)
		return "", fmt.Errorf("cgpt command failed: %w", err)
	}

	xqCmd := exec.Command("xq", "-j")
	xqCmd.Stdin = strings.NewReader(string(cgptOutput))
	xqCmd.Stderr = os.Stderr
	xqOutput, err := xqCmd.Output()
	if err != nil {
		errorInput, _ := json.Marshal(map[string]interface{}{"row": rowNumber, "input": string(cgptOutput)})
		fmt.Printf("\n%s\n", errorInput)
		return "", fmt.Errorf("xq command failed: %w", err)
	}

	jqCmd := exec.Command("jq", "-c", "{question: .symbolic_template_question, answer: .symbolic_template_answer}")
	jqCmd.Stdin = bytes.NewReader(xqOutput)
	jqCmd.Stderr = os.Stderr
	finalOutput, err := jqCmd.Output()
	if err != nil {
		errorInput, _ := json.Marshal(map[string]interface{}{"row": rowNumber, "input": string(xqOutput)})
		fmt.Printf("\n%s\n", errorInput)
		return "", fmt.Errorf("jq command failed: %w", err)
	}

	output := string(finalOutput)
	return strings.TrimSpace(output), nil
}

func main() {
	logger := log.New(os.Stderr, "", log.LstdFlags)
	logger.Println("Starting conversion...")
	scanner := bufio.NewScanner(os.Stdin)
	rowNumber := 0
	for scanner.Scan() {
		rowNumber++
		line := scanner.Text()
		logger.Println(line)
		var data map[string]string
		if err := json.Unmarshal([]byte(line), &data); err != nil {
			logger.Printf("Error parsing JSON: %v\n", err)
			errorInput, _ := json.Marshal(map[string]interface{}{"row": rowNumber, "input": line})
			fmt.Printf("\n%s\n", errorInput)
			continue
		}
		result, err := convertProblem(rowNumber, data["question"], data["answer"])
		if err != nil {
			logger.Printf("Error converting problem: %v\n", err)
			continue
		}
		fmt.Println(result)
	}
	if err := scanner.Err(); err != nil {
		logger.Fatalf("Error reading input: %v\n", err)
	}
}
