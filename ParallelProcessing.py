import abc
import multiprocessing



class ParallelProcessing(abc.ABC):
    def __init__(self):
        self.group = None
        self.args = [None]
        self.kwargs = {}
        self.target = None
        self.name: str | None = None
        self.daemon: bool | None = None

        self.queue = multiprocessing.Queue(-1)
        self.runtime = multiprocessing.Process(
            group=self.group,
            args=self.args,
            kwargs=self.kwargs,
            target=self.target,
            name=self.name,
            daemon=self.daemon,
        )


