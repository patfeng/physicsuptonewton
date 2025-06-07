#!/usr/bin/env python3
"""
Training Data Validator for OpenAI Fine-tuning
This script validates JSONL training data for OpenAI fine-tuning jobs.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
import re

def validate_jsonl_format(file_path: Path) -> List[Dict[str, Any]]:
    """Validate that the file is in proper JSONL format."""
    data = []
    line_num = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_num += 1
                line = line.strip()
                
                if not line:  # Skip empty lines
                    continue
                    
                try:
                    json_obj = json.loads(line)
                    data.append(json_obj)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error on line {line_num}: {e}")
                    return []
                    
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []
    
    print(f"✅ Successfully parsed {len(data)} training examples from JSONL file")
    return data

def validate_training_format(data: List[Dict[str, Any]]) -> bool:
    """Validate the training data format for fine-tuning."""
    
    if len(data) < 10:
        print(f"⚠️  Warning: Only {len(data)} examples found. OpenAI recommends at least 10-100 examples.")
    
    errors = []
    warnings = []
    
    for i, example in enumerate(data):
        # Check for required 'messages' field
        if 'messages' not in example:
            errors.append(f"Example {i+1}: Missing 'messages' field")
            continue
            
        messages = example['messages']
        
        if not isinstance(messages, list):
            errors.append(f"Example {i+1}: 'messages' must be a list")
            continue
            
        if len(messages) < 2:
            errors.append(f"Example {i+1}: Must have at least 2 messages (user and assistant)")
            continue
            
        # Validate message format
        has_user = False
        has_assistant = False
        
        for j, msg in enumerate(messages):
            if not isinstance(msg, dict):
                errors.append(f"Example {i+1}, Message {j+1}: Must be a dictionary")
                continue
                
            if 'role' not in msg:
                errors.append(f"Example {i+1}, Message {j+1}: Missing 'role' field")
                continue
                
            if 'content' not in msg:
                errors.append(f"Example {i+1}, Message {j+1}: Missing 'content' field")
                continue
                
            role = msg['role']
            content = msg['content']
            
            if role not in ['system', 'user', 'assistant']:
                errors.append(f"Example {i+1}, Message {j+1}: Invalid role '{role}'. Must be 'system', 'user', or 'assistant'")
                
            if not isinstance(content, str):
                errors.append(f"Example {i+1}, Message {j+1}: Content must be a string")
                
            if role == 'user':
                has_user = True
            elif role == 'assistant':
                has_assistant = True
                
            # Check for overly long content
            if isinstance(content, str) and len(content) > 4000:
                warnings.append(f"Example {i+1}, Message {j+1}: Content is very long ({len(content)} chars). Consider shortening.")
                
        if not has_user:
            errors.append(f"Example {i+1}: Must have at least one 'user' message")
            
        if not has_assistant:
            errors.append(f"Example {i+1}: Must have at least one 'assistant' message")
    
    # Print results
    if errors:
        print(f"\n❌ Found {len(errors)} errors:")
        for error in errors:
            print(f"  • {error}")
        return False
    else:
        print(f"✅ All {len(data)} examples have valid format!")
        
    if warnings:
        print(f"\n⚠️  Found {len(warnings)} warnings:")
        for warning in warnings:
            print(f"  • {warning}")
    
    return True

def analyze_data_distribution(data: List[Dict[str, Any]]) -> None:
    """Analyze the distribution of the training data."""
    
    print(f"\n📊 Data Analysis:")
    print(f"  • Total examples: {len(data)}")
    
    # Analyze message lengths
    user_lengths = []
    assistant_lengths = []
    total_lengths = []
    
    for example in data:
        example_length = 0
        for msg in example.get('messages', []):
            content = msg.get('content', '')
            msg_length = len(content) if isinstance(content, str) else 0
            example_length += msg_length
            
            if msg.get('role') == 'user':
                user_lengths.append(msg_length)
            elif msg.get('role') == 'assistant':
                assistant_lengths.append(msg_length)
                
        total_lengths.append(example_length)
    
    if user_lengths:
        print(f"  • User message length - Avg: {sum(user_lengths)/len(user_lengths):.0f}, Max: {max(user_lengths)}")
    
    if assistant_lengths:
        print(f"  • Assistant message length - Avg: {sum(assistant_lengths)/len(assistant_lengths):.0f}, Max: {max(assistant_lengths)}")
    
    if total_lengths:
        print(f"  • Total example length - Avg: {sum(total_lengths)/len(total_lengths):.0f}, Max: {max(total_lengths)}")

def main():
    parser = argparse.ArgumentParser(description="Validate training data for OpenAI fine-tuning")
    parser.add_argument("-f", "--file", required=True, help="Path to the JSONL training file")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress detailed output")
    
    args = parser.parse_args()
    
    file_path = Path(args.file)
    
    print(f"🔍 Validating training data: {file_path}")
    
    # Step 1: Validate JSONL format
    data = validate_jsonl_format(file_path)
    if not data:
        sys.exit(1)
    
    # Step 2: Validate training format
    if not validate_training_format(data):
        sys.exit(1)
    
    # Step 3: Analyze data distribution
    if not args.quiet:
        analyze_data_distribution(data)
    
    print(f"\n✅ Training data validation complete! Your file is ready for fine-tuning.")
    print(f"💡 Next steps:")
    print(f"  1. Upload the file: client.files.create(file=open('{file_path}', 'rb'), purpose='fine-tune')")
    print(f"  2. Create fine-tuning job: client.fine_tuning.jobs.create(training_file='file-xxx', model='gpt-3.5-turbo')")

if __name__ == "__main__":
    main() 