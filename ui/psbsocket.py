import socket
import json
import time


class PSBSocket():
    TCP_CONNECTION = ("127.0.0.1", 8181)
    RECIEVE_SIZE = 1024 * 32
    sequence = 0
    recv_list = {}
    retrying = False

    def __init__(self):
        self.retry_connection()

    def retry_connection(self):
        # Account for multiple threads, let a single thread handle
        # retrying and wait until we are connected before we return
        if (self.retrying):
            print("Thread already retrying, waiting...")

            while (self.retrying):
                time.sleep(5)

            return

        self.retrying = True

        while self.retrying:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect(self.TCP_CONNECTION)
                self.retrying = False
            except socket.error:
                print("Error connecting to socket. Retrying...")
                time.sleep(5)

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
        print("request for " + str(seq) + ":")
        print(msg_enc)

        send_attempts = 0

        while True:
            try:
                sent = self.sock.send(msg_enc)
            except socket.error:
                self.retry_connection()
                sent = self.sock.send(msg_enc)

            if sent == 0:
                self.retry_connection()
                sent = self.sock.send(msg_enc)

            attempts = 0

            try:
                raw_data = self.sock.recv(self.RECIEVE_SIZE)
            except socket.error:
                self.retry_connection()
                raw_data = self.sock.recv(self.RECIEVE_SIZE)

            # if the data is returned too quickly (containing two or more \r\n)
            data_list = raw_data.split(b"\r\n")[0:-1]

            for data in data_list:
                try:
                    data_dict = json.loads(data)
                    self.recv_list[data_dict["seq"]] = data_dict
                except json.decoder.JSONDecodeError:
                    print(data)
                    print("Error decoding json! PSB Server error?")

            # Since multiple threads are sending messages in a single socket,
            # we may recieve data that was meant for a different thread.
            # Thus, we instead check to see if we received our data, before
            # returning the data we want back to the specific thread.
            while True:
                if seq in self.recv_list:
                    recv = self.recv_list.pop(seq)
                    print("response for " + str(seq) + ":")
                    print(recv)
                    return recv["resp"]

                if attempts == 10:
                    break

                attempts += 1
                time.sleep(0.2)

            if send_attempts == 5:
                break

            print("Attempting to send " + str(seq) + " again.")
            send_attempts += 1

        print("Attempts surpassed for " + str(seq) + ", returning empty object.")
        return {}
