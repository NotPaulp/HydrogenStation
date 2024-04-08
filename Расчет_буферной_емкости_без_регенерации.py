import json
import os
import tkinter as tk
import re
from tkinter import filedialog
import sqlite3

class GUI:
    def __init__(self, root):
        self.root = root

        # <editor-fold desc="root init">
        root.title("Hydrogen Calculator")
        root.geometry("900x625")  # Initial window size
        root.configure(background='#cbecd0')
        # </editor-fold>
        # <editor-fold desc="Main vars">
        self.zoom_level=1.0
        self.name='Project'
        self.label_widgets=[]
        self.entries = {}
        self.label_values={}
        self.buttons = []
        self.frames=[]
        self.labels = [
            "Температура окр. среды, С | K",
            "Температура после компрессора, C | K",
            "Производительность компрессора, Нм3/ч | кг/ч",
            "Суточное производство водорода, кг",
            "Давление начальное в буфере, атм",
            "Объем 4 - х буферных емкостей, м3",
            "Плотность водорода при данных атм, кг/м3",
            "Масса водорода начальная в буфере, кг",
            "Газовая постоянная, Дж/моль*К",
            "Молярная масса, кг/моль",
        ]
        self.rows=0
        #константы
        self.gas_constant=8.314462618
        self.molar_mass=0.00201588
        self.initial_hydrogen_mass=None
        self.pressure_in_buffer=None
        self.font_size={}
        self.widget_width={}
        self.first_zoom=True
        self.prev_zoom_completed=True
        # </editor-fold>
        for i, label_text in enumerate(self.labels):
            label = tk.Label(root, text=label_text, font=("Arial",int(12*self.zoom_level)), padx=5, pady=5,borderwidth=1, relief="ridge",width=40)
            label.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            self.label_widgets.append(label)
        self.rows += len(self.labels)


        for i in range(len(self.labels)):
            frame = tk.Frame(self.root)
            frame.grid(row=i, column=2, padx=3, pady=5, sticky="ew")
            if i < 3:
                entry1 = tk.Entry(frame,  validate="key")
                entry1.bind("<KeyRelease>", self.on_entry_change)
                entry1.pack(side="left", fill="x", expand=True)
                entry1.config(font=("Arial", 14), width=10)
                entry2 = tk.Entry(frame, validate="key")
                entry2.bind("<KeyRelease>", self.on_entry_change)
                entry2.pack(side="left", fill="x", expand=True)
                entry2.config(font=("Arial", 14), width=10)
                self.entries["1. "+self.labels[i]] = entry1
                self.entries["2. "+self.labels[i]] = entry2
                if i<2:
                    entry1['validatecommand'] = (entry1.register(self.validate_float), "%P")
                    entry2['validatecommand'] = (entry2.register(self.validate_positive_float), "%P")
                    clear_button = tk.Button(root, font=("Arial", 12),text="❌",
                                             command=lambda e1=entry1, e2=entry2: self.clear_widgets(e1, e2))
                    clear_button.grid(row=i, column=3, padx=5, pady=5, sticky="ew")
                    self.buttons.append(clear_button)
                else:
                    entry1['validatecommand'] = (entry1.register(self.validate_positive_float), "%P")
                    entry2['validatecommand'] = (entry2.register(self.validate_positive_float), "%P")
            elif i<4:
                entry = tk.Entry(frame, validate="key")
                entry.bind("<KeyRelease>", self.on_entry_change)
                entry.pack(side="left", fill="x", expand=True)
                entry.config(font=("Arial", 14), width=10)
                entry['validatecommand'] = (entry.register(self.validate_positive_float), "%P")
                self.entries[self.labels[i]]=entry
                entry1 = self.entries["1. Производительность компрессора, Нм3/ч | кг/ч"]
                entry2 = self.entries["2. Производительность компрессора, Нм3/ч | кг/ч"]
                clear_button = tk.Button(root, font=("Arial", 12),text="❌",
                                         command=lambda e1=entry1,e2=entry2,e3=entry: self.clear_widgets(e1,e2,e3))
                clear_button.grid(row=i-1, column=3, rowspan=2,padx=5, pady=5, sticky="ew")
                self.buttons.append(clear_button)
            elif i<6:
                entry = tk.Entry(frame, validate="key")
                entry.bind("<KeyRelease>", self.on_entry_change)
                entry.pack(side="left", fill="x", expand=True)
                entry.config(font=("Arial", 14), width=10)
                entry['validatecommand'] = (entry.register(self.validate_positive_float), "%P")
                self.entries[self.labels[i]] = entry
                clear_button = tk.Button(root, font=("Arial", 12),text="❌",
                                         command=lambda e=entry: self.clear_widgets(e))
                clear_button.grid(row=i, column=3, padx=5, pady=5, sticky="ew")
                self.buttons.append(clear_button)
            else:
                label = tk.Label(root,borderwidth=1, relief="sunken",background='#f0f0f0')
                label.grid(row=i, column=2, padx=3, pady=5, sticky="ew")
                label.config(font=("Arial", 14), width=35)
                if self.labels[i]=="Газовая постоянная, Дж/моль*К":
                    label.config(text=str(self.gas_constant))
                elif self.labels[i]=="Молярная масса, кг/моль":
                    label.config(text=str(self.molar_mass))
                self.label_values[self.labels[i]]=(label)
            if frame:
                self.frames.append(frame)
        # <editor-fold desc="Create clear-all button">
        self.clear_all_button = tk.Button(root, font=("Arial", 12),text="❌", command=self.clear_all)
        self.clear_all_button.grid(row=len(self.labels),column=2, pady=5)
        self.buttons.append(self.clear_all_button)
        # </editor-fold>
        self.rows += 1

        root.bind("<MouseWheel>", self.zoom)

        self.widgets_rows={}
        for widget in self.label_widgets + self.frames + self.buttons + list(self.label_values.values()):
            self.widgets_rows[widget]=widget.grid_info()["row"]

        # <editor-fold desc="Create hide-show button">
        self.hide_show_button = tk.Button(root, font=("Arial",12),text="Спрятать данные",foreground='white',
                                          command=self.hide_show_main_inputs,background='#64c474')
        self.hide_show_button.grid(row=len(self.labels), column=1, pady=10,padx=10)
        self.buttons.append(self.hide_show_button)
        self.main_inputs_hidden = False
        # </editor-fold>
        # <editor-fold desc="Create second canvas, navigation and boxes frames">
        self.second_canvas = tk.Canvas(root, bg="#eff9f1")
        self.second_canvas.grid(row=self.rows, column=1, columnspan=2,rowspan=len(self.labels) + 1, padx=10, sticky="nsew")
        self.second_canvas.columnconfigure(0, weight=2)
        self.second_canvas.rowconfigure(0, weight=1)
        self.second_canvas_frame = tk.Frame(self.second_canvas,bg="#eff9f1")
        self.second_canvas_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.nav_frame=tk.Frame(self.second_canvas_frame,bg="#eff9f1")
        self.nav_frame.grid(column=0,row=0)
        self.boxes_frame=tk.Frame(self.second_canvas_frame,bg="#eff9f1")
        self.boxes_frame.grid(column=1,row=0,columnspan=2)
        self.manage_boxes_frame = tk.Frame(self.second_canvas_frame, bg="#eff9f1")
        self.manage_boxes_frame.grid(column=3, row=0)
        # </editor-fold>
        # <editor-fold desc="Second canvas main vars">
        self.objects_refills_frames=[]
        self.buffer_refills_frames=[]
        self.second_canvas_widgets={}
        self.second_canvas_widgets["Масса заправки H2, кг"]=list()
        self.second_canvas_widgets["Время заправки, ч"] = list()
        self.second_canvas_widgets["1. Давление, атм"] = list()
        self.second_canvas_widgets["1. Масса H2, кг"] = list()
        self.second_canvas_widgets["1. Плотность H2, кг"] = list()
        self.second_canvas_widgets["2. Давление, атм"] = list()
        self.second_canvas_widgets["2. Масса H2, кг"] = list()
        self.second_canvas_widgets["2. Плотность H2, кг"] = list()
        self.second_canvas_widgets["Заголовок"] = list()
        self.second_canvas_widgets_list=[
        "Масса заправки H2, кг",
        "Время заправки, ч",
        "1. Давление, атм",
        "1. Масса H2, кг",
        "1. Плотность H2, кг",
        "2. Давление, атм",
        "2. Масса H2, кг",
        "2. Плотность H2, кг",
        "Заголовок",
        ]
        # </editor-fold>
        self.create_default_refills()
        # <editor-fold desc="Create navigation">
        self.previous = tk.Button(self.nav_frame, text="▲", font=("Arial", 12), width=2,height=1,command= lambda: self.change_refills_row(-1))
        self.previous.grid(row=1,column=0,pady=5, padx=5,sticky="ew")

        self.current_fill = tk.Entry(self.nav_frame, validate="key", font=("Arial", 10),width=2,justify='center')
        self.current_fill.grid(row=2,column=0,pady=5, padx=5,sticky="ew")
        self.current_fill.bind("<KeyRelease>", self.change_refills_row)
        self.current_fill['validatecommand'] = (self.current_fill.register(self.validate_positive_integer), "%P")

        self.current_fill.insert(0,"1")

        self.following = tk.Button(self.nav_frame, text="▼", font=("Arial", 12),width=2, height=1,command= lambda: self.change_refills_row(1))
        self.following.grid(row=3,column=0,pady=5, padx=5,sticky="ew")
        self.second_canvas_widgets["Navigation"]=[self.previous,self.current_fill,self.following]
        # </editor-fold>
        # <editor-fold desc="Create manager">
        self.add_row = tk.Button(self.manage_boxes_frame, text="➕", font=("Arial", 12,),
                                    command=self.add_refills_row, foreground='white', background='green',
                                    activebackground='lightgreen')
        self.add_row.grid(row=0, column=0,  pady=5, padx=5, sticky="ew")
        self.clear_row = tk.Button(self.manage_boxes_frame, text="❌", font=("Arial", 12),
                                    command=self.clear_refills_row)
        self.clear_row.grid(row=1, column=0,  pady=5, padx=5, sticky="ew")
        self.delete_row = tk.Button(self.manage_boxes_frame, text="➖", font=("Arial", 12),
                                    command=self.delete_refills_row,foreground='white',background='darkred',activebackground='red')
        self.delete_row.grid(row=2, column=0, pady=5, padx=5, sticky="ew")
        self.second_canvas_widgets["Manager"]=[self.add_row,self.clear_row,self.delete_row]
        self.second_canvas_widgets["Manager"]=[self.add_row,self.clear_row,self.delete_row]
        self.current_fill_row=1
        # </editor-fold>
    def create_default_refills(self):
        # <editor-fold desc="1st row (visible)">
        object_refill_frame = tk.Frame(self.boxes_frame, bg="#eff9f1")
        object_refill_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        object_label_refill = tk.Label(object_refill_frame, text="Заправка объекта", font=("Arial",int(12*self.zoom_level)), padx=5,
                                       pady=0, borderwidth=1, relief="ridge",
                                       width=37, height=1)
        object_label_refill.grid(row=0, column=0, columnspan=2)
        for j in range(4):
            label1 = tk.Label(object_refill_frame, font=("Arial",int(12*self.zoom_level)), padx=5,
                              pady=0, borderwidth=1, relief="ridge",
                              width=63, height=1)
            label1.grid(row=j + 1, column=0)
            label1.config(font=("Arial", 12), width=18)
            if j < 1:
                entry = tk.Entry(object_refill_frame, validate="key")
                entry.bind("<KeyRelease>", self.on_entry_change)
                entry.grid(row=j + 1, column=1)
                entry.bind("<KeyRelease>", self.fill_object)
                entry.config(font=("Arial", 12), width=18)
                entry['validatecommand'] = (entry.register(self.validate_positive_float), "%P")
                label1.config(text="Масса заправки H2, кг")
                self.second_canvas_widgets["Масса заправки H2, кг"].append([label1, entry])
            else:
                label2 = tk.Label(object_refill_frame, borderwidth=1, relief="sunken", background='#f0f0f0')
                label2.grid(row=j + 1, column=1, padx=0, pady=0, sticky="e")
                label2.config(font=("Arial", 12), width=18)
                if j == 1:
                    label1.config(text="Давление, атм")
                    self.second_canvas_widgets["1. Давление, атм"].append([label1, label2])
                elif j == 2:
                    label1.config(text="Масса H2, кг")
                    self.second_canvas_widgets["1. Масса H2, кг"].append([label1, label2])
                elif j == 3:
                    label1.config(text="Плотность H2, кг")
                    self.second_canvas_widgets["1. Плотность H2, кг"].append([label1, label2])
        self.objects_refills_frames.append(object_refill_frame)
        buffer_refill_frame = tk.Frame(self.boxes_frame, bg="#eff9f1")
        buffer_refill_frame.grid(row=0, column=2, columnspan=2, padx=10, pady=5, sticky="ew")
        buffer_label_refill = tk.Label(buffer_refill_frame, text="Заправка буфера", font=("Arial",int(12*self.zoom_level)), padx=5,
                                       pady=0, borderwidth=1, relief="ridge",
                                       width=37, height=1)
        buffer_label_refill.grid(row=0, column=0, columnspan=2)

        for j in range(4):
            label1 = tk.Label(buffer_refill_frame, font=("Arial", int(12*self.zoom_level)), padx=5,
                              pady=0, borderwidth=1, relief="ridge",
                              width=63, height=1)
            label1.grid(row=j + 1, column=0)
            label1.config(font=("Arial", 12), width=18)
            if j == 0:
                entry = tk.Entry(buffer_refill_frame, validate="key")
                entry.bind("<KeyRelease>", self.on_entry_change)
                entry.grid(row=j + 1, column=1)
                entry.config(font=("Arial", int(12*self.zoom_level)), width=18)
                entry['validatecommand'] = (entry.register(self.validate_positive_float), "%P")
                entry.bind("<KeyRelease>", self.fill_buffer)
                label1.config(text="Время заправки, ч")
                self.second_canvas_widgets["Время заправки, ч"].append([label1, entry])
            else:
                label2 = tk.Label(buffer_refill_frame, borderwidth=1, relief="sunken", background='#f0f0f0')
                label2.grid(row=j + 1, column=1, padx=0, pady=0, sticky="e")
                label2.config(font=("Arial", int(12*self.zoom_level)), width=18)
                if j == 1:
                    label1.config(text="Давление, атм")
                    self.second_canvas_widgets["2. Давление, атм"].append([label1, label2])
                elif j == 2:
                    label1.config(text="Масса H2, кг")
                    self.second_canvas_widgets["2. Масса H2, кг"].append([label1, label2])
                elif j == 3:
                    label1.config(text="Плотность H2, кг")
                    self.second_canvas_widgets["2. Плотность H2, кг"].append([label1, label2])
        self.second_canvas_widgets["Заголовок"].append([object_label_refill, buffer_label_refill])
        self.buffer_refills_frames.append(buffer_refill_frame)
        # </editor-fold>
    def add_refills_row(self):
        try:
            n=int(self.current_fill.get())
        except ValueError:
            n=1
        # <editor-fold desc="n-th row (hiden)">
        # <editor-fold desc="Create n-th row">
        object_refill_frame = tk.Frame(self.boxes_frame, bg="#eff9f1")
        object_refill_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        object_label_refill = tk.Label(object_refill_frame, text="Заправка объекта", font=("Arial", 12), padx=5,
                                       pady=0, borderwidth=1, relief="ridge",
                                       width=37, height=1)
        object_label_refill.grid(row=0, column=0, columnspan=2)
        for j in range(4):
            label1 = tk.Label(object_refill_frame, font=("Arial",int(12*self.zoom_level)), padx=5,
                              pady=0, borderwidth=1, relief="ridge",
                              width=63, height=1)
            label1.grid(row=j + 1, column=0)
            label1.config(font=("Arial", 12), width=18)
            if j < 1:
                entry = tk.Entry(object_refill_frame, validate="key")
                entry.bind("<KeyRelease>", self.on_entry_change)
                entry.grid(row=j + 1, column=1)
                entry.bind("<KeyRelease>", self.fill_object)
                entry['validatecommand'] = (entry.register(self.validate_positive_float), "%P")
                entry.config(font=("Arial", 12), width=18)
                entry.insert(0, self.second_canvas_widgets["Масса заправки H2, кг"][n-1][1].get())
                label1.config(text="Масса заправки H2, кг")
                self.second_canvas_widgets["Масса заправки H2, кг"].insert(n, [label1, entry])
            else:
                label2 = tk.Label(object_refill_frame, borderwidth=1, relief="sunken", background='#f0f0f0')
                label2.grid(row=j + 1, column=1, padx=0, pady=0, sticky="e")
                label2.config(font=("Arial", 12), width=18)
                if j == 1:
                    label1.config(text="Давление, атм")
                    self.second_canvas_widgets["1. Давление, атм"].insert(n, [label1, label2])
                elif j == 2:
                    label1.config(text="Масса H2, кг")
                    self.second_canvas_widgets["1. Масса H2, кг"].insert(n, [label1, label2])
                elif j == 3:
                    label1.config(text="Плотность H2, кг")
                    self.second_canvas_widgets["1. Плотность H2, кг"].insert(n, [label1, label2])
        self.objects_refills_frames.insert(n, object_refill_frame)
        buffer_refill_frame = tk.Frame(self.boxes_frame, bg="#eff9f1")
        buffer_refill_frame.grid(row=0, column=2, columnspan=2, padx=10, pady=5, sticky="ew")
        buffer_label_refill = tk.Label(buffer_refill_frame, text="Заправка буфера", font=("Arial",12), padx=5,
                                       pady=0, borderwidth=1, relief="ridge",
                                       width=37, height=1)
        buffer_label_refill.grid(row=0, column=0, columnspan=2)
        for j in range(4):
            label1 = tk.Label(buffer_refill_frame, font=("Arial", 12), padx=5,
                              pady=0, borderwidth=1, relief="ridge",
                              width=63, height=1)
            label1.grid(row=j + 1, column=0)
            label1.config(font=("Arial", 12), width=18)
            if j == 0:
                entry = tk.Entry(buffer_refill_frame, validate="key")
                entry.bind("<KeyRelease>", self.on_entry_change)
                entry.grid(row=j + 1, column=1)
                entry.config(font=("Arial", 12), width=18)
                entry.bind("<KeyRelease>", self.fill_buffer)
                entry['validatecommand'] = (entry.register(self.validate_positive_float), "%P")
                entry.insert(0,self.second_canvas_widgets["Время заправки, ч"][n-1][1].get())
                label1.config(text="Время заправки, ч")
                self.second_canvas_widgets["Время заправки, ч"].insert(n, [label1, entry])
            else:
                label2 = tk.Label(buffer_refill_frame, borderwidth=1, relief="sunken", background='#f0f0f0')
                label2.grid(row=j + 1, column=1, padx=0, pady=0, sticky="e")
                label2.config(font=("Arial", 12), width=18)
                if j == 1:
                    label1.config(text="Давление, атм")
                    self.second_canvas_widgets["2. Давление, атм"].insert(n, [label1, label2])
                elif j == 2:
                    label1.config(text="Масса H2, кг")
                    self.second_canvas_widgets["2. Масса H2, кг"].insert(n, [label1, label2])
                elif j == 3:
                    label1.config(text="Плотность H2, кг")
                    self.second_canvas_widgets["2. Плотность H2, кг"].insert(n, [label1, label2])
        self.second_canvas_widgets["Заголовок"].insert(n, [object_label_refill, buffer_label_refill])
        self.buffer_refills_frames.insert(n, buffer_refill_frame)
        # </editor-fold>
        # <editor-fold desc="Hide n-th row">
        object_refill_frame.grid_remove()
        buffer_refill_frame.grid_remove()
        # </editor-fold>
        # </editor-fold>
        self.fill_object(None,n-1)
    def clear_refills_row(self):
        try:
            n=int(self.current_fill.get())
        except ValueError:
            n=1
        self.second_canvas_widgets["Масса заправки H2, кг"][n - 1][1].delete(0,"end")
        self.second_canvas_widgets["Время заправки, ч"][n - 1][1].delete(0, "end")
        self.fill_object(None,n-1)
    def delete_refills_row(self):
        def delete_data(n):
            for key in self.second_canvas_widgets_list:
                self.second_canvas_widgets[key].pop(n-1)
            self.objects_refills_frames.pop(n-1)
            self.buffer_refills_frames.pop(n-1)
        rows = len(self.objects_refills_frames)
        if rows<2:
            return False
        try:
            n=int(self.current_fill.get())
        except ValueError:
            n=1
        self.hide_refills(n)
        last_row = (n == rows)
        if last_row:
            self.change_refills_row(-1)
        delete_data(n)
        if not(last_row):
            self.fill_object(None,n-1)
            self.show_refills(n)
    def change_refills_row(self,change):
        n=self.current_fill_row
        self.hide_refills(n)
        if not(isinstance(change,tk.Event)):
            n += change
        else:
            try:
                n=int(self.current_fill.get())
            except ValueError:
                n=1
        min_n = 1
        max_n = len(self.objects_refills_frames)
        n = max(min_n, n)
        n = min(max_n, n)
        self.current_fill.delete(0, "end")
        self.current_fill.insert(0, str(n))
        self.show_refills(n)
        self.current_fill_row=n
    def hide_refills(self,n):
        self.objects_refills_frames[n-1].grid_remove()
        self.buffer_refills_frames[n-1].grid_remove()
    def show_refills(self,n):
        self.objects_refills_frames[n - 1].grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.buffer_refills_frames[n - 1].grid(row=0, column=2, columnspan=2, padx=10, pady=5, sticky="ew")
        self.zoom_font()
    def hide_show_main_inputs(self):
        def check_widget(widget):

            widgets_to_keep=[self.hide_show_button, self.label_widgets[7],
                          self.label_values["Масса водорода начальная в буфере, кг"],
                          self.clear_all_button]
            for staying_widget in widgets_to_keep:
                if widget==staying_widget:
                    return False
            return True

        self.main_inputs_hidden = not self.main_inputs_hidden
        if self.main_inputs_hidden:
            self.hide_show_button.config(text="Показать данные")
        else:
            self.hide_show_button.config(text="Спрятать данные")
        for widget in self.label_widgets + self.frames + self.buttons + list(self.label_values.values()):
            if self.main_inputs_hidden and check_widget(widget):
                widget.grid_remove()
            else:
                widget.grid()
    def on_entry_change(self, event):

        if isinstance(event,tk.Event):
            value = (event.widget.get())
            other_entry=None
            another_entry=None
            if event.widget == self.entries["1. Температура окр. среды, С | K"]:
                other_entry = self.entries["2. Температура окр. среды, С | K"]
                if self.isfloat(value):
                    value = float(value)
                    value+=273.15
            elif event.widget == self.entries["2. Температура окр. среды, С | K"]:
                other_entry = self.entries["1. Температура окр. среды, С | K"]
                if self.isfloat(value):
                    value = float(value)
                    value -= 273.15
            elif event.widget == self.entries["1. Температура после компрессора, C | K"]:
                other_entry = self.entries["2. Температура после компрессора, C | K"]
                if self.isfloat(value):
                    value = float(value)
                    value += 273.15
            elif event.widget == self.entries["2. Температура после компрессора, C | K"]:
                other_entry = self.entries["1. Температура после компрессора, C | K"]
                if self.isfloat(value):
                    value = float(value)
                    value -= 273.15
            elif event.widget == self.entries["1. Производительность компрессора, Нм3/ч | кг/ч"]:
                other_entry = self.entries["2. Производительность компрессора, Нм3/ч | кг/ч"]
                another_entry = self.entries["Суточное производство водорода, кг"]
                if self.isfloat(value):
                    value = float(value)
                    value *= 0.089
                    value2 = 24 * value
            elif event.widget == self.entries["2. Производительность компрессора, Нм3/ч | кг/ч"]:
                other_entry = self.entries["1. Производительность компрессора, Нм3/ч | кг/ч"]
                another_entry = self.entries["Суточное производство водорода, кг"]
                if self.isfloat(value):
                    value = float(value)
                    value2 = 24 * value
                    value /= 0.089
            elif event.widget == self.entries["Суточное производство водорода, кг"]:
                other_entry = self.entries["1. Производительность компрессора, Нм3/ч | кг/ч"]
                another_entry=self.entries["2. Производительность компрессора, Нм3/ч | кг/ч"]
                if self.isfloat(value):
                    value = float(value)
                    value2 = value / 24
                    value = value / 0.089 / 24
            if other_entry:
                other_entry.delete(0, "end")
                if self.isfloat(value):
                    text=str(round(value,2))
                else:
                    text=''
                other_entry.insert(0, text)
            if another_entry:
                if self.isfloat(value):
                    text=str(round(value2,2))
                else:
                    text=''
                another_entry.delete(0, "end")
                another_entry.insert(0, text)

        self.temp_after_the_compressor=self.entries["1. Температура после компрессора, C | K"].get()
        self.pressure_in_buffer=self.entries["Давление начальное в буфере, атм"].get()
        if self.isfloat(self.temp_after_the_compressor) and self.isfloat(self.pressure_in_buffer):
            self.temp_after_the_compressor=float(self.temp_after_the_compressor)
            self.pressure_in_buffer=float(self.pressure_in_buffer)
            self.hydrogen_density=((self.pressure_in_buffer*100000*self.molar_mass)
                                   /(self.gas_constant*(self.temp_after_the_compressor+273.15)))\
                                  /(1.004272516-0.001081602*self.temp_after_the_compressor
                                    +0.006891594*(self.pressure_in_buffer/10))
            self.hydrogen_density=round(self.hydrogen_density,8)
        else:
            self.hydrogen_density=''
        self.label_values["Плотность водорода при данных атм, кг/м3"].config(text=str(self.hydrogen_density))

        self.buffer_volume=self.entries["Объем 4 - х буферных емкостей, м3"].get()
        if self.isfloat(self.buffer_volume) and self.isfloat(self.hydrogen_density):
            self.buffer_volume=float(self.buffer_volume)
            self.initial_hydrogen_mass=round(self.buffer_volume*self.hydrogen_density,8)
        else:
            self.initial_hydrogen_mass=""
        self.label_values["Масса водорода начальная в буфере, кг"].config(text=str(self.initial_hydrogen_mass))
        self.fill_object(None,0)
    def isfloat(self,value):
        try:
            value=float(value)
            if value>=0:
                return 1
            else:
                return -1
        except TypeError:
            return 0
        except ValueError:
            return 0
    def calc_values(self,row,type,value,error=False):
        type_coef={'Object':-1,'Buffer':1}
        # <editor-fold desc="Default return vals">
        final_pressure = ""
        final_mass = ""
        final_density = ""
        final_values=[final_pressure,final_mass,final_density]
        # </editor-fold>
        # <editor-fold desc="Error return">
        if error:
            return final_values
        # </editor-fold>
        # <editor-fold desc="Calc mass">
        if type=='Object':
            mass=value
        elif type=='Buffer':
            compressor_capacity=self.entries["2. Производительность компрессора, Нм3/ч | кг/ч"].get()
            if self.isfloat(compressor_capacity):
                mass=float(value)*float(compressor_capacity)
            else:
                return final_values
        else:
            raise Exception("The type is neither Object or Buffer")
        # </editor-fold>
        # <editor-fold desc="Calc init mass and init pressure">
        if row == 0 and type=='Object':
            initial_mass = self.initial_hydrogen_mass
            initial_pressure = self.pressure_in_buffer
        elif type=='Buffer':
            initial_mass = self.second_canvas_widgets["1. Масса H2, кг"][row][1]['text']
            initial_pressure = self.second_canvas_widgets["1. Давление, атм"][row][1]['text']
        else:
            initial_mass = self.second_canvas_widgets["2. Масса H2, кг"][row - 1][1]['text']
            initial_pressure = self.second_canvas_widgets["2. Давление, атм"][row - 1][1]['text']
        # </editor-fold>
        if self.isfloat(initial_mass)>0 and self.isfloat(initial_pressure)>0:
            final_mass=float(initial_mass)+type_coef[type]*float(mass)
            if final_mass>0 or type_coef[type]>0:
                final_density = final_mass/self.buffer_volume
                temp_C=float(self.entries["1. Температура после компрессора, C | K"].get())
                temp_K=float(self.entries["2. Температура после компрессора, C | K"].get())
                final_pressure = ((final_density*(0.922332+0.0000676*temp_C+0.013839*final_density))*temp_K*self.gas_constant/self.molar_mass)/100000
                final_values=[round(final_pressure,2),round(final_mass,2),round(final_density,2)]
                return final_values
            else:
                final_pressure = "НЕ ХВАТАЕТ"
                final_mass = "ВОДОРОДА"
                final_density = "В БУФФЕРЕ"
                final_values=[final_pressure,final_mass,final_density]
                return final_values
        else:
            return final_values
    def fill_object(self,event,current_row=-1):
        if current_row==-1:
            current_row=int(self.current_fill.get())-1
        entry = self.second_canvas_widgets["Масса заправки H2, кг"][current_row][1]
        object_mass = entry.get()
        final_pressure, final_mass, final_density = '', '', ''
        if self.isfloat(object_mass)>0:
            final_pressure,final_mass,final_density=(self.calc_values(current_row,'Object',object_mass))
        init_pressure = self.entries["Давление начальное в буфере, атм"].get()
        if self.isfloat(final_pressure) and self.isfloat(init_pressure):
            if final_pressure>float(init_pressure):
                color='darkred'
            else:
                color='black'
        else:
            color = 'black'
        self.second_canvas_widgets['1. Давление, атм'][current_row][1].config(foreground=color)
        self.second_canvas_widgets['1. Давление, атм'][current_row][1].config(text=str(final_pressure))
        self.second_canvas_widgets["1. Масса H2, кг"][current_row][1].config(text=str(final_mass))
        self.second_canvas_widgets["1. Плотность H2, кг"][current_row][1].config(text=str(final_density))
        self.fill_buffer(None,current_row)
    def fill_buffer(self,event,current_row=-1):
        if current_row==-1:
            current_row=int(self.current_fill.get())-1
        entry = self.second_canvas_widgets["Время заправки, ч"][current_row][1]
        refill_time=entry.get()
        final_pressure, final_mass, final_density = '', '', ''
        if self.isfloat(refill_time)>0:
            final_pressure, final_mass, final_density = (self.calc_values(current_row, 'Buffer', refill_time))
        init_pressure=self.entries["Давление начальное в буфере, атм"].get()
        if self.isfloat(final_pressure) and self.isfloat(init_pressure):
            if final_pressure > float(init_pressure):
                color = 'darkred'
            else:
                color = 'black'
        else:
            color = 'black'
        self.second_canvas_widgets['2. Давление, атм'][current_row][1].config(foreground=color)
        self.second_canvas_widgets["2. Давление, атм"][current_row][1].config(text=str(final_pressure))
        self.second_canvas_widgets["2. Масса H2, кг"][current_row][1].config(text=str(final_mass))
        self.second_canvas_widgets["2. Плотность H2, кг"][current_row][1].config(text=str(final_density))
        if len(self.objects_refills_frames)>current_row+1:
            self.fill_object(None, current_row+1)
    def zoom(self, event):
        if event.state & 0x4 and self.prev_zoom_completed:
            self.prev_zoom_completed = False
            if event.delta > 0 and self.zoom_level < 2.0:
                self.zoom_level += 0.05
            elif event.delta < 0 and self.zoom_level > 0.5:
                self.zoom_level -= 0.05
            self.zoom_font()
            self.first_zoom = False
    def zoom_font(self):
        for widget in self.label_widgets+ list(self.label_values.values())+list(self.entries.values())+ self.buttons+list(self.second_canvas_widgets.values()):
            self._zoom_font(widget)
        self.prev_zoom_completed=True
    def _zoom_font(self, widget):
        if isinstance(widget, list):
            for sub_widget in widget:
                self._zoom_font(sub_widget)
        else:
            current_font_style = widget.cget('font').split(' ')
            font = current_font_style[0]
            if self.font_size.get(widget,None)==None:
                self.font_size[widget]=int(current_font_style[1])
            size=self.font_size[widget]
            if widget.winfo_exists():
                widget.config(font=(font, int(size * self.zoom_level)))
    def clear_widgets(self, *widgets):
        for widget in widgets:
            if isinstance(widget,tk.Entry):
                widget.delete(0, "end")
                event = tk.Event()
                event.type = tk.EventType.KeyRelease
                event.widget = widget
                self.on_entry_change(event)
            elif isinstance(widget, tk.Label):
                widget.config(text="")
    def clear_all(self):
        for entry in self.entries.values():
            if isinstance(entry, list):
                for e in entry:
                    e.delete(0, "end")
                    self.clear_widgets(e)
            else:
                entry.delete(0, "end")
                self.clear_widgets(entry)
    def validate_positive_integer(self, value):
        if value.isdigit() or value=='':
            return True
        else:
            return False
    def validate_positive_float(self, value):
        if re.match(r'^\d*\.?\d*$', value):
            return True
        else:
            return False
    def validate_float(self,value):
        try:
            if value!='-' and value!='':
                float(value)
            return True
        except ValueError:
            return False
    def get_entries(self):
        self.all_entries={}
        for key,entry in self.entries.items():
            self.all_entries[key]=entry.get()
        self.all_entries["Время заправки, ч"] = list()
        for widgets in self.second_canvas_widgets["Время заправки, ч"]:
            self.all_entries["Время заправки, ч"].append(widgets[1].get())
        self.all_entries["Масса заправки H2, кг"] = list()
        for widgets in self.second_canvas_widgets["Масса заправки H2, кг"]:
            self.all_entries["Масса заправки H2, кг"].append(widgets[1].get())
        return self.all_entries
    def set_entries(self,data):
        for key,value in data:
            if key!='Время заправки, ч' and key!='Масса заправки H2, кг':
                if key!='name':
                    self.entries[key].delete(0, "end")
                    self.entries[key].insert(0,value)

            else:
                value = json.loads(value)
                while len(value)>len(self.second_canvas_widgets['Масса заправки H2, кг']):
                    self.add_refills_row()
                while len(value)<len(self.second_canvas_widgets['Масса заправки H2, кг']):
                    self.delete_refills_row()
                for i in range(len(value)):
                    if key=='Время заправки, ч':
                        self.second_canvas_widgets['Время заправки, ч'][i][1].delete(0, "end")
                        self.second_canvas_widgets['Время заправки, ч'][i][1].insert(0, value[i])
                    else:
                        self.second_canvas_widgets['Масса заправки H2, кг'][i][1].delete(0, "end")
                        self.second_canvas_widgets['Масса заправки H2, кг'][i][1].insert(0, value[i])
        self.on_entry_change(tk.Event)
        self.fill_object(None, 0)
    def set_name(self,name):
        self.name=name
    def get_name(self):
        return self.name
class MainMenu:
    def __init__(self, root, gui_instance):
        self.root = root
        self.gui = gui_instance

        menubar = tk.Menu(root)
        root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_command(label="Save Project As...", command=self.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)


    def open_project(self):
        file_path = filedialog.askdirectory()
        if file_path:
            parts=file_path.split("/")
            name=parts[-1]
            database=f'{file_path}/{name}.db'
            if os.path.isfile(database):
                connection = sqlite3.connect(database)
                cursor = connection.cursor()
                try:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='data';")
                    table_exists = cursor.fetchone() is not None

                    if table_exists:
                        cursor.execute("SELECT * FROM data;")
                        data = cursor.fetchall()
                        app.set_entries(data)
                        app.set_name(file_path)
                finally:
                    connection.close()

    def save_project(self):
        file_path=app.get_name()
        self.write_db(file_path)


    def save_project_as(self):
        file_path = filedialog.asksaveasfilename(filetypes=[("Your Project","*")])
        if file_path:
            self.write_db(file_path)

    def write_db(self,file_path):
        parts = file_path.split("/")
        path = "/".join(parts[:-1])
        name = parts[-1]
        if not (os.path.isdir(file_path)):
            os.mkdir(file_path)
        database = f"{file_path}/{name}.db"
        connection = sqlite3.connect(database)
        cursor=connection.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='data';")
        table_exists = cursor.fetchone() is not None
        if table_exists:
            delete_all_rows = f'DELETE FROM data;'
            cursor.execute(delete_all_rows)
        else:
            create_table_sql = f'CREATE TABLE data (key TEXT, value TEXT);'
            cursor.execute(create_table_sql)
        data_to_insert = app.get_entries()
        insert_data = f'INSERT INTO data (key, value) VALUES (?, ?);'
        cursor.execute(insert_data, ("name", file_path))
        for key, value in data_to_insert.items():
            if isinstance(value, list):
                value = json.dumps(value)
            cursor.execute(insert_data, (key, value))

        connection.commit()
        connection.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    main_menu = MainMenu(root, app)
    root.mainloop()

