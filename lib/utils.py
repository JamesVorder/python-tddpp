import os
import shutil


class CodeGenSandbox:

    project_path: str
    class_skeleton_path: str
    test_path: str
    sandbox_path: str

    def __init__(self, project_path: str, class_skeleton_path: str, test_path: str, sandbox_path: str):
        assert os.path.exists(project_path), "The project_dir directory does not exist!"
        assert os.path.exists(os.path.join(project_path, class_skeleton_path)), "The class_skeleton path does not exist!"
        assert os.path.exists(os.path.join(project_path, test_path)), "The test_path path does not exist!s"
        self.project_path = project_path
        self.class_skeleton_path = class_skeleton_path
        self.test_path = test_path
        self.sandbox_path = sandbox_path

    def init_sandbox(self) -> None:
        if os.path.exists(self.sandbox_path):
            shutil.rmtree(self.sandbox_path)
        # os.makedirs(self.sandbox_path)
        shutil.copytree(self.project_path, self.sandbox_path)

    def get_sandboxed_project_path(self) -> str:
        return self.sandbox_path

    def get_sandboxed_test_path(self) -> str:
        return os.path.join(self.sandbox_path, self.test_path)

    def get_sandboxed_class_path(self) -> str:
        return os.path.join(self.sandbox_path, self.class_skeleton_path)