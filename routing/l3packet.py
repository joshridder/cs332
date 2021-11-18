from l3addr import L3Addr


class L3Packet:

    def __init__(self, dest: L3Addr, src: L3Addr, ttl: int):
        self.dest = dest
        self.src = src
        self.ttl = ttl

    def __str__(self):
        return f"Packet<dst: {self.dest.as_str()} src: {self.src.as_str()} ttl: {self.ttl}>"
