import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from pathlib import Path

json_file = Path("dataset_descriptions.json")

# Create a complete JSON with schemas if the file does not exist
if not json_file.exists():
    initial_data = {
        "categories": {
            "1_drone_entire_object": {},  # The Schemes are already in the code
            "2_headset_entire_object": {},
            "3_large_nodes": {},
            "4_isolated_options": {},
            "5_isolated_details": {},
            "6_states_and_relationships": {}
        },
        "counter": 0
    }
    json_file.write_text(json.dumps(initial_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Created dataset_descriptions.json with category schemas")

# Reading and updating
try:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data["counter"] = data.get("counter", 0) + 1
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"dataset_descriptions.json is updated: {data}")
    
except json.JSONDecodeError as e:
    print(f"Error JSON in the file: {e}")
except FileNotFoundError:
    print("File not found although we have created it")
except Exception as e:
    print(f"Other error: {e}")

class CategoryJSONEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Caption generator by categories (Drone and Headset Dataset)")
        self.current_category = tk.StringVar()
        self.current_row = {}  # Actual record
        self.entries = {}  # Field widgets
        self.schemas_by_category = {}  # Schemas by categories
        self.image_counter = {}  # Image counter by category

        self.setup_ui()
        self.parse_schemas_by_category()
        self.update_category_list()

    def setup_ui(self):
        # Category selection
        cat_frame = tk.Frame(self.root)
        cat_frame.pack(pady=10)
        ttk.Label(cat_frame, text="Category:").pack(side=tk.LEFT)

        # We create a Combobox, but do not set any values yet
        self.category_cb = ttk.Combobox(
            cat_frame,
            textvariable=self.current_category,
            width=50,
            state='readonly'
        )
        self.category_cb.pack(side=tk.LEFT, padx=5)
        self.category_cb.bind('<<ComboboxSelected>>', self.on_category_change)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Load template JSON", command=self.load_template).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clean form", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Generate .txt", command=self.generate_caption_txt, bg='green', fg='white').pack(side=tk.LEFT, padx=5)

        # Status
        self.status_label = ttk.Label(self.root, text="Select category")
        self.status_label.pack(pady=5)

        # Scroll-form (IMPORTANT: create here, before any show_category_form calls)
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)

        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.pack(side="right", fill="y")

    def parse_schemas_by_category(self):
        # Full schemas by 6 categories from JSON
        self.schemas_by_category = {
            '1_drone_entire_object': {
                'object_type': {'type': 'select', 'options': ['unmanned airship drone']},
                'base_model': {'type': 'select', 'options': ['model M', 'model F']},
                'main_size_diameter': {'type': 'string'},
                'main_size_length': {'type': 'string'},
                'main_size_height': {'type': 'string'},
                'material': {'type': 'select', 'options': ['solid composite', 'low glass plastic']},
                'orientation': {'type': 'select', 'options': ['normal', 'horizontal', 'vertical', 'slightly inclined position', 'middle inclined position']},
                'action': {'type': 'select', 'options': ['flying', 'hovering', 'climbing', 'dedcending', 'is landed']},
                'engine_group': {'type': 'string'},
                'engine_count': {'type': 'string'},
                'engine_rotor_count': {'type': 'string'},
                'engine_rotor_blade_count': {'type': 'string'},
                'engines_composition': {'type': 'select', 'options': ['in the center of the airship']},
                'engine_position': {'type': 'select', 'options': ['mid-string', 'frontal']},
                'engine_group_state': {'type': 'select', 'options': ['VTOL mode', 'omnidrive mode', 'cruise speed mode']},
                'options_text': {'type': 'select', 'options': ['no additional options or payloads mounted', 'additional options and payload mounted including']},
                'options_text_2': {'type': 'string'},
                'state_description': {'type': 'string'},
                'color_scheme': {'type': 'select', 'options': ['light gray and light blue camouflage', 'light gray and light blue', 'light gray and dark blue', 'light gray and dark gray', 'yellow and dark pink']},
                'markings': {'type': 'string'},
                'light': {'type': 'select', 'options': ['soft sunlight', 'multi-directional studio light']},
                'background_type': {'type': 'select', 'options': ['white', 'gray', 'green', 'blue', 'black', 'sky with scattered clouds', 'gray gradient']},
                'camera_view_position': {'type': 'select', 'options': ['full-front', 'quarter-turn right', 'profile right', 'three-quarter front right', 'back to camera', 'three-quarter front left', 'profile left', 'quarter-turn left', 'bird’s-eye view', 'worm’s-eye view', 'full-front high-angle', 'quarter-turn right high-angle', 'profile right high-angle', 'three-quarter front right high-angle', 'back to camera high-angle', 'three-quarter front left high-angle', 'profile left high-angle', 'quarter-turn left high-angle', 'full-front low-angle', 'quarter-turn right low-angle', 'profile right low-angle', 'three-quarter front right low-angle', 'back to camera low-angle', 'three-quarter front left low-angle', 'profile left low-angle', 'quarter-turn left low-angle']},
                'camera_distance': {'type': 'string'},
                'camera_azimuth': {'type': 'string'},
                'camera_inclination': {'type': 'string'},
                'camera_twist': {'type': 'string'},
                'camera_pivot': {'type': 'string'},
                'camera_focal_length': {'type': 'string'},
                'image_name': {'type': 'string'},
            },
            '2_headset_entire_object': {
                'object_type': {'type': 'select', 'options': ['arhudfm']},
                'base_model': {'type': 'select', 'options': ['model One']},
                'modification': {'type': 'select', 'options': ['basic', 'kit', 'ballistic', 'total kit', 'SBCA']},
                'main_size_width': {'type': 'string'},
                'main_size_length': {'type': 'string'},
                'main_size_height': {'type': 'string'},
                'material': {'type': 'select', 'options': ['solid composite', 'low glass plastic']},
                'orientation': {'type': 'select', 'options': ['normal', 'horizontal', 'vertical', 'slightly inclined position', 'middle inclined position']}, 
                'options_text': {'type': 'select', 'options': ['no additional options or payloads mounted', 'additional options and payload mounted including']},
                'options_text_2': {'type': 'string'},
                'state_description': {'type': 'string'},
                'color_scheme': {'type': 'select', 'options': ['MCCUU MARPAT woodland pattern camouflage', 'MCCUU MARPAT desert pattern camouflage', 'NWU III AOR II pattern camouflage', 'NWU II AOR I pattern camouflage', 'OCP ACU Scorpion W2 woodland pattern camouflage', 'OCP ACU Scorpion W2 desert pattern camouflage', 'A2CU arctic pattern camouflage', 'Flecktarn pattern camouflage', 'MultiTarn pattern camouflage', 'Tropentarn desert pattern camouflage', 'CCE pattern camouflage', 'CCE blends pattern camouflage', 'M05 woodland digital pattern camouflage', 'M05 snowspot pattern camouflage', 'M05 desert pattern camouflage', 'MTP Multi-Terrain forest pattern camouflage', 'MTP Multi-Terrain desert hybrid pattern camouflage', 'IDF solid color olive drab army', 'IDF solid color blue navy', 'IDF solid color air force', 'Multicam pattern camouflage', 'dark navy blue color', 'black police uniform color', 'sheriff uniform color', 'light gray color', 'light blue medical uniform color', 'light green medical uniform color', 'yellow and dark pink emergency uniform color']},
                'markings': {'type': 'string'},
                'light': {'type': 'select', 'options': ['soft sunlight', 'multi-directional studio light']},
                'background_type': {'type': 'select', 'options': ['white', 'gray', 'green', 'blue', 'black', 'sky with scattered clouds', 'gray gradient']},
                'camera_view_position': {'type': 'select', 'options': ['full-front', 'quarter-turn right', 'profile right', 'three-quarter front right', 'back to camera', 'three-quarter front left', 'profile left', 'quarter-turn left', 'bird’s-eye view', 'worm’s-eye view', 'full-front high-angle', 'quarter-turn right high-angle', 'profile right high-angle', 'three-quarter front right high-angle', 'back to camera high-angle', 'three-quarter front left high-angle', 'profile left high-angle', 'quarter-turn left high-angle', 'full-front low-angle', 'quarter-turn right low-angle', 'profile right low-angle', 'three-quarter front right low-angle', 'back to camera low-angle', 'three-quarter front left low-angle', 'profile left low-angle', 'quarter-turn left low-angle']},
                'camera_distance': {'type': 'string'},
                'camera_azimuth': {'type': 'string'},
                'camera_inclination': {'type': 'string'},
                'camera_twist': {'type': 'string'},
                'camera_pivot': {'type': 'string'},
                'camera_focal_length': {'type': 'string'},
                'image_name': {'type': 'string'},
            },
            '3_large_nodes': {
                'object_type': {'type': 'select', 'options': ['ACSG emals catapult', 'ACSG arresting gate', 'drone hunter', 'drone Lyutiy', 'drone Hermes', 'ACSG drone group', 'ACSG group', 'HPM group', 'AESA group', 'VTOL drone launch pad', 'HPM model M', 'AESA model M', 'HEL model M']},
                'main_size_width': {'type': 'string'},
                'main_size_length': {'type': 'string'},
                'main_size_height': {'type': 'string'},
                'material': {'type': 'select', 'options': ['solid composite', 'low glass plastic']},
                'orientation': {'type': 'select', 'options': ['normal', 'horizontal', 'vertical', 'slightly inclined position', 'middle inclined position']}, 
                'options_text': {'type': 'select', 'options': ['no additional options or payloads mounted', 'additional options and payload mounted including']},
                'options_text_2': {'type': 'string'},
                'state_description': {'type': 'string'},
                'color_scheme': {'type': 'select', 'options': ['light gray and light blue camouflage', 'light gray and light blue', 'light gray and dark blue', 'light gray and dark gray', 'yellow and dark pink']},
                'markings': {'type': 'string'},
                'light': {'type': 'select', 'options': ['soft sunlight', 'multi-directional studio light']},
                'background_type': {'type': 'select', 'options': ['white', 'gray', 'green', 'blue', 'black', 'sky with scattered clouds', 'gray gradient']},
                'camera_view_position': {'type': 'select', 'options': ['full-front', 'quarter-turn right', 'profile right', 'three-quarter front right', 'back to camera', 'three-quarter front left', 'profile left', 'quarter-turn left', 'bird’s-eye view', 'worm’s-eye view', 'full-front high-angle', 'quarter-turn right high-angle', 'profile right high-angle', 'three-quarter front right high-angle', 'back to camera high-angle', 'three-quarter front left high-angle', 'profile left high-angle', 'quarter-turn left high-angle', 'full-front low-angle', 'quarter-turn right low-angle', 'profile right low-angle', 'three-quarter front right low-angle', 'back to camera low-angle', 'three-quarter front left low-angle', 'profile left low-angle', 'quarter-turn left low-angle']},
                'camera_distance': {'type': 'string'},
                'camera_azimuth': {'type': 'string'},
                'camera_inclination': {'type': 'string'},
                'camera_twist': {'type': 'string'},
                'camera_pivot': {'type': 'string'},
                'camera_focal_length': {'type': 'string'},
                'image_name': {'type': 'string'},
            },
            '4_isolated_options': {
                'object_type': {'type': 'select', 'options': ['airship drone model M balloon envelope', 'airship drone model F balloon envelope', 'airship drone propeller engine group', 'airship drone gondola', 'ACSG emals catapult', 'ACSG arresting gate', 'drone hunter', 'drone Lyutiy', 'drone Hermes', 'VTOL drone launch pad', 'HPM model M', 'AESA model M', 'HEL model M', 'ARHUDFM buit-in drinking system', 'ARHUDFM SBCA option']},
                'main_size_width': {'type': 'string'},
                'main_size_length': {'type': 'string'},
                'main_size_height': {'type': 'string'},
                'material': {'type': 'select', 'options': ['solid composite', 'low glass plastic']},
                'orientation': {'type': 'select', 'options': ['normal', 'horizontal', 'vertical', 'slightly inclined position', 'middle inclined position']}, 
                'options_text': {'type': 'select', 'options': ['no additional options or payloads mounted', 'additional options and payload mounted including']},
                'options_text_2': {'type': 'string'},
                'state_description': {'type': 'string'},
                'color_scheme': {'type': 'select', 'options': ['light gray and light blue camouflage', 'light gray and light blue', 'light gray and dark blue', 'light gray and dark gray', 'yellow and dark pink']},
                'markings': {'type': 'string'},
                'light': {'type': 'select', 'options': ['soft sunlight', 'multi-directional studio light']},
                'background_type': {'type': 'select', 'options': ['white', 'gray', 'green', 'blue', 'black', 'sky with scattered clouds', 'gray gradient']},
                'camera_view_position': {'type': 'select', 'options': ['full-front', 'quarter-turn right', 'profile right', 'three-quarter front right', 'back to camera', 'three-quarter front left', 'profile left', 'quarter-turn left', 'bird’s-eye view', 'worm’s-eye view', 'full-front high-angle', 'quarter-turn right high-angle', 'profile right high-angle', 'three-quarter front right high-angle', 'back to camera high-angle', 'three-quarter front left high-angle', 'profile left high-angle', 'quarter-turn left high-angle', 'full-front low-angle', 'quarter-turn right low-angle', 'profile right low-angle', 'three-quarter front right low-angle', 'back to camera low-angle', 'three-quarter front left low-angle', 'profile left low-angle', 'quarter-turn left low-angle']},
                'camera_distance': {'type': 'string'},
                'camera_azimuth': {'type': 'string'},
                'camera_inclination': {'type': 'string'},
                'camera_twist': {'type': 'string'},
                'camera_pivot': {'type': 'string'},
                'camera_focal_length': {'type': 'string'},
                'image_name': {'type': 'string'},
            },
            '5_isolated_details': {
                'object_type': {'type': 'select', 'options': ['single airship drone propeller engine', 'ACSG emals catapult trolley', 'ACSG emals catapult trolley clamps', 'ACSG roll arresting wires', 'ACSG pitch-yaw arresting wires', 'ACSG counter-tension arresting wires', 'VTOL launch pad clamps']},
                'main_size_width': {'type': 'string'},
                'main_size_length': {'type': 'string'},
                'main_size_height': {'type': 'string'},
                'material': {'type': 'select', 'options': ['solid composite', 'low glass plastic']},
                'orientation': {'type': 'select', 'options': ['normal', 'horizontal', 'vertical', 'slightly inclined position', 'middle inclined position']}, 
                'options_text': {'type': 'select', 'options': ['no additional options or payloads mounted', 'additional options and payload mounted including']},
                'options_text_2': {'type': 'string'},
                'state_description': {'type': 'string'},
                'color_scheme': {'type': 'select', 'options': ['light gray and light blue camouflage', 'light gray and light blue', 'light gray and dark blue', 'light gray and dark gray', 'yellow and dark pink', 'semi-transparent light gray', 'solid black and red element']},
                'markings': {'type': 'string'},
                'light': {'type': 'select', 'options': ['soft sunlight', 'multi-directional studio light']},
                'background_type': {'type': 'select', 'options': ['white', 'gray', 'green', 'blue', 'black', 'sky with scattered clouds', 'gray gradient']},
                'camera_view_position': {'type': 'select', 'options': ['full-front', 'quarter-turn right', 'profile right', 'three-quarter front right', 'back to camera', 'three-quarter front left', 'profile left', 'quarter-turn left', 'bird’s-eye view', 'worm’s-eye view', 'full-front high-angle', 'quarter-turn right high-angle', 'profile right high-angle', 'three-quarter front right high-angle', 'back to camera high-angle', 'three-quarter front left high-angle', 'profile left high-angle', 'quarter-turn left high-angle', 'full-front low-angle', 'quarter-turn right low-angle', 'profile right low-angle', 'three-quarter front right low-angle', 'back to camera low-angle', 'three-quarter front left low-angle', 'profile left low-angle', 'quarter-turn left low-angle']},
                'camera_distance': {'type': 'string'},
                'camera_azimuth': {'type': 'string'},
                'camera_inclination': {'type': 'string'},
                'camera_twist': {'type': 'string'},
                'camera_pivot': {'type': 'string'},
                'camera_focal_length': {'type': 'string'},
                'image_name': {'type': 'string'},
           },
            '6_states_and_relationships': {
                'object_type': {'type': 'select', 'options': ['unmanned airship drone', 'arhudfm', 'airship drone propeller engine group', 'single airship drone propeller engine', 'ACSG emals catapult trolley', 'ACSG emals catapult trolley clamps', 'ACSG arresting gate', 'ACSG roll arresting wires', 'ACSG pitch-yaw arresting wires', 'ACSG counter-tension arresting wires', 'VTOL launch pad clamps', 'HEL model M']},
                'base_model': {'type': 'select', 'options': ['model M', 'model F', 'model One']},
                'modification': {'type': 'select', 'options': ['', 'basic', 'kit', 'ballistic', 'total kit', 'SBCA']},
                'state_type': {'type': 'select', 'options': ['empty without payload and drones on board', 'with drones on board', 'flying mode', 'during fine water discharge', 'during water intake', 'during water supply', 'VTOL mode', 'omnidrive mode', 'cruise speed mode', 'feather', 'high-pitch', 'low-pitch', 'flat-pitch', 'reverse-pitch', 'starting position', 'launching position', 'braking position', 'stopped position', 'engaged', 'released', 'raised position', 'lowered position', 'rigged state', 'pull-out state', 'loaded state', 'retracted state', 'high-angle', 'frontal-angle', 'low-angle']},
                'relationships': {'type': 'select', 'options': ['isolated', 'isolated with gondola', 'isolated with emals catapult and clamps', 'isolated with catapult trolley and clamps', 'isolated with arresting gate and other wires', 'isolated with arresting gate', 'isolated with VTOL launch pad', 'isolated with balloon envelope']},
                'relationships_2': {'type': 'string'},
                'light': {'type': 'select', 'options': ['soft sunlight', 'multi-directional studio light']},
                'background_type': {'type': 'select', 'options': ['white', 'gray', 'green', 'blue', 'black', 'sky with scattered clouds', 'gray gradient']},
                'camera_view_position': {'type': 'select', 'options': ['full-front', 'quarter-turn right', 'profile right', 'three-quarter front right', 'back to camera', 'three-quarter front left', 'profile left', 'quarter-turn left', 'bird’s-eye view', 'worm’s-eye view', 'full-front high-angle', 'quarter-turn right high-angle', 'profile right high-angle', 'three-quarter front right high-angle', 'back to camera high-angle', 'three-quarter front left high-angle', 'profile left high-angle', 'quarter-turn left high-angle', 'full-front low-angle', 'quarter-turn right low-angle', 'profile right low-angle', 'three-quarter front right low-angle', 'back to camera low-angle', 'three-quarter front left low-angle', 'profile left low-angle', 'quarter-turn left low-angle']},
                'camera_distance': {'type': 'string'},
                'camera_azimuth': {'type': 'string'},
                'camera_inclination': {'type': 'string'},
                'camera_twist': {'type': 'string'},
                'camera_pivot': {'type': 'string'},
                'camera_focal_length': {'type': 'string'},
                'image_name': {'type': 'string'},
           },
        }
    
    def update_category_list(self):
        """Updates the list of categories in the Combobox and, if desired, immediately displays the form."""
        categories = list(self.schemas_by_category.keys())
        self.category_cb['values'] = categories

        if categories:
            # Auto selection of the first category
            self.current_category.set(categories[0])
            # Show form immediately
            self.show_category_form(categories[0])

    def on_category_change(self, event=None):
        cat = self.current_category.get()
        if cat:
            self.show_category_form(cat)

    def show_category_form(self, cat):
        # Cleaning form
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entries.clear()
        self.current_row = {'category': cat}

        schema = self.schemas_by_category.get(cat, {})
        row = 0
        for field, config in schema.items():
            ttk.Label(self.scrollable_frame, text=field + ":").grid(row=row, column=0, sticky='w', padx=5, pady=2)
            if config['type'] == 'select' and config.get('options'):
                cb = ttk.Combobox(self.scrollable_frame, values=config['options'], width=210, state='readonly')
                cb.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
                self.entries[field] = cb
            else:
                e = ttk.Entry(self.scrollable_frame, width=210)
                e.grid(row=row, column=1, sticky='ew', padx=5, pady=2)
                self.entries[field] = e
            row += 1
        self.scrollable_frame.grid_columnconfigure(1, weight=1)
        self.status_label.config(text=f"Please fill out form for '{cat}'")

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def load_template(self):
        file = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data and 'category' in data[0]:
                cat = data[0]['category']
                if cat in self.schemas_by_category:
                    self.current_category.set(cat)
                    self.current_row.update(data[0])
                    self.show_category_form(cat)
                    # Insering values
                    for field, widget in self.entries.items():
                        if field in self.current_row:
                            widget.delete(0, tk.END)
                            widget.insert(0, str(self.current_row[field]))

    def clear_form(self):
        for widget in self.entries.values():
            widget.delete(0, tk.END)
        self.current_row = {'category': self.current_category.get()}
        self.status_label.config(text="The form is cleaned")

    def generate_caption_txt(self):
        cat = self.current_category.get()
        if not cat or not self.entries:
            messagebox.showerror("Error", "Select category and fill out form!")
            return

        # Assembly current_row
        self.current_row = {'category': cat}
        for field, widget in self.entries.items():
            self.current_row[field] = widget.get().strip()

        if not self.current_row.get('image_name'):
            counter_str = str(1)  # Без zfill для дефолта
            self.current_row['image_name'] = f"{cat.replace('_', '-')}_{counter_str}"

        # Selection template
        template = self.get_template(cat)
        if not template:
            messagebox.showerror("Error", f"Template doesn't exist for '{cat}'")
            return

        caption = template.format(**self.current_row)

        # Saving
        dataset_dir = Path("dataset") / cat
        dataset_dir.mkdir(parents=True, exist_ok=True)
        img_name = self.current_row['image_name']
        txt_path = dataset_dir / f"{img_name}.txt"
        txt_path.write_text(caption, encoding='utf-8')

        # Counter increment
        counter = self.image_counter.get(cat, 0) + 1
        self.image_counter[cat] = counter
        next_name = f"{cat.replace('_', '-')}_{str(counter)}"
        self.entries['image_name'].delete(0, tk.END)
        self.entries['image_name'].insert(0, next_name)

        self.status_label.config(text=f"Saved: {txt_path} (next: {next_name})")
        messagebox.showinfo("Done", f"Caption is saved in {txt_path}")

    def get_template(self, cat):
        templates = {
            '1_drone_entire_object': """[trigger] {object_type} {base_model}, huge size, {main_size_diameter} meter diameter, {main_size_length} meter length, {main_size_height} meter height, {material}, {orientation} orientation, {action}, engine group {engine_group}, {engine_count} {engine_rotor_count}-rotor {engine_rotor_blade_count}‑blade on rotor propeller engines {engines_composition}, engines in {engine_position} position, {engine_group_state}, {options_text} {options_text_2}, {state_description}, {color_scheme} paint, {markings} markings, {light}, {background_type} background, camera view position {camera_view_position}, camera distance {camera_distance} meter, camera azimuth {camera_azimuth}°, camera inclination {camera_inclination}°, camera twist {camera_twist}°, camera pivot {camera_pivot}, camera focal length {camera_focal_length} mm, {image_name}.png""",
            '2_headset_entire_object': """[trigger] {object_type} {base_model} {modification}, headset, {main_size_width} meter width, {main_size_length} meter length, {main_size_height} meter height, {material}, {orientation} orientation, {options_text} {options_text_2}, {state_description}, {color_scheme} paint, {markings} markings, {light}, {background_type} background, camera view position {camera_view_position}, camera distance {camera_distance} meter, camera azimuth {camera_azimuth}°, camera inclination {camera_inclination}°, camera twist {camera_twist}°, camera pivot {camera_pivot}, camera focal length {camera_focal_length} mm, {image_name}.png""",
            '3_large_nodes': """[trigger] {object_type}, large node, close-up shot, {main_size_width} meter width, {main_size_length} meter length, {main_size_height} meter height, {material}, {orientation} orientation, {options_text} {options_text_2}, {state_description}, {color_scheme} paint, {markings} markings, {light}, {background_type} background, camera view position {camera_view_position}, camera distance {camera_distance} meter, camera azimuth {camera_azimuth}°, camera inclination {camera_inclination}°, camera twist {camera_twist}°, camera pivot {camera_pivot}, camera focal length {camera_focal_length} mm, {image_name}.png""",
            '4_isolated_options': """[trigger] {object_type}, isolated option, {main_size_width} meter width, {main_size_length} meter length, {main_size_height} meter height, {material}, {orientation} orientation, {options_text} {options_text_2}, {state_description}, {color_scheme} paint, {markings} markings, {light}, {background_type} background, camera view position {camera_view_position}, camera distance {camera_distance} meter, camera azimuth {camera_azimuth}°, camera inclination {camera_inclination}°, camera twist {camera_twist}°, camera pivot {camera_pivot}, camera focal length {camera_focal_length} mm, {image_name}.png""",
            '5_isolated_details': """[trigger] {object_type}, isolated detail, {main_size_width} meter width, {main_size_length} meter length, {main_size_height} meter height, {material}, {orientation} orientation, {options_text} {options_text_2}, {state_description}, {color_scheme} paint, {markings} markings, {light}, {background_type} background, camera view position {camera_view_position}, camera distance {camera_distance} meter, camera azimuth {camera_azimuth}°, camera inclination {camera_inclination}°, camera twist {camera_twist}°, camera pivot {camera_pivot}, camera focal length {camera_focal_length} mm, {image_name}.png""",
            '6_states_and_relationships': """[trigger] {object_type} {base_model} {modification}, {state_type}, {relationships} {relationships_2}, {light}, {background_type} background, camera view position {camera_view_position}, camera distance {camera_distance} meter, camera azimuth {camera_azimuth}°, camera inclination {camera_inclination}°, camera twist {camera_twist}°, camera pivot {camera_pivot}, camera focal length {camera_focal_length} mm, {image_name}.png""",
        }
        return templates.get(cat)

if __name__ == "__main__":
    root = tk.Tk()
    app = CategoryJSONEditor(root)
    root.mainloop()
