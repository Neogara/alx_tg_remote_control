import os
import json

prefix_name = "[assistant_config] "
assistants_config_path = os.path.join(os.path.dirname(__file__), "assistant_configs.json")


class AssistantInstance:
    def __init__(self, name, program_path, window_name, process_name):
        self.name = name
        self.program_path = program_path
        self.window_name = window_name
        self.process_name = process_name

        self.pre_check()

    def pre_check(self):
        if not os.path.exists(self.program_path):
            error_message = f"{prefix_name}[pre_check] Not found program file: {self.program_path}\n" \
                            f"Check {self.name} configuration in {assistants_config_path} file."
            print(error_message)
            raise FileNotFoundError(error_message)

    def __str__(self):
        return f"{self.name}: {self.program_path}, {self.window_name}, {self.process_name}"


class AssistantConfig:

    def __init__(self, config_path: str):
        self._assistant_instances: list[AssistantInstance] = []
        self.load_config_file(config_path)

    def load_config_file(self, config_path: str):
        print(f"{prefix_name}Loading config file: {config_path}")

        if not os.path.exists(config_path):
            print(f"{prefix_name}Config file not found: {config_path}")
            raise FileNotFoundError(f"Config file not found: {config_path}")

        load_data = json.load(open(config_path, "r", encoding="utf-8"))
        for value_item in load_data:
            if not value_item["active"]:
                continue

            instance = AssistantInstance(
                name=value_item["name"],
                program_path=value_item["program_path"],
                window_name=value_item["window_name"],
                process_name=value_item["process_name"],
            )
            self._assistant_instances.append(instance)

    def get_names(self):
        return [assistant_instance.name for assistant_instance in self._assistant_instances]

    def get_assistant_instance_by_name(self, name: str) -> AssistantInstance:
        for assistant_instance in self._assistant_instances:
            if assistant_instance.name == name:
                return assistant_instance
        return None

    def __str__(self):
        if len(self._assistant_instances) == 0:
            return "[ No assistant instances load ]"

        instance_str = "\n".join([assistant_instance.__str__() for assistant_instance in self._assistant_instances])
        return f"[\n{instance_str}\n]"

    def __repr__(self):
        return self.__str__()


AssistantInstances = AssistantConfig(assistants_config_path)
