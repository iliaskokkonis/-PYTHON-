import sqlite3
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
global save_button


conn = sqlite3.connect('base2.db')
cursor = conn.cursor()


tables = {
    'recipes': '''
        CREATE TABLE IF NOT EXISTS recipes (
            recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_name TEXT
        )
    ''',
    'categories': '''
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            category TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
        )
    ''',
    'ingredients': '''
        CREATE TABLE IF NOT EXISTS ingredients (
            ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            ingredients TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
        )
    ''',
    'instructions': '''
        CREATE TABLE IF NOT EXISTS instructions (
            instruction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            instruction_order INTEGER,
            instruction_text TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
        )
    ''',
    'time': '''
        CREATE TABLE IF NOT EXISTS time (
            recipe_id INTEGER,
            time TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
        )
    ''',
    'hardness': '''
        CREATE TABLE IF NOT EXISTS hardness (
            recipe_id INTEGER,
            hardness TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
        )
    '''
}

for table_name, create_command in tables.items():
  
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    result = cursor.fetchone()
 

    if not result:
        cursor.execute(create_command)

conn.commit()

def check_recipe_exists(recipe_name):
    cursor.execute("SELECT recipe_name FROM recipes")
    recipes = cursor.fetchall()
    for stored_recipe in recipes:
        if stored_recipe[0].lower() == recipe_name.lower():
            return True
    return False





def add_recipe():
    recipe_name = recipe_name_entry.get().strip()
    category = category_entry.get()
    ingredients = ingredients_entry.get("1.0", tk.END).strip()
    instructions = instructions_entry.get("1.0", tk.END).strip()
    time = time_entry.get()
    hardness = hardness_entry.get()

    if not recipe_name or not category or not ingredients or not instructions or not time or not hardness:
        result_label.config(text="Παρακαλώ συμπληρώστε όλα τα πεδία")
        return
    if check_recipe_exists(recipe_name):  # Changed function name to check_recipe_exists
        result_label.config(text="Η συνταγή υπάρχει ήδη στη βάση δεδομένων")
        return

    



    
    cursor.execute("INSERT INTO recipes (recipe_name) VALUES (?)", (recipe_name,))
    recipe_id = cursor.lastrowid


    cursor.execute("INSERT INTO categories (recipe_id, category) VALUES (?, ?)", (recipe_id, category))


    cursor.execute("INSERT INTO ingredients (recipe_id, ingredients) VALUES (?, ?)", (recipe_id, ingredients))

   
    instructions_list = instructions.split(",")
    for order, instruction in enumerate(instructions_list, 1):
        cursor.execute("INSERT INTO instructions (recipe_id, instruction_order, instruction_text) VALUES (?, ?, ?)",
                       (recipe_id, order, instruction.strip()))

   
    cursor.execute("INSERT INTO time (recipe_id, time) VALUES (?, ?)", (recipe_id, time))

    cursor.execute("INSERT INTO hardness (recipe_id, hardness) VALUES (?, ?)", (recipe_id, hardness))

    conn.commit()
    result_label.config(text="Η συνταγή προστέθηκε με επιτυχία")

 
    recipe_name_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    ingredients_entry.delete("1.0", tk.END)
    instructions_entry.delete("1.0", tk.END)
    time_entry.delete(0, tk.END)
    hardness_entry.delete(0, tk.END)
    



def view_recipe():
    recipe_name = recipe_name_entry.get().strip()

    
    if not recipe_name:
        result_label.config(text="Παρακαλώ εισάγετε το όνομα της συνταγής")
        return

    
    cursor.execute("SELECT * FROM recipes WHERE recipe_name=?", (recipe_name,))
    recipe = cursor.fetchone()


    if not recipe:
        result_label.config(text="Δεν βρέθηκε συνταγή με αυτό το όνομα")
        return

   

    recipe_window = tk.Toplevel(root)
    recipe_window.title(f"Συνταγή: {recipe_name}")


    recipe_label = tk.Label(recipe_window, text=f"Συνταγή: {recipe_name}")
    recipe_label.pack()
    cursor.execute("SELECT category FROM categories WHERE recipe_id=?", (recipe[0],))
    category = cursor.fetchone()[0]
    category_label = tk.Label(recipe_window, text=f"Κατηγορία: {category}")
    category_label.pack()

    cursor.execute("SELECT ingredients FROM ingredients WHERE recipe_id=?", (recipe[0],))
    ingredients = cursor.fetchone()[0]
    ingredients_label = tk.Label(recipe_window, text=f"Υλικά:\n{ingredients}")
    ingredients_label.pack()


    cursor.execute("SELECT instruction_text FROM instructions WHERE recipe_id=? ORDER BY instruction_order", (recipe[0],))
    instructions = cursor.fetchall()
    instructions_text = "\n".join([f"{index}. {instruction[0]}" for index, instruction in enumerate(instructions, 1)])
    instructions_label = tk.Label(recipe_window, text=f"Οδηγίες:\n{instructions_text}")
    instructions_label.pack()


    cursor.execute("SELECT time FROM time WHERE recipe_id=?", (recipe[0],))
    time = cursor.fetchone()[0]
    time_label = tk.Label(recipe_window, text=f"Χρόνος εκτέλεσης: {time}")
    time_label.pack()


    cursor.execute("SELECT hardness FROM hardness WHERE recipe_id=?", (recipe[0],))
    hardness = cursor.fetchone()[0]
    hardness_label = tk.Label(recipe_window, text=f"Δυσκολία εκτέλεσης: {hardness}")
    hardness_label.pack()
    recipe_name_entry.delete(0, tk.END)


    recipe_window.protocol("WM_DELETE_WINDOW", recipe_window.destroy)


def delete_recipe():
    recipe_name = recipe_name_entry.get().strip()

    if not recipe_name:
        result_label.config(text="Παρακαλώ εισάγετε το όνομα της συνταγής")
        return

   
    cursor.execute("SELECT recipe_id FROM recipes WHERE recipe_name=?", (recipe_name,))
    recipe_id = cursor.fetchone()

    if not recipe_id:
        result_label.config(text="Δεν βρέθηκε συνταγή με αυτό το όνομα")
        return

  
    delete_commands = [
        f"DELETE FROM recipes WHERE recipe_name='{recipe_name}'",
        f"DELETE FROM categories WHERE recipe_id={recipe_id[0]}",
        f"DELETE FROM ingredients WHERE recipe_id={recipe_id[0]}",
        f"DELETE FROM instructions WHERE recipe_id={recipe_id[0]}",
        f"DELETE FROM time WHERE recipe_id={recipe_id[0]}",
        f"DELETE FROM hardness WHERE recipe_id={recipe_id[0]}"
    ]

   

    for delete_command in delete_commands:
        cursor.execute(delete_command)

    conn.commit()
    result_label.config(text=f"Η συνταγή '{recipe_name}' διαγράφηκε με επιτυχία")


def modify_recipe():
    recipe_name = recipe_name_entry.get().strip()


    #if not recipe_name:
    #    result_label.config(text="Παρακαλώ εισάγετε το όνομα της συνταγής")
    #    return


    cursor.execute('''SELECT recipes.recipe_name, categories.category, ingredients.ingredients, instructions.instruction_text, time.time, hardness.hardness
                      FROM recipes
                      LEFT JOIN categories ON recipes.recipe_id = categories.recipe_id
                      LEFT JOIN ingredients ON recipes.recipe_id = ingredients.recipe_id
                      LEFT JOIN instructions ON recipes.recipe_id = instructions.recipe_id
                      LEFT JOIN time ON recipes.recipe_id = time.recipe_id
                      LEFT JOIN hardness ON recipes.recipe_id = hardness.recipe_id
                      WHERE recipes.recipe_name = ?''', (recipe_name,))


    row = cursor.fetchone()


    if row:
        recipe_window = tk.Toplevel(root)
        recipe_window.title("Τροποποίηση Συνταγής")

        recipe_name_description_label = tk.Label(recipe_window, text="Όνομα Συνταγής:")
        recipe_name_description_label.grid(row=0, column=0, padx=10, pady=10)

        recipe_name_label = tk.Label(recipe_window, text=row[0])
        recipe_name_label.grid(row=0, column=1, padx=10, pady=10)


        category_label = tk.Label(recipe_window, text="Κατηγορία Συνταγής:")
        category_label.grid(row=1, column=0, padx=10, pady=10)

        category_entry = tk.Entry(recipe_window, width=50)
        category_entry.grid(row=1, column=1, padx=10, pady=10)
        category_entry.insert(tk.END, row[1])


        ingredients_label = tk.Label(recipe_window, text="Υλικά Που Θα Χρειαστούν:")
        ingredients_label.grid(row=2, column=0, padx=10, pady=10)

        ingredients_entry = tk.Text(recipe_window, height=12, width=50)
        ingredients_entry.grid(row=2, column=1, padx=10, pady=10)
        ingredients_entry.insert(tk.END, row[2])

        instructions_label = tk.Label(recipe_window, text="Οδηγίες Παρασκευής Χωρισμένες Με Κόμμα:")
        instructions_label.grid(row=3, column=0, padx=10, pady=10)

        instructions_entry = tk.Text(recipe_window, height=12, width=50)
        instructions_entry.grid(row=3, column=1, padx=10, pady=10)


        cursor.execute('''
            SELECT instructions.instruction_text
            FROM recipes
            LEFT JOIN instructions ON recipes.recipe_id = instructions.recipe_id
            WHERE recipes.recipe_name = ?
        ''', (recipe_name,))


        instructions = cursor.fetchall()
        instructions_text = ', '.join([instruction[0] for instruction in instructions])
        instructions_entry.insert(tk.END, instructions_text)


        time_label = tk.Label(recipe_window, text="Χρόνος Παρασκευής:")
        time_label.grid(row=4, column=0, padx=10, pady=10)

        time_entry = tk.Entry(recipe_window, width=50)
        time_entry.grid(row=4, column=1, padx=10, pady=10)
        time_entry.insert(tk.END, row[4])

        hardness_label = tk.Label(recipe_window, text="Δυσκολία Παρασκευής:")
        hardness_label.grid(row=5, column=0, padx=10, pady=10)

        hardness_entry = tk.Entry(recipe_window, width=50)
        hardness_entry.grid(row=5, column=1, padx=10, pady=10)
        hardness_entry.insert(tk.END, row[5])

        save_button = tk.Button(recipe_window, text="ΑΠΟΘΗΚΕΥΣΗ", bg="green", fg="white",
                                command=lambda: update_recipe(recipe_name, category_entry.get(),
                                                              ingredients_entry.get("1.0", tk.END),
                                                              instructions_entry.get("1.0", tk.END), time_entry.get(),
                                                              hardness_entry.get(), recipe_window))

        save_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    else:
        result_label.config(text="Η συνταγή δεν βρέθηκε στη βάση δεδομένων.")




def update_recipe(recipe_name, category, ingredients, instructions, time, hardness, recipe_window):
    cursor.execute('''UPDATE recipes
                      SET recipe_name = ?
                      WHERE recipe_name = ?''', (recipe_name, recipe_name_entry.get()))

    cursor.execute('''UPDATE categories
                      SET category = ?
                      WHERE recipe_id = (SELECT recipe_id FROM recipes WHERE recipe_name = ?)''',
                   (category, recipe_name))

    cursor.execute('''UPDATE ingredients
                      SET ingredients = ?
                      WHERE recipe_id = (SELECT recipe_id FROM recipes WHERE recipe_name = ?)''',
                   (ingredients, recipe_name))


    cursor.execute('''DELETE FROM instructions WHERE recipe_id = (SELECT recipe_id FROM recipes WHERE recipe_name = ?)''', (recipe_name,))


    instruction_list = instructions.split(",")
    instruction_order = 1
    for instruction_text in instruction_list:
        cursor.execute('''INSERT INTO instructions (recipe_id, instruction_order, instruction_text) VALUES ((SELECT recipe_id FROM recipes WHERE recipe_name = ?), ?, ?)''',
                       (recipe_name, instruction_order, instruction_text.strip()))
        instruction_order += 1

    cursor.execute('''UPDATE time
                      SET time = ?
                      WHERE recipe_id = (SELECT recipe_id FROM recipes WHERE recipe_name = ?)''', (time, recipe_name))

    cursor.execute('''UPDATE hardness
                      SET hardness = ?
                      WHERE recipe_id = (SELECT recipe_id FROM recipes WHERE recipe_name = ?)''',
                   (hardness, recipe_name))


    conn.commit()
    result_label.config(text="Η συνταγή ενημερώθηκε επιτυχώς.")
    recipe_name_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    ingredients_entry.delete("1.0", tk.END)
    instructions_entry.delete("1.0", tk.END)
    time_entry.delete(0, tk.END)
    hardness_entry.delete(0, tk.END)
    recipe_window.destroy()


def cook_recipe():
    recipe_name = recipe_name_entry.get().strip()

    if not recipe_name:
        result_label.config(text="Παρακαλώ εισάγετε το όνομα της συνταγής")
        return


    cursor.execute("SELECT * FROM recipes WHERE recipe_name=?", (recipe_name,))
    recipe = cursor.fetchone()

    if not recipe:
        result_label.config(text="Δεν βρέθηκε συνταγή με αυτό το όνομα")
        return
    

    cursor.execute("SELECT instruction_text FROM instructions WHERE recipe_id=? ORDER BY instruction_order", (recipe[0],))
    instructions = cursor.fetchall()

    if not instructions:
        result_label.config(text="Δεν υπάρχουν οδηγίες για αυτήν τη συνταγή")
        return
  
    total_instructions = len(instructions)
    current_instruction = 0

    
    cook_window = tk.Toplevel(root)
    cook_window.title("Μαγειρεύουμε..!")
    cook_window.geometry("400x300")


    instruction_label = tk.Label(cook_window, text=instructions[current_instruction][0], wraplength=350)
    instruction_label.pack(padx=10, pady=10)

    
    def next_instruction():
        nonlocal current_instruction
        current_instruction += 1
       

        if current_instruction < total_instructions:
            instruction_label.config(text=instructions[current_instruction][0])
            percentage = (current_instruction / total_instructions) * 100
            result_label.config(text=f"Ποσοστό έτοιμης συνταγής: {percentage:.2f}%")
        else:
            instruction_label.config(text="100% Έτοιμη Συνταγή")
            result_label.config(text="Ποσοστό έτοιμης συνταγής: 100%")
            messagebox.showinfo("Ολοκλήρωση Συνταγής", "Η συνταγή ολοκληρώθηκε!")
            cook_window.destroy()
    def previous_instruction():
        nonlocal current_instruction
        current_instruction -= 1

        if current_instruction >= 0:
            instruction_label.config(text=instructions[current_instruction][0])
            percentage = (current_instruction / total_instructions) * 100
            result_label.config(text=f"Ποσοστό έτοιμης συνταγής: {percentage:.2f}%")
        else:
            current_instruction = 0


   
    next_button = tk.Button(cook_window, text="Επόμενο Βήμα", bg="blue", fg="white", command=next_instruction)
    next_button.pack(padx=10, pady=10)

    previous_button = tk.Button(cook_window, text="Προηγούμενο Βήμα", bg="white", fg="blue", command=previous_instruction)
    previous_button.pack(padx=10, pady=10)

    
    initial_percentage = (current_instruction / total_instructions) * 100
    result_label.config(text=f"Ποσοστό έτοιμης συνταγής: {initial_percentage:.2f}%")


    cook_window.mainloop()


root.title("ΠΡΟΓΡΑΜΜΑ ΔΙΑΧΕΙΡΙΣΗΣ ΣΥΝΤΑΓΩΝ ΜΑΓΕΙΡΙΚΗΣ - ΖΑΧΑΡΟΠΛΑΣΤΙΚΗΣ")

recipe_name_label = tk.Label(root, text="Πληκτρολογήστε Το Όνομα Της Συνταγής:")
recipe_name_label.grid(row=0, column=0, padx=10, pady=10)

recipe_name_entry = tk.Entry(root, width=50)
recipe_name_entry.grid(row=0, column=1, padx=10, pady=10)

category_label = tk.Label(root, text="Κατηγορία Συνταγής:")
category_label.grid(row=1, column=0, padx=10, pady=10)

category_entry = tk.Entry(root, width=50)
category_entry.grid(row=1, column=1, padx=10, pady=10)

ingredients_label = tk.Label(root, text="Υλικά Που Θα Χρειαστούν:")
ingredients_label.grid(row=2, column=0, padx=10, pady=10)

ingredients_entry = tk.Text(root, height=12, width=50)
ingredients_entry.grid(row=2, column=1, padx=10, pady=10)

instructions_label = tk.Label(root, text="Οδηγίες Παρασκευής Χωρισμένες Με Κόμμα:")
instructions_label.grid(row=3, column=0, padx=10, pady=10)

instructions_entry = tk.Text(root, height=15, width=50)
instructions_entry.grid(row=3, column=1, padx=10, pady=10)

time_label = tk.Label(root, text="Χρόνος Εκτέλεσης")
time_label.grid(row=4, column=0, padx=10, pady=10)

time_entry = tk.Entry(root, width=50)
time_entry.grid(row=4, column=1, padx=10, pady=10)

hardness_label = tk.Label(root, text="Δυσκολία Εκτέλεσης:")
hardness_label.grid(row=5, column=0, padx=10, pady=10)

hardness_entry = tk.Entry(root, width=50)
hardness_entry.grid(row=5, column=1, padx=10, pady=10)

add_button = tk.Button(root, text="Προσθήκη Συνταγής", bg="green", fg="white", command=add_recipe)
add_button.grid(row=6, column=0, padx=10, pady=10)

view_button = tk.Button(root, text="Εύρεση - Εμφάνιση Συνταγής", bg="purple", fg="white", command=view_recipe)
view_button.grid(row=6, column=1, padx=10, pady=10)

delete_button = tk.Button(root, text="Διαγραφή Συνταγής", bg="red", fg="white", command=delete_recipe)
delete_button.grid(row=7, column=0, padx=10, pady=10)

modify_button = tk.Button(root, text="Τροποποίηση Συνταγής", bg="tomato", fg="white", command=modify_recipe)
modify_button.grid(row=7, column=1, padx=10, pady=10)

result_label = tk.Label(root, text="")
result_label.grid(row=8, columnspan=2, padx=10, pady=10)

cook_button = tk.Button(root, text="Μαγειρέψτε..!", bg="yellow", fg="black", command=cook_recipe)
cook_button.grid(row=7, column=2, padx=10, pady=10)

result_label = tk.Label(root, text="")
result_label.grid(row=8, columnspan=2, padx=10, pady=10)

root.mainloop()


conn.close()
