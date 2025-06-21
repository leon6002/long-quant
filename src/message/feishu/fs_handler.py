import importlib.util
import yaml
import os
from message.feishu.fs_msg_format import plain_text

# Load command-to-script mapping at startup
with open("src/commands.yaml", "r") as f:
    COMMAND_MAP = yaml.safe_load(f)["commands"]

ALLOWED_PREFIXES = ["!", "/"]
def handle_command(command: str) -> str:
    command = command.strip().lower()
    if not any(command.startswith(prefix) for prefix in ALLOWED_PREFIXES):
        return plain_text(f"Command must start with one of the prefixes: {', '.join(ALLOWED_PREFIXES)}")
    command = command[1:].strip().lower()  # Assuming single-character prefixes
    command_name = command.split(' ')[0]
    command_args = command.split(' ')[1:]
    print(f'command_name is {command_name}')
    print(f"command_args is {command_args}")
    if command_name not in COMMAND_MAP:
        return plain_text('Unknown command')

    script_path = COMMAND_MAP[command_name]
    if not os.path.exists(script_path):
        return plain_text(f"Script {script_path} not found")

    module_name = os.path.splitext(os.path.basename(script_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print(f'module name is: {module_name}')
    try:
        # Assume each script has a `run()` function
        result = module.run(command_args)
        return result
    except Exception as e:
        return plain_text(f"Error executing script: {str(e)}")