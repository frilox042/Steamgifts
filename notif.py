import json
import requests
import os


class Notif():
    def __init__(self):
        f = self._open_or_create_json_file_notif()
        self.notif = json.load(f)
        f.close()

    def save(self):
        f = self._open_or_create_json_file_notif()
        json.dump(self.notif, f)
        f.close()

    def _open_or_create_json_file_notif(self):
        working_dir = os.getcwd()
        if not os.path.isfile(working_dir + '/notif.json'):
            f = open(working_dir + '/notif.json', "x+")
            json.dump({"created": 0, "won": 0, "message": 0}, f)
            f.close()
        f = open(working_dir + '/notif.json', "r+")
        return f

    def getCreated(self):
        return self.notif["created"]

    def getWon(self):
        return self.notif["won"]

    def getMessage(self):
        return self.notif["message"]

    def setCreated(self, n):
        self.notif["created"] = n
        self.save()

    def setWon(self, n):
        self.notif["won"] = n
        self.save()

    def setMessage(self, n):
        self.notif["message"] = n
        self.save()
