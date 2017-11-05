import socket
import json
import time


class PSBSocket():
    TCP_CONNECTION = ("127.0.0.1", 8181)
    RECIEVE_SIZE = 1024
    sequence = 250

    def __init__(self):
        if not self.testing:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(self.TCP_CONNECTION)

    def get_psb_version(self):
        return self.send_message("version")

    def get_topology(self):
        return self.send_message("get_all_nodes")

    def get_devices(self):
        return self.send_message("get_all_devices")

    def get_drivers(self):
        return self.send_message("get_all_drivers")

    def get_data_range(self, device_ids, start, end):
        return self.send_message("get_data_range", {
            "ids": device_ids,
            "start": start,
            "end": end,
        })

    def get_current_data(self, device_id):
        cur_time = time.time() * 1000
        points = self.get_data_range([device_id], cur_time - 1000, cur_time)

        point = points["resp"]["0"]

        # In case of no points were created
        if len(point):
            point = point[-1]

        return {"seq": points["seq"], "resp": point}

    def add_device(self, args):
        return self.send_message("create_device", args)

    def send_message(self, func, args={}):
        msg = {
            "seq": self.sequence,
            "func": func,
        }

        if args:
            msg["args"] = args

        self.sequence += 1

        print(str.encode(json.dumps(msg)))
        sent = self.sock.send(str.encode(json.dumps(msg)))

        if sent == 0:
            raise RuntimeError("socket connection broken")

        data = self.sock.recv(self.RECIEVE_SIZE)
        print(data)

        return json.loads(data)["resp"]
