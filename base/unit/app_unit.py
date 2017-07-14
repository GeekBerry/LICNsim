from common import Unit
from base.unit.face_unit import FaceBase


class AppUnitBase(Unit):
    def __init__(self):
        self.app_face= None

    def install(self, announces, api):
        super().install(announces, api)
        api['APP.ask']= self.ask
        api['APP.store']= self.store
        api['APP.respond']= self.respond

        self.app_face= api['Face.access']('APP', FaceBase)  # 其中执行 face.download= Bind(FaceUnit.receive, 'APP')
        self.app_face.upload= api['APP.respond']

    def ask(self, packet):  # APP -> interest
        self.app_face.download(packet)
        self.announces['ask'](packet)

    def store(self, packet):  # APP -> data
        self.app_face.download(packet)
        self.announces['store'](packet)

    def respond(self, packet):  # APP <- data, interest
        self.announces['respond'](packet)
