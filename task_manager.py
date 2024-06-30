# %%

# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 20:12:57 2024

@author: tomur
"""


import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

def create_connection():
    # コネクションオブジェクトを生成
    connection = sqlite3.connect("task_manager3.db")
    return connection

def create_table(connection):
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT
        )
    ''')
    connection.commit()

def add_columns_to_table(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN purpose TEXT")
        cursor.execute("ALTER TABLE tasks ADD COLUMN comment TEXT")
        cursor.execute("ALTER TABLE tasks ADD COLUMN satisfaction INTEGER")
        connection.commit()
        print("Columns 'purpose', 'comment', and 'satisfaction' added successfully.")
    except sqlite3.OperationalError as e:
        # エラーメッセージが「duplicate column name」でない場合のみ表示
        if "duplicate column name" not in str(e):
            print(f"An error occurred: {e}")

def add_task(connection, task_name, purpose, comment):
    cursor = connection.cursor()
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO tasks (name, start_time, purpose, comment) VALUES (?, ?, ?, ?)", 
                   (task_name, start_time, purpose, comment))
    connection.commit()
    new_value = cursor.execute("SELECT MAX(id) FROM tasks").fetchone()[0]
    
    print(f"Task '{task_name}' added. task_id = {new_value}")

def start_task(connection, task_id):
    cursor = connection.cursor()
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE tasks SET start_time = ? WHERE id = ?", (start_time, task_id))
    connection.commit()
    print(f"Task {task_id} started at {start_time}.")

def end_task(connection, task_id):
    cursor = connection.cursor()
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE tasks SET end_time = ? WHERE id = ?", (end_time, task_id))
    connection.commit()
    print(f"Task {task_id} ended at {end_time}.")

def display_tasks(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    # Create a pandas DataFrame
    df = pd.DataFrame(tasks, columns=['ID', 'Name', 'Start Time', 'End Time', 'Purpose', 'Comment', 'Satisfaction'])

    # Calculate total time for each task
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['End Time'] = pd.to_datetime(df['End Time'])
    df['Total Time'] = (df['End Time'] - df['Start Time']).dt.total_seconds() / 3600  # convert to hours

    # Aggregate total times by task name
    total_times = df.groupby('Name')['Total Time'].sum().reset_index()

    # Plotting
    fig, ax = plt.subplots(1, 2, figsize=(14, 7))
    
    # Pie chart
    ax[0].pie(total_times['Total Time'], labels=total_times['Name'], autopct='%1.1f%%', startangle=90)
    ax[0].axis('equal')
    ax[0].set_title('Total Time Spent on Each Task (Pie Chart)')

    # Bar chart
    ax[1].bar(total_times['Name'], total_times['Total Time'], color='skyblue')
    ax[1].set_ylabel('Total Time (hours)')
    ax[1].set_xlabel('Task Name')
    ax[1].set_title('Total Time Spent on Each Task (Bar Chart)')
    plt.xticks(rotation=45, ha='right')

    # Save the figures with the specified dpi, bbox_inches, and pad_inches
    plt.savefig("task_times.png", dpi=600, bbox_inches='tight', pad_inches=0.1)

    # Display the plots
    plt.show()

def update_task(connection, task_id, comment, satisfaction):
    cursor = connection.cursor()
    cursor.execute("UPDATE tasks SET comment = ?, satisfaction = ? WHERE id = ?", 
                   (comment, satisfaction, task_id))
    connection.commit()
    print(f"Task {task_id} updated with comment and satisfaction.")

def delete_task(connection, task_id):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    connection.commit()
    print(f"Task {task_id} deleted.")
    
def close_task(connection, task_id, comment, satisfaction):
    cursor = connection.cursor()
    cursor.execute("UPDATE tasks SET comment = ?, satisfaction = ? WHERE id = ?",
                   (comment, satisfaction, task_id))
    connection.commit()
    print(f"Task {task_id} is completed. Nice work")

def main():
    connection = create_connection()
    create_table(connection)
    add_columns_to_table(connection)

    while True:
        print("\nTime Management App")
        print("1. Add Task")
        print("2. Start Task")
        print("3. End Task")
        print("4. Display Tasks")
        print("5. Update Task")
        print("6. Delete Task")
        print("7. Looking Back and Close")
        print("8. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            task_name = input("Enter the task name: ")
            purpose = input("Enter a purpose for the task: ")
            comment = input("Enter a comment for the task: ")
            add_task(connection, task_name, purpose, comment)
        elif choice == "2":
            task_id = int(input("Enter the task ID to start: "))
            start_task(connection, task_id)
        elif choice == "3":
            task_id = int(input("Enter the task ID to end: "))
            end_task(connection, task_id)
        elif choice == "4":
            display_tasks(connection)
        elif choice == "5":
            task_id = int(input("Enter the task ID to update: "))
            comment = input("Enter a new comment for the task: ")
            satisfaction = int(input("Enter a new satisfaction level (1-10): "))
            update_task(connection, task_id, comment, satisfaction)
        elif choice == "6":
            task_id = int(input("Enter the task ID to delete: "))
            delete_task(connection, task_id)
        elif choice == "7":
            task_id = int(input("Enter the task ID to finish: "))
            comment = input("Enter a comment for the task: ")
            satisfaction = int(input("Enter a satisfaction level (1-10): "))
            close_task(connection, task_id, comment, satisfaction)
            connection.close()
            
        elif choice == "8":
            connection.close()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

# %%
