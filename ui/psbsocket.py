import socket
import json
import time


class PSBSocket():
    TCP_CONNECTION = ("127.0.0.1", 8181)
    #TCP_CONNECTION = ("10.209.75.207", 8181)
    RECIEVE_SIZE = 4096 * 16
    sequence = 0
    recv_list = {}

    def __init__(self):
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

    def get_data_range(self, ids, start, end):
        return self.send_message("get_data_range", {
            "ids": ids,
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

        seq = self.sequence
        self.sequence += 1

        msg_enc = str.encode(json.dumps(msg))
        print(msg_enc)
        sent = self.sock.send(msg_enc)

        if sent == 0:
            raise RuntimeError("socket connection broken")

        attempts = 0

        data = self.sock.recv(self.RECIEVE_SIZE)
        data_dict = json.loads(data)

        self.recv_list[data_dict["seq"]] = data_dict

        # Since multiple threads are sending messages in a single socket,
        # we may recieve data that was meant for a different thread.
        # Thus, we instead check to see if we received our data, before
        # returning the data we want back to the specific thread.
        while True:
            if seq in self.recv_list:
                recv = self.recv_list.pop(seq)
                print(recv)
                return recv["resp"]

            if attempts == 10:
                break

            attempts += 1
            time.sleep(0.2)

        print("Attempts surpassed for " + str(seq) + ", returning empty object.")
        return {}
