import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT username, created_at
    FROM users
    ORDER BY created_at DESC
""")

users = cursor.fetchall()

print("\n========== REGISTERED USERS ==========\n")

if users:
    for username, created_at in users:
        print(f"Username: {username}")
        print(f"Registered: {created_at}")
        print("-------------------------------------")
else:
    print("No registered users found.")

conn.close()