#! /usr/bin/env python

from __future__ import print_function
from locust import Locust, TaskSet, task

class MyTaskSet(TaskSet):
    @task
    def my_task(self):
        print("Executing my task.")

class MyLocust(Locust):
    task_set = MyTaskSet
    min_wait = 5000
    max_wait = 15000
 
