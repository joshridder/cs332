from l3packet import L3Packet
from l3addr import L3Addr
from routing_table import RoutingTable
from l3interface import L3Interface


class Router:
    def __init__(self):
        self._ifaces = []
        self._routing_table = RoutingTable()

    def add_interface(self, iface: L3Interface):
        self._ifaces.append(iface)
        self._routing_table.add_iface_route(iface.get_number(), iface.get_netaddr(), iface.get_mask(), L3Addr("0.0.0.0"))

    def route_packet(self, pkt: L3Packet, incoming_iface: L3Interface) -> int:
        '''Route the given packet that arrived on the given interface (iface == None
        if the packet originated on this device). Return the interface # it was sent out,
        or None, if dropped or accepted to be processed on this host.'''

        # Check the following and drop pkt if any are true:
        #   bcast packets (directed bcasts handled later)
        #   dest on same network as packet arrived on: drop
        if pkt.dest.is_bcast():
            print(f"{pkt} dropped because dest is bcast.")
            return None
            
        if incoming_iface.on_same_network(pkt.dest):
            print(f"{pkt} dropped because dest on same network as packet arrived on.")
            return None

        # drops packet if it's a directed bcast, accepts it if the packet's dest is on interface's network
        for interface in self._ifaces:

            # drops packet if it is a directed bcast packet
            if pkt.dest == interface.get_directed_bcast_addr():
                print(f"{pkt} dropped because dest is directed bcast.")
                return None

            # If dest addr is one of the interfaces, accept and do not forward.
            if interface.get_addr() == pkt.dest:
                return None

        # Decrement ttl and if 0, drop.
        pkt.ttl -= 1
        if pkt.ttl == 0:
            return None

        # Get best route entry. Return the interface number of best match.
        entry = self._routing_table.get_best_route(pkt.dest)

        # NOTE: print out what the algorithm is doing just before each return statement.
        # e.g., print(f"{pkt} accepted because dest matches iface {iface.get_number()}")
        print(f'{pkt} routed to interface {entry.iface_num}')

        return entry.iface_num

    def set_default_route(self, nexthop: str):
        self._routing_table.add_route(
            self._ifaces, L3Addr("0.0.0.0"), 0, L3Addr(nexthop))

    def add_route(self, netaddr: str, mask: int, nexthop: str):
        self._routing_table.add_route(
            self._ifaces, L3Addr(netaddr), mask, L3Addr(nexthop))

    def print_routing_table(self):
        print(self._routing_table)


if __name__ == "__main__":

    r = Router()
    i1 = L3Interface(1, "10.10.10.2", 8)
    r.add_interface(i1)
    i2 = L3Interface(2, "20.0.0.1", 8)
    r.add_interface(i2)
    i3 = L3Interface(3, "44.55.66.77", 24)
    r.add_interface(i3)
    r.print_routing_table()

    # 16 is the ttl value
    pkt1 = L3Packet(L3Addr("255.255.255.255"), L3Addr("20.1.2.3"), ttl=16)
    assert r.route_packet(pkt1, i1) == None
    pkt2 = L3Packet(L3Addr("1.2.3.4"), L3Addr("20.1.2.3"), 1)
    assert r.route_packet(pkt2, i2) == None
    # Should be dropped because it dest is on the network that pkt arrived on
    pkt5 = L3Packet(L3Addr("10.0.1.2"), L3Addr("10.0.2.3"), 16)
    assert r.route_packet(pkt5, i1) == None

    pkt3 = L3Packet(L3Addr("10.0.1.2"), L3Addr("20.0.1.2"), 16)
    assert r.route_packet(pkt3, i2) == 1   # routed out interface 1
    pkt4 = L3Packet(L3Addr("20.0.1.2"), L3Addr("10.0.1.2"), 16)
    assert r.route_packet(pkt4, i1) == 2   # routed out interface 2

    # Accept packet because destination is one of the interfaces.
    pkt6 = L3Packet(i1.get_addr(), L3Addr("44.44.44.44"), 16)
    assert r.route_packet(pkt6, i3) == None

    # Drop directed broadcast packet
    pkt7 = L3Packet(i3.get_directed_bcast_addr(), L3Addr("7.8.9.10"), 16)
    assert r.route_packet(pkt7, i1) == None

    # Set default route and route pkt8, which should use default route
    r.set_default_route("20.0.0.2")
    r.print_routing_table()
    pkt8 = L3Packet(L3Addr("4.5.6.7"), L3Addr("7.8.9.10"), 16)
    assert r.route_packet(pkt8, i3) == 2

    # Test add_route: network 40.0.0/24 is out past the 10 network.
    r.add_route("40.0.0.8", 24, "10.0.0.7")
    r.print_routing_table()
    pkt9 = L3Packet(L3Addr("40.0.0.75"), L3Addr("99.100.99.100"), 16)
    assert r.route_packet(pkt9, i2) == 1

    print("Router: all tests passed!")
