from bearlibterminal import terminal as blt
class EventHandler:
    def __init__(self,ck_dict):
        self.ck_dict = ck_dict
    def get_event(self):
        if blt.has_input():
            key = blt.read()
            #print(key)
            if key in self.ck_dict:
                #print("what?")
                event = self.ck_dict[key]
                return event
        else:
            return None

ck_dict = {blt.TK_UP: "up",
           blt.TK_DOWN: "down",
           blt.TK_LEFT: "left",
           blt.TK_RIGHT: "right",
           blt.TK_SPACE: "action1",
           blt.TK_X: "action2",
           #blt.TK_CLOSE:"QUIT",
           blt.TK_Q: "QUIT"}