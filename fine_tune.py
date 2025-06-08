#!/usr/bin/env python3
"""
Modern OpenAI Fine-tuning Example
This shows how to upload training data and create fine-tuning jobs using the new OpenAI client.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def upload_training_file(file_path: str) -> str:
    """Upload a training file and return the file ID."""
    print(f"📤 Uploading training file: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            response = client.files.create(
                file=f,
                purpose="fine-tune"
            )
        
        file_id = response.id
        print(f"✅ File uploaded successfully! File ID: {file_id}")
        return file_id
        
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return None

def create_fine_tuning_job(training_file_id: str, model: str = "gpt-3.5-turbo") -> str:
    """Create a fine-tuning job and return the job ID."""
    print(f"🚀 Starting fine-tuning job with model: {model}")
    
    try:
        response = client.fine_tuning.jobs.create(
            training_file=training_file_id,
            model=model,
            hyperparameters={
                "n_epochs": 3  # You can adjust this
            }
        )
        
        job_id = response.id
        print(f"✅ Fine-tuning job created! Job ID: {job_id}")
        print(f"📊 Status: {response.status}")
        return job_id
        
    except Exception as e:
        print(f"❌ Error creating fine-tuning job: {e}")
        return None

def check_job_status(job_id: str):
    """Check the status of a fine-tuning job."""
    try:
        response = client.fine_tuning.jobs.retrieve(job_id)
        
        print(f"\n📋 Job Status for {job_id}:")
        print(f"  • Status: {response.status}")
        print(f"  • Model: {response.model}")
        print(f"  • Created: {response.created_at}")
        
        if response.finished_at:
            print(f"  • Finished: {response.finished_at}")
            
        if response.fine_tuned_model:
            print(f"  • Fine-tuned model: {response.fine_tuned_model}")
            
        if response.error:
            print(f"  • Error: {response.error}")
            
        return response.status
        
    except Exception as e:
        print(f"❌ Error checking job status: {e}")
        return None

def list_fine_tuning_jobs():
    """List all fine-tuning jobs."""
    try:
        response = client.fine_tuning.jobs.list(limit=10)
        
        print(f"\n📜 Recent Fine-tuning Jobs:")
        for job in response.data:
            status_emoji = "✅" if job.status == "succeeded" else "⏳" if job.status in ["running", "validating_files"] else "❌"
            print(f"  {status_emoji} {job.id} - {job.status} - {job.model}")
            if job.fine_tuned_model:
                print(f"    └─ Model: {job.fine_tuned_model}")
                
    except Exception as e:
        print(f"❌ Error listing jobs: {e}")

def monitor_job(job_id: str):
    """Monitor a fine-tuning job until completion."""
    print(f"👀 Monitoring job {job_id}...")
    
    while True:
        status = check_job_status(job_id)
        
        if status in ["succeeded", "failed", "cancelled"]:
            break
        elif status in ["running", "validating_files"]:
            print("⏳ Job still running, checking again in 30 seconds...")
            time.sleep(30)
        else:
            print(f"❓ Unknown status: {status}")
            break

def main():
    """Example usage of the fine-tuning workflow."""
    print("🔧 OpenAI Fine-tuning Example")
    
    # Example 1: List existing jobs
    list_fine_tuning_jobs()
    
    # Example 2: Upload file and create job (uncomment to use)
    # training_file_path = "training_data.jsonl"
    # 
    # # Upload the training file
    # file_id = upload_training_file(training_file_path)
    # if not file_id:
    #     return
    # 
    # # Create fine-tuning job
    # job_id = create_fine_tuning_job(file_id)
    # if not job_id:
    #     return
    # 
    # # Monitor the job (optional - this will wait until completion)
    # monitor_job(job_id)
    
    print("\n💡 To use this script:")
    print("  1. Make sure you have a valid 'training_data.jsonl' file")
    print("  2. Run the validation script first: python validate_training_data.py -f training_data.jsonl")
    print("  3. Uncomment the example code in main() to start fine-tuning")

if __name__ == "__main__":
    main() 