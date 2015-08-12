#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

"""
Tree ASCII View:

View Newick tree as ASCII.
Based on jeetsukumaran/DendroPy.
"""

import sys
import os
import re
import Tkinter as tk
import ttk
import ScrolledText as st
import tkFileDialog
import dendropy

__version__ = 'v0.2.4'

# If species name is longer than 50, the tree may not display correctly.
# You can modify this value if you need.
MAX_NAME_LEN = 60

HELP_MSG = """
    Newick Tree ASCII Viewer

    Version:  %s

    Please select Newick tree file.

        File -> Open -> example.nwk
""" % __version__

CUR_PATH = os.getcwd()


def arg_parser():
    arg_list = sys.argv
    if len(arg_list) > 2:
        raise ValueError('More than two arguments')
    elif len(arg_list) == 2:
        if not os.path.isfile(arg_list[1]) and \
                not os.path.isfile(os.path.join(CUR_PATH, arg_list[1])):
            raise IOError('No such file: %s' % arg_list[1])
        return arg_list[1]
    else:
        return None


class TreeASCIIViewGUI(tk.Frame, object):
    def __init__(self, tree_file_path, master=None):
        tk.Frame.__init__(self, master)
        self.tree_file_path = tree_file_path
        self.master.grid()
        self.set_style()
        self.create_menubar()
        self.create_widgets()

    def set_style(self):
        s = ttk.Style()

        s.configure('title.TLabel', padding='0 15 0 0')
        s.configure('title.TLabel', font=('Helvetica', 11))

    def create_menubar(self):
        self.menubar = tk.Menu(self.master)

        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label='Open', command=self.ask_open_file)
        self.file_menu.add_command(label='Save', command=lambda: print('Save'))
        self.file_menu.add_command(label='Exit', command=self.master.quit)
        self.menubar.add_cascade(label='File', menu=self.file_menu)

        self.config_menu = tk.Menu(self.menubar, tearoff=0)
        self.config_menu.add_command(
            label='Theme Config',
            command=lambda: print('Theme Config')
        )
        self.config_menu.add_command(
            label='Display Config',
            command=lambda: print('Display Config')
        )
        self.menubar.add_cascade(label='Config', menu=self.config_menu)

        self.help_menu = tk.Menu(self.master, tearoff=0)
        self.help_menu.add_command(label='Help', command=lambda: print('Help'))
        self.menubar.add_cascade(label='Help', menu=self.help_menu)

        self.master.config(menu=self.menubar)

    def create_widgets(self):
        """
        Left Pane:
            1. plot_metric
                   Label:  plot_metric_label
               Combo var:  plot_metric_var
                Combobox:  plot_metric_options
                  Button:  plot_metric_confirm_button

            2. display_width
                   Label:  plot_display_width_label
               Combo var:  display_width_var
                Combobox:  plot_display_width_options
                  Button:  plot_display_width_confirm_button

            3. leaf_spacing_factor
                   Label:  plot_leaf_spacing_factor_label
               Combo var:  leaf_spacing_var
                Combobox:  plot_leaf_spacing_factor_options
                  Button:  plot_leaf_spacing_factor_confirm_button

            4. show_internal_node_labels
                   Label:  plot_show_node_label_label
               Combo var:  show_node_label_var
                Combobox:  plot_show_node_label_options
                  Button:  plot_show_node_label_confirm_button

        Right Pane:
            ScrolledText: ascii_view_area
        """
        # ======================== Left Pane ============================
        # +----+-------------------+
        # |****|                   |
        # |****|                   |
        # |****|                   |
        # |****|                   |
        # |****|                   |
        # |****|                   |
        # |****|                   |
        # +----+-------------------+
        self.left_pane = ttk.Frame(self.master, padding=(10))
        self.left_pane.grid(row=0, column=0, sticky='wen')

        # ------------------------------------
        # ----------- plot_metric ------------
        # ------------------------------------
        self.plot_metric_label = ttk.Label(
            self.left_pane, text='Plot Metric', style='title.TLabel')
        self.plot_metric_label.grid(row=0, column=0, columnspan=2, sticky='w')

        self.plot_metric_var = tk.StringVar()
        self.plot_metric_options = ttk.Combobox(
            self.left_pane,
            textvariable=self.plot_metric_label,
            state='readonly')

        self.plot_metric_options['values'] = ['depth', 'level', 'age',
                                              'length']
        self.plot_metric_options.bind(
            '<<ComboboxSelected>>',
            self._refresh_tree_with_current_value
        )
        self.plot_metric_options.current('0')
        self.plot_metric_options.grid(
            row=1, column=0, columnspan=2, sticky='we')

        # ------------------------------------
        # ---------- display_width -----------
        # ------------------------------------
        self.plot_display_width_label = ttk.Label(
            self.left_pane, text='Display Width', style='title.TLabel')
        self.plot_display_width_label.grid(
            row=2, column=0, columnspan=2, sticky='w')

        self.display_width_scale = ttk.Scale(
            self.left_pane, from_=20, to=220, orient=tk.HORIZONTAL,
            value='100')
        self.display_width_scale.grid(
            row=3, column=0, sticky='we')

        self.plot_display_width_confirm_button = ttk.Button(
            self.left_pane, text='Confirm')
        self.plot_display_width_confirm_button.grid(
            row=3, column=1, sticky='w')

        # ------------------------------------
        # ------- leaf_spacing_factor --------
        # ------------------------------------
        self.plot_leaf_spacing_factor_label = ttk.Label(
            self.left_pane, text='Leaf Spacing Factor', style='title.TLabel')
        self.plot_leaf_spacing_factor_label.grid(
            row=4, column=0, columnspan=2, sticky='w')

        def _refresh_tree_for_leaf_spacing_factor(event):
            new_plot_metric = self.plot_metric_options.get()
            new_display_width = self.display_width_scale.get()
            new_leaf_spacing_factor = \
                self.plot_leaf_spacing_factor_options.get()
            new_show_internal_node_labels = self.show_node_label_var.get()
            self.display_tree(
                plot_metric=new_plot_metric,
                display_width=new_display_width,
                leaf_spacing_factor=new_leaf_spacing_factor,
                width=None,
                show_internal_node_labels=new_show_internal_node_labels)

        self.plot_leaf_spacing_factor_options = ttk.Combobox(
            self.left_pane,
            values=[1, 2, 3, 4, 5]
            )
        self.plot_leaf_spacing_factor_options.bind(
            "<<ComboboxSelected>>", _refresh_tree_for_leaf_spacing_factor)
        self.plot_leaf_spacing_factor_options.current('1')
        self.plot_leaf_spacing_factor_options.grid(
            row=5, column=0, columnspan=2, sticky='we')

        # ------------------------------------
        # --- show_internal_node_labels ------
        # ------------------------------------
        self.plot_show_node_label_label = ttk.Label(
            self.left_pane, text='Show Internal Node Label',
            style='title.TLabel')
        self.plot_show_node_label_label.grid(
            row=6, column=0, columnspan=2, sticky='w')

        modes = [
            ('Show Node Labels', 'True'),
            ('Not show', 'False')
        ]
        self.show_node_label_var = tk.StringVar()
        self.show_node_label_var.set('True')
        for i, (text, mode) in enumerate(modes):
            self.show_node_label_radiobutton = ttk.Radiobutton(
                self.left_pane, text=text, variable=self.show_node_label_var,
                value=mode, command=self._refresh_tree_with_new_opt)
            self.show_node_label_radiobutton.grid(
                row=7, column=i, sticky='we')

        # ------------------------------------
        # ----------- Refresh button ---------
        # ------------------------------------
        self.refresh_button = ttk.Button(
            self.left_pane,
            text='Reload Tree with Default Options')
        self.refresh_button.grid(row=8, column=0, columnspan=2, sticky='we')

        # ======================== Ploting Pane ==========================
        # +----+-------------------+
        # |    |*******************|
        # |    |*******************|
        # |    |*******************|
        # |    |*******************|
        # |    |*******************|
        # |    |*******************|
        # |    |*******************|
        # +----+-------------------+

        self.right_pane = ttk.Frame(self.master)
        self.right_pane.grid(row=0, column=1, sticky='wens')

        self.ascii_view_area = st.ScrolledText(
            self.right_pane,
            fg='#FDF6E3',
            bg='#002B36',
            font=('Consolas', 10))
        self.ascii_view_area.grid(row=0, column=0, sticky='wens')

        # ************************ Button Command **************************
        # 1. plot_metric
        #        Label:  plot_metric_label
        #    Combo var:  plot_metric_var
        #     Combobox:  plot_metric_options
        #       Button:  plot_metric_confirm_button
        #
        # 2. display_width
        #        Label:  plot_display_width_label
        #    Combo var:  display_width_var
        #     Combobox:  plot_display_width_options
        #       Button:  plot_display_width_confirm_button
        #
        # 3. leaf_spacing_factor
        #        Label:  plot_leaf_spacing_factor_label
        #    Combo var:  leaf_spacing_var
        #     Combobox:  plot_leaf_spacing_factor_options
        #       Button:  plot_leaf_spacing_factor_confirm_button
        #
        # 4. show_internal_node_labels
        #        Label:  plot_show_node_label_label
        #    Combo var:  show_node_label_var
        #     Combobox:  plot_show_node_label_options
        #       Button:  plot_show_node_label_confirm_button
        # ************************ Button Command **************************

        # Plot metric
        # self.reload_tree_with_current_opt(self.plot_metric_confirm_button)
        # Display width
        self.plot_display_width_confirm_button['command'] = \
            self._refresh_tree_with_new_opt
        # Reload button
        self.refresh_button['command'] = lambda: self.display_tree()

        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=0)
        self.master.columnconfigure(1, weight=1)
        for i in xrange(8):
            self.left_pane.rowconfigure(i, weight=0)
        self.left_pane.columnconfigure(0, weight=0)
        self.left_pane.columnconfigure(1, weight=0)
        self.right_pane.rowconfigure(0, weight=1)
        self.right_pane.columnconfigure(0, weight=1)

    def _refresh_tree_with_new_opt(self):
        new_plot_metric = self.plot_metric_options.get()
        new_display_width = self.display_width_scale.get()
        new_leaf_spacing_factor = \
            self.plot_leaf_spacing_factor_options.get()
        new_show_internal_node_labels = self.show_node_label_var.get()
        self.display_tree(
            plot_metric=new_plot_metric,
            display_width=new_display_width,
            leaf_spacing_factor=new_leaf_spacing_factor,
            width=None,
            show_internal_node_labels=new_show_internal_node_labels)

    def _refresh_tree_with_current_value(self, event):
        new_plot_metric = self.plot_metric_options.get()
        new_display_width = self.display_width_scale.get()
        new_leaf_spacing_factor = \
            self.plot_leaf_spacing_factor_options.get()
        new_show_internal_node_labels = self.show_node_label_var.get()
        self.display_tree(
            plot_metric=new_plot_metric,
            display_width=new_display_width,
            leaf_spacing_factor=new_leaf_spacing_factor,
            width=None,
            show_internal_node_labels=new_show_internal_node_labels)

    def display_tree(
            self,
            plot_metric='depth',
            display_width=100,
            leaf_spacing_factor=2,
            width=None,
            show_internal_node_labels=True,
            node_label_compose_fn=None,
            ):
        self.ascii_view_area['state'] = 'normal'
        if not self.tree_file_path:
            self.ascii_view_area.insert(
                'end',
                HELP_MSG
            )
        else:
            FLAG = 1
            # Check if name length is shorter than MAX_NAME_LEN
            error_list = []
            with open(self.tree_file_path, 'r') as f:
                species_name_list = parse_tree_str(f.read())
            for i, species_name in enumerate(species_name_list):
                if len(species_name) > MAX_NAME_LEN:
                    error_list.append('->  [ species %d ]  \t%s'
                                      % (i+1, species_name))
                    FLAG = 0
            if not FLAG:
                name_error_msg = \
                    '[ ERROR ]  All species names must be less than'\
                    ' %s characters (defined by: MAX_NAME_LEN)\n\n'\
                    '    You can change MAX_NAME_LEN to use longer names, '\
                    'although the tree may not display correctly with names'\
                    ' that long.\n\n\n%s\n\n%s\n\n'\
                    % (MAX_NAME_LEN, '\n'.join(error_list), HELP_MSG)
                self.ascii_view_area.insert(
                    'end',
                    name_error_msg
                )

            if FLAG:
                tree_obj = dendropy.Tree.get_from_path(
                    self.tree_file_path,
                    'newick'
                )
                self.ascii_view_area.delete('1.0', 'end')
                show_internal_node_labels = False if\
                    show_internal_node_labels == 'False' else True
                self.ascii_view_area.insert(
                    'end',
                    tree_obj.as_ascii_plot(
                        plot_metric=plot_metric,
                        display_width=int(display_width),
                        leaf_spacing_factor=int(leaf_spacing_factor),
                        width=width,
                        show_internal_node_labels=show_internal_node_labels,
                        node_label_compose_fn=None,
                    ))
            self.ascii_view_area['state'] = 'disabled'

    def ask_open_file(self):
        c = tkFileDialog.askopenfile(mode='r')
        try:
            run_app(tree_file_path=c.name)
        except AttributeError:
            pass


def parse_tree_str(tree_str):
    """Parse Newick tree string and return a list of names.
    """
    tree_str = tree_str.strip().replace('\n', '')\
        .replace('\t', ' ')
    if not tree_str:
        return None
    re_all_names = re.compile('[^(),;]+')
    all_names = re_all_names.findall(tree_str)
    tmp_list = []
    for i, name in enumerate(all_names):
        name = name.strip()
        if not name:
            continue
        if name[0] in {'#', ':', '>', '<', '/', '\\', ''}:
            continue
        if ':' in name:
            tmp_list.append(name.split(':')[0])
        if '#' in name:
            tmp_list.append(name.split('#')[0])
        elif len(name.split()) != 1:
            continue
        else:
            tmp_list.append(name)

    final_list = [_ for _ in tmp_list
                  if '#' not in _
                  and '/' not in _
                  and '\\' not in _
                  and '>' not in _
                  and '<' not in _
                  and ':' not in _
                  and ';' not in _
                  and ')' not in _
                  and '(' not in _]
    return final_list


def extract_pure_newick_tree_string(raw_tree_content):
    """Read tree content, parse, and return tree string"""
    tmp_tree_str = ''
    tree_start_flag = False
    lines = raw_tree_content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('('):
            tree_start_flag = True
        if not tree_start_flag:
            continue
        if line.startswith('//') or line.startswith('#'):
            break
        else:
            tmp_tree_str += line
    return tmp_tree_str


def generate_pure_newick_tree_file(orig_format_tree_file=None):
    """Generate a temp file with pure Newick tree string, return file name."""
    if not orig_format_tree_file:
        return '', ''
    dirname = os.path.dirname(r'%s' % orig_format_tree_file)
    basename = os.path.basename(r'%s' % orig_format_tree_file)
    bare_name, _, extension = basename.rpartition('.')
    pure_newick_file_name = '%s.pure_newick.%s' % (bare_name, extension)
    with open(orig_format_tree_file, 'r') as f:
        pure_newick_content = \
            extract_pure_newick_tree_string(f.read())
    with open(pure_newick_file_name, 'w') as f:
        f.write(pure_newick_content)
    return dirname, pure_newick_file_name


def run_app(tree_file_path=arg_parser()):
    dirname, pure_newick_file_name = \
        generate_pure_newick_tree_file(tree_file_path)

    t = TreeASCIIViewGUI(tree_file_path=pure_newick_file_name)
    t.display_tree()
    t.master.title('Tree ASCII View Window')
    t.master.geometry('1200x700')
    t.mainloop()
    if os.path.isfile(pure_newick_file_name):
        os.remove(pure_newick_file_name)


def main():
    run_app()


if __name__ == '__main__':
    main()
