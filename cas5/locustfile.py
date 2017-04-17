#! /usr/bin/env python

from __future__ import print_function
import csv
import datetime
import os
import random
import re
from urlparse import urlparse, parse_qs
from locust import HttpLocust, TaskSet, task
from locust.exception import StopLocust

class CASTaskSet(TaskSet):
    execution_pat = re.compile(r'<input type="hidden" name="execution" value="([^"]+)"')
    eventid_pat = re.compile(r'<input type="hidden" name="_eventId" value="([^"]+)"')

    def on_start(self):
        """
        Start a new session.
        """
        self.initialize()

    def initialize(self):
        """
        Login, obtain a TGT.
        """
        print("Initializing locust ...")
        self.expiration = None
        client = self.client
        with client.get("/cas/login", catch_response=True) as response:
            if response.status_code == 404:
                response.success()
            content = response.content
        m = self.execution_pat.search(content)
        if m is None:
            return
        execution = m.groups()[0]
        m = self.eventid_pat.search(content)
        if m is None:
            return
        event_id = m.groups()[0]
        creds = random.choice(self.locust.creds)
        user = creds[0]
        passwd = creds[1]
        data = {
            "username": user,
            "password": passwd,
            "execution": execution,
            "_eventId": event_id,
            "geolocation": "",
        }
        response = client.post("/cas/login", data=data)
        lifetime_bins = []
        lifetime_bins.extend([600]*1)
        lifetime_bins.extend([3600]*2)
        lifetime_bins.extend([3600*8]*7)
        seconds = random.choice(lifetime_bins) 
        self.expiration = datetime.datetime.now() + datetime.timedelta(seconds=seconds)

    @task
    def authenticate_to_service(self):
        if self.expiration is None:
            self.initialize()
            return
        if datetime.datetime.now() >= self.expiration:
            self.logout()  
            self.initialize()
            return
        service = '''https://badges.stage.lafayette.edu/'''
        client = self.client
        with client.get("/cas/login", catch_response=True, params={'service': service}, allow_redirects=False) as response:
            if response.status_code in (301, 302):
                response.success()
                location = response.headers['Location']
            else:
                response.failure()
                return
        p = urlparse(location)
        q = p.query
        qs = parse_qs(q)
        ticket = qs['ticket'] 
        response = client.get("/cas/serviceValidate", params={'service': service, 'ticket': ticket})    

    def logout(self):
        """
        Logout.  This locust should die afterwards."
        """
        client = self.client()
        client.get("/cas/logout")


def load_creds():
    """
    Load test user credentials.
    """
    credpath = os.path.join(
        os.path.dirname(__file__),
        "credentials.csv")
    creds = []
    with open(credpath, "r") as f:
        reader = csv.reader(f)        
        for row in reader:
            creds.append((row[0], row[1]))
    print("Creds:\n{0}".format(creds))
    return creds


class CASLocust(HttpLocust):
    task_set = CASTaskSet
    host = 'https://cas.stage.lafayette.edu'
    min_wait = 5000
    max_wait = 15000
    creds = load_creds()























