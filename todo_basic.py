import json
import os
import boto3

# Connect to S3 using your local AWS config
s3 = boto3.client("s3")
bucket_name = "jack-todo-list"  # replace with your bucket name

def load_todos():
    if os.path.exists('todos.json'):
        with open('todos.json', 'r') as f:
            return json.load(f)
    return []

def save_todos(todos):
    # Save locally first
    with open('todos.json', 'w') as f:
        json.dump(todos, f)
    
    # Also save to AWS S3
    try:
        # Convert todos to a simple text format for S3
        tasks_text = []
        for todo in todos:
            status = "✓" if todo["done"] else " "
            tasks_text.append(f"[{status}] {todo['task']}")
        
        data = "\n".join(tasks_text)
        
        # Upload to S3
        s3.put_object(
            Bucket=bucket_name,
            Key="tasks.txt",
            Body=data
        )
        print("✅ Tasks saved locally and to AWS S3!")
    except Exception as e:
        print(f"⚠️  Saved locally, but S3 upload failed: {e}")

def add_todo():
    todo = input("Enter your todo: ")
    todos = load_todos()
    todos.append({"task": todo, "done": False})
    save_todos(todos)
    print("Todo added!")

def view_todos():
    todos = load_todos()
    if not todos:
        print("No todos yet!")
        return
    
    for i, todo in enumerate(todos):
        status = "✓" if todo["done"] else " "
        print(f"{i+1}. [{status}] {todo['task']}")

def mark_done():
    view_todos()
    try:
        num = int(input("Enter todo number to mark done: ")) - 1
        todos = load_todos()
        if 0 <= num < len(todos):
            todos[num]["done"] = True
            save_todos(todos)
            print("Marked as done!")
        else:
            print("Invalid number!")
    except ValueError:
        print("Please enter a valid number!")

def check_password():
    password = "1234"  # Simple password - you can change this
    attempts = 3
    
    while attempts > 0:
        user_input = input(f"Enter password ({attempts} attempts left): ")
        if user_input == password:
            print("Access granted! Welcome to your todo list.")
            return True
        else:
            attempts -= 1
            if attempts > 0:
                print("Wrong password! Try again.")
            else:
                print("Too many wrong attempts. Goodbye!")
                return False

def load_from_s3():
    try:
        # Try to download from S3
        response = s3.get_object(
            Bucket=bucket_name,
            Key="tasks.txt"
        )
        data = response['Body'].read().decode('utf-8')
        
        # Parse the text format back to todos
        todos = []
        for line in data.strip().split('\n'):
            if line.strip():
                done = line.startswith('[✓]')
                task = line[4:] if line.startswith('[✓]') else line[3:]
                todos.append({"task": task, "done": done})
        
        # Save locally
        with open('todos.json', 'w') as f:
            json.dump(todos, f)
        
        print("✅ Loaded todos from AWS S3!")
        return todos
    except Exception as e:
        print(f"⚠️  Failed to load from S3: {e}")
        return load_todos()

def main():
    # Password check first
    if not check_password():
        return
    
    while True:
        print("\n=== SIMPLE TODO LIST ===")
        print("1. Add todo")
        print("2. View todos")
        print("3. Mark done")
        print("4. Sync from S3")
        print("5. Quit")
        
        choice = input("Choose (1-5): ")
        
        if choice == "1":
            add_todo()
        elif choice == "2":
            view_todos()
        elif choice == "3":
            mark_done()
        elif choice == "4":
            load_from_s3()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
