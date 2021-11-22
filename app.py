# from rich.table import Table
from re import L
import rich
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree




# from textual import events
# from textual.app import App
# from textual.widgets import ScrollView
# from textual.widgets import Placeholder

import argparse
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from pprint import pprint as pp
from rich.pretty import pprint as rpp


def main_app(args):
    rpt_dir = Path(args.rpt_dir)
    csynth_xml_fp = rpt_dir/"csynth.xml"
    csynth_xml = ET.parse(csynth_xml_fp)
    
    csynth_xml_root = csynth_xml.getroot()

    user_assignments = []
    for el in csynth_xml_root.find("UserAssignments"):
        user_assignments.append([el.tag, el.text])
    # pp(user_assignments)

    design_hierarchy = []
    top_module = csynth_xml_root.find("RTLDesignHierarchy/TopModule")
    
    def build_design_hierarchy_data_object(starting_module, design_hierarchy):
        if starting_module.find("InstancesList"):
            instances = list(starting_module.find("InstancesList"))
        else:
            instances = []

        for instance in instances:
            inst_data = {el.tag: el.text for el in instance if el.tag not in ["InstancesList", "BindInstances"]}
            inst_data["InstancesList"] = []
            build_design_hierarchy_data_object(instance, inst_data["InstancesList"])
            design_hierarchy.append(inst_data)
    build_design_hierarchy_data_object(top_module, design_hierarchy)
    rpp(design_hierarchy)
    

    layout = Layout()
    layout.split_column(
        Layout(name="UserAssignments"),
        Layout(name="RTLDesignHierarchy")
    )

    user_assignments_table = Table()
    user_assignments_table.add_column("key", justify="right")
    user_assignments_table.add_column("val", justify="left")
    for item in user_assignments:
        user_assignments_table.add_row(*item)
    
    user_assignments_panel = Panel(user_assignments_table, title="UserAssignments")
    layout["UserAssignments"].update(user_assignments_panel)

    design_hierarchy_tree = Tree("RTLDesignHierarchy")
    

    rich.print(design_hierarchy_tree)


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"rpt_dir:{path} is not a valid path")

def cli():
    parser = argparse.ArgumentParser(description='Process and pretty print Vitis HLS synthesis reports')
    parser.add_argument('rpt_dir', help='report dir synthesis solution', type=dir_path)
    args = parser.parse_args()
    main_app(args)

if __name__ == "__main__":
    cli()
