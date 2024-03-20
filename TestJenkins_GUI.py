import os
import json
import tkinter as tk
from pathlib import Path
from ttkthemes import ThemedStyle
from tkinter import scrolledtext, ttk, messagebox
from JenkinsTestReportCompare import JenkinsTestResults


def compare_and_display_results():
    try:
        # Get values from input boxes
        username = username_entry.get()
        functional_test_1_url = functional_test_1_entry.get()
        functional_test_2_url = functional_test_2_entry.get()
        
        if not username:
            raise ValueError("Username cannot be empty")
        if not functional_test_1_url:
            raise ValueError("URL for Functional Test 1 cannot be empty")
        if not functional_test_2_url:
            raise ValueError("URL for Functional Test 2 cannot be empty")
        
        # Pass user values to JenkinsTestResults class
        compare_output = {}
        userInfo = (username, os.environ.get('JENKINS_API_TOKEN', 'your-api-token'))
        jenkins_result = JenkinsTestResults(userInfo)
        result1 = jenkins_result.get_result_and_parse(functional_test_1_url)
        result2 = jenkins_result.get_result_and_parse(functional_test_2_url)
        compare_output['Comparison_Result'] = jenkins_result.compare_results(result1, result2)

        output = json.dumps (compare_output)

        file_path = jenkins_result.create_ouput_file()                
        jenkins_result.write_results_to_output_file(file_path, output) 


        text_area.config(state=tk.NORMAL)
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.INSERT, output)
        text_area.config(state=tk.DISABLED)
        
        # Load and display the output file
        display_comparison_result()
        
    except ValueError as ve:
        messagebox.showerror("Value Error", ve)

def display_comparison_result():
    output_file_path = os.path.join(Path(__file__).parent.absolute(), "Output.txt")
    
    try:
        with open(output_file_path, "r") as file:
            content = file.read()
            
            text_area.config(state=tk.NORMAL)  
            text_area.delete(1.0, tk.END)
            
            text_area.insert(tk.INSERT, content)
            
            tag_words = ["Category:", "Description:", "Total count:"]
            for word in tag_words:
                start_index = "1.0"
                while True:
                    start_index = text_area.search(word, start_index, stopindex=tk.END)
                    if not start_index:
                        break
                    end_index = f"{start_index}+{len(word)}c"
                    text_area.tag_add("bold", start_index, end_index)
                    text_area.tag_config("bold", font=("Arial", 10, "bold"))
                    start_index = end_index
            
            # Tag categories with respective colors and font weights
            tag_categories = {
                "Regression/New errors in existing tests": ("blue", "bold"),
                "Conflicting Errors": ("red", "bold"),
                "Equal Tests": ("green", "bold"),
                "Resolved Tests": ("purple", "bold"),
                "Ignored Tests": ("orange", "bold"),
                "Emerging Test Failures": ("brown", "bold"),
                "Emerging Resolved Tests": ("magenta", "bold"),
                "New Test Failures": ("darkorange", "bold"),
                "New Testsuite Failures": ("darkred", "bold")
            }
            for category, (color, font_weight) in tag_categories.items():
                start_index = text_area.search(category, "1.0", stopindex=tk.END)
                while start_index:
                    end_index = f"{start_index} lineend"
                    text_area.tag_add(category, start_index, end_index)
                    text_area.tag_config(category, foreground=color, font=("Arial", 10, font_weight))
                    start_index = text_area.search(category, end_index, stopindex=tk.END)
            
            # Tag "*** Jenkins FT Comparison Results ***" with a different color
            header_tag_color = "navy"
            start_index = text_area.search("*** Jenkins FT Comparison Results ***", "1.0", stopindex=tk.END)
            while start_index:
                end_index = f"{start_index} lineend"
                text_area.tag_add("header", start_index, end_index)
                text_area.tag_config("header", foreground=header_tag_color, font=("Arial", 12, "bold"))
                start_index = text_area.search("*** Jenkins FT Comparison Results ***", end_index, stopindex=tk.END)
            
            text_area.config(state=tk.DISABLED)  # Disable editing after insertion
            
    except FileNotFoundError:
        messagebox.showerror("File Not Found", "The specified file could not be found.")

# Create the main window
window = tk.Tk()
window.title("Compare Jenkins Functional Tests")
# Load the icon image
icon_path = os.path.join(Path(__file__).parent.absolute(), "logo.png")
icon_image = tk.PhotoImage(file=icon_path)

# Set window icon
window.iconphoto(True, icon_image)

window.geometry("800x600")
window.configure(bg="#f0f0f0")

# Set theme to 'arc'
style = ThemedStyle(window)
style.set_theme("arc")

# Heading and Description
heading_label = ttk.Label(window, text="Compare Jenkins Functional Tests", font=("Arial", 16, "bold"), foreground="black")
heading_label.pack(pady=10)

description_label = ttk.Label(window, text="Provide your Jenkins username and the Jenkins test result links for any two Functional Tests that were run for the same driver and platform which you want to compare:", foreground="red")
description_label.pack(pady=5)

# Username Input
username_frame = ttk.Frame(window)
username_frame.pack(pady=10, anchor="w")
username_label = ttk.Label(username_frame, text="Jenkins Username:", font=("Arial", 10, "bold"), foreground="black")
username_label.pack(side="left", padx=(30, 5), pady=5)
username_entry = ttk.Entry(username_frame, width=100)
username_entry.pack(side="left", padx=(22, 10), pady=5)


# Functional Test 1 Input
functional_test_1_frame = ttk.Frame(window)
functional_test_1_frame.pack(pady=10, anchor="w")
functional_test_1_label = ttk.Label(functional_test_1_frame, text="Functional Test 1 Link:", font=("Arial", 10, "bold"), foreground="black")
functional_test_1_label.pack(side="left", padx=(30, 5), pady=5)
functional_test_1_entry = ttk.Entry(functional_test_1_frame, width=200)
functional_test_1_entry.pack(side="left", padx=(0, 10), pady=5)

# Functional Test 2 Input
functional_test_2_frame = ttk.Frame(window)
functional_test_2_frame.pack(pady=10, anchor="w")
functional_test_2_label = ttk.Label(functional_test_2_frame, text="Functional Test 2 Link:", font=("Arial", 10, "bold"), foreground="black")
functional_test_2_label.pack(side="left", padx=(30, 5), pady=5)
functional_test_2_entry = ttk.Entry(functional_test_2_frame, width=200)
functional_test_2_entry.pack(side="left", padx=(0, 10), pady=5)

# Compare Button
button_style = ttk.Style()
button_style.configure("Bold.TButton", 
                        font=("Arial", 10, "bold"), 
                        foreground="#1ea64b", 
                        width=15)
compare_button = ttk.Button(window, text="Compare", command=compare_and_display_results, style="Bold.TButton")
compare_button.pack(pady=10, padx=(10, 0))

# Create a frame for the text area
text_frame = ttk.Frame(window)
text_frame.pack(padx=20, pady=10, fill="both", expand=True)
text_frame.pack(padx=20, pady=10, fill="both", expand=True)

# Create a scrolled text area to display the file content
text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=80, height=20, state=tk.DISABLED)  # Set state to DISABLED
text_area.pack(expand=True, fill="both", padx=10, pady=10)

# Run the application
window.mainloop()
