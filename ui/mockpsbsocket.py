"""
This class is meant to send mock data to the frontend while the PSB server is
under development.
"""
import time
import random


class MockPSBSocket():
    def get_psb_version(self):
        return {"version": "0.1.0"}

    def get_data_range(self, device_ids, start, end):
        return {
            "0": [
                {"time": start, "power": random.randrange(0, 500)},
                #{"time": (start + end) / 2, "power": random.randrange(0, 500)},
                #{"time": end, "power": random.randrange(0, 500)}
            ],
            #"1": [
                #{"time": start, "power": random.randrange(0, 500)},
                #{"time": (start + end) / 2, "power": random.randrange(0, 500)},
                #{"time": end - 0.1, "power": random.randrange(0, 500)}
            #]
        }

    def get_current_data(self, device_id):
        cur_time = time.time() * 1000
        points = self.get_data_range([device_id], cur_time - 1000, cur_time)
        return points[device_id][-1]

    def get_topology(self):
        cur_time = time.time() * 1000
        return {
            "0": {
                "node_id": 0,
                "parent_id": 0,
                "description": "node 0",
                "time_added": cur_time - 100000,
                "time_removed": cur_time
            },
            "1": {
                "node_id": 1,
                "parent_id": 0,
                "description": "node 1",
                "time_added": cur_time - 100000,
                "time_removed": cur_time
            },
            "2": {
                "node_id": 2,
                "parent_id": 0,
                "description": "node 2",
                "time_added": cur_time - 100000,
                "time_removed": cur_time,
            },
            "3": {
                "node_id": 3,
                "parent_id": 2,
                "description": "node 3",
                "time_added": cur_time - 100000,
                "time_removed": cur_time,
            },
            "4": {
                "node_id": 4,
                "parent_id": 3,
                "description": "node 4",
                "time_added": cur_time - 100000,
                "time_removed": cur_time,
            }
        }

    def get_devices(self):
        return {
            "3": {
                "driver_id": 3,
                "device_id": 3,
                "description": "device 3",
                "node_id": 3,
                "calibration": 5.44,
                "address": "192.168.0.2:8081",
                "state": 1
            },
            "6": {
                "driver_id": 3,
                "device_id": 6,
                "description": "device 6",
                "node_id": -1,
                "calibration": 5.44,
                "address": "192.168.0.3:8081",
                "state": 0
            }
        }

    def get_drivers(self):
        return {
            "0": {
                "name": "faux-driver",
                "driver_id": 0,
                "user_description": "i loaded this cause yea",
                "driver_description": "this module does xyz",
            },
            "1": {
                "name": "real-fake-driver",
                "driver_id": 1,
                "user_description": "i loaded this cause yea",
                "driver_description": "this module does xyz",
            },
        }

    def add_device(self, args):
        return {
            "status": "success",
            "device": {
                "driver_id": args["driver_id"],
                "device_id": 7,
                "description": args["description"],
                "node_id": args["node_id"],
                "calibration": 1,
                "address": args["address"],
                "state": 0
            }
        }
