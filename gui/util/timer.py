import time

class TimedTask:
    def __init__(self, interval: float, task : callable):
        """
        interval: time in milliseconds between each task execution
        task: the task to execute
        """
        self.interval = interval
        self.task = task
        self.last_time = time.time()

    def update(self):
        current_time = time.time()
        # check if the interval has passed in milliseconds
        if (current_time - self.last_time) * 1000 >= self.interval:
            self.task()
            self.last_time = current_time

class TimerGroup:
    def __init__(self):
        self.timed_tasks = []

    def add_task(self, interval: float, task: callable):
        self.timed_tasks.append(TimedTask(interval, task))

    def tick(self):
        for task in self.timed_tasks:
            task.update()