import json
import os
import subprocess

import inquirer


def raw_configs(filename):
    with open(f"templates/{filename}", "r") as file:
        configs = json.load(file)
    return configs


def config_dicts(filename):
    configs = raw_configs(filename)
    global_config = configs["global"]
    for attribute in configs.keys():
        if type(configs[attribute]) == dict:
            for key, value in global_config.items():
                if key not in configs[attribute].keys():
                    configs[attribute][key] = value
            if any(
                elem in configs[attribute].keys()
                for elem in {"sub_point", "imperial", "metric"}
            ):
                if "imperial" in configs[attribute].keys():
                    for key, value in global_config.items():
                        if key not in configs[attribute]["imperial"].keys():
                            configs[attribute]["imperial"][key] = value
                if "metric" in configs[attribute].keys():
                    for key, value in global_config.items():
                        if key not in configs[attribute]["metric"].keys():
                            configs[attribute]["metric"][key] = value
                if "sub_point" in configs[attribute].keys():
                    for key, value in global_config.items():
                        if key not in configs[attribute]["sub_point"].keys():
                            configs[attribute]["sub_point"][key] = value
        elif type(configs[attribute]) == list:
            for element in configs[attribute]:
                for key, value in global_config.items():
                    if key not in element.keys():
                        element[key] = value
        else:
            raise Exception("config attribute must be dict or list, depending on type")
    return configs


def modify_prop(attribute, prop, configs, config_filename, parent=None):
    while True:
        if prop == "add a property":
            prop = input("Enter a new property:\n")
            if not prop:
                break
            if parent:
                configs[attribute][parent][prop] = None
            else:
                configs[attribute][prop] = None

        print(f"Modifying {prop} for {parent} {attribute}") if parent else print(
            f"Modifying {prop} for {attribute}"
        )
        prop_value = (
            configs[attribute][parent][prop] if parent else configs[attribute][prop]
        )
        print(f"Current value: {prop_value}")

        try:  # might need to type case depending on the property - i.e. booleans should not take text input - should be selection
            subprocess.call(
                ["osascript", "-e", 'tell application "Terminal" to activate']
            )
            value = input("Enter a new value:\n")
            print("")
            if not value:
                break
            if prop == "hide":
                value = bool(value)
            elif prop in {
                "x",
                "y",
                "x1",
                "x2",
                "y1",
                "y2",
                "width",
                "height",
                "font_size",
                "round",
                "point_weight",
                "line_width",
                "dpi",
                "rotation",
            }:
                value = int(value)
            elif prop in {"opacity"}:
                value = float(value)
                if not (0 <= value <= 1):
                    print("Try again: opacity must be between 0 and 1")

            if parent:
                configs[attribute][parent][prop] = value
            else:
                configs[attribute][prop] = value
        except Exception as e:
            print("configging error during modify_prop", e)
        with open(f"templates/{config_filename}", "w") as file:
            json.dump(configs, file, indent=2)


def query_props(attribute, configs, parent=None):
    props = None
    if parent:
        message = f"Select properties to modify for {parent} {attribute}"
        choices = configs[attribute][parent].keys()
    else:
        message = f"Select properties to modify for {attribute}"
        choices = configs[attribute].keys()
    while not props:
        question = [
            inquirer.Checkbox(
                "properties",
                message=message,
                choices=sorted(list(choices) + ["add a property"]),
            ),
        ]
        props = inquirer.prompt(question)["properties"]
    return props


def modify_child_props(attribute, parent, configs, config_filename):
    props = query_props(attribute, configs, parent)
    for prop in props:
        modify_prop(attribute, prop, configs, config_filename, parent)


def modify_template(config_filename):
    exit_choice = "*** exit ***"
    try:
        while True:
            configs = raw_configs(config_filename)
            subprocess.call(
                ["osascript", "-e", 'tell application "Terminal" to activate']
            )
            attribute = inquirer.list_input(
                "Select attribute to modify",
                choices=[exit_choice] + sorted(configs.keys()),
            )
            if attribute == exit_choice:
                break
            props = query_props(attribute, configs)
            for prop in props:
                if prop in ("sub_point", "imperial", "metric"):
                    modify_child_props(attribute, prop, configs, config_filename)
                else:
                    modify_prop(attribute, prop, configs, config_filename)
    except (KeyboardInterrupt, TypeError) as e:
        print(e)
    finally:
        window_number = int(
            subprocess.check_output(
                ["osascript", "-e", 'tell application "Preview" to count window']
            )
            .decode("utf-8")
            .replace("\n", "")
        )
        if window_number > 0:
            subprocess.call(
                [
                    "osascript",
                    "-e",
                    f'tell application "Preview" to close window {str(window_number)}',
                ]
            )
        for f in [
            demo_frame_filename,
            "./tmp/course/demo_frame_00.png",
            "./tmp/profile/demo_frame_00.png",
        ]:
            try:
                os.remove(f)
            except FileNotFoundError:
                print(f"File {f} not found.")
            except PermissionError:
                print(f"Permission denied to delete {f}.")
            except Exception as e:
                print(f"An error occurred while deleting {f}: {str(e)}")
