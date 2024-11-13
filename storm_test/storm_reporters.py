from abc import ABC, abstractmethod


class StormReporter(ABC):

    @property
    def results(self):
        return self.results

    @results.setter
    def results(self, result_item):
        if not isinstance(self.results, list):
            self.results = []
        self.results.append(result_item)

    @abstractmethod
    def before_run(self, *args, **kwargs):
        pass

    @abstractmethod
    def after_run(self, *args, **kwargs):
        pass

    @abstractmethod
    def before_test(self, *args, **kwargs):
        pass

    @abstractmethod
    def after_test(self, *args, **kwargs):
        pass

    @abstractmethod
    def before_step(self, *args, **kwargs):
        pass

    @abstractmethod
    def after_step(self, *args, **kwargs):
        pass

class StormConsoleReporter(StormReporter):
    pass
