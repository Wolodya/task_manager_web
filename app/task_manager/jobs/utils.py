from task.read_from_file import ReadFileTask
from task.write2file import WriteFileTask


class TaskCreator:

    def create_task(self, task_type, *args, **kwargs):
        if task_type == 'WriteFileTask':
            return WriteFileTask
        elif task_type == 'ReadFileTask':
            return ReadFileTask
        else:
            raise ValueError(task_type)

