from bearlibterminal import terminal as blt
class EventHandler:
    def __init__(self,ck_dict):
        self.ck_dict = ck_dict

    @property
    def event(self):
        if blt.has_input():
            key = blt.read()
            #print(key)
            if key in self.ck_dict:
                #print("what?")
                _event = self.ck_dict[key]
                return _event
        else:
            return None
    def register_event(self,ck_dict,key,event_type):
        ck_dict[key] = event_type
