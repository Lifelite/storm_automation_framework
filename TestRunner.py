import abc
import multiprocessing
import queue
from concurrent import futures


class TestRunner:
        queue = multiprocessing.Queue(-1)
        

