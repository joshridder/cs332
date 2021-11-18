from l3addr import L3Addr
from icecream import ic

ic.disable()


class RoutingTableEntry:
    def __init__(self, iface_num: int, destaddr: L3Addr, mask_numbits: int, nexthop: L3Addr, is_local: bool):
        self.iface_num = iface_num
        self.destaddr = destaddr
        self.mask_numbits = mask_numbits
        self.is_local = is_local
        # if is_local is true, then nexthop value does not matter
        self.nexthop = nexthop


class RoutingTable:

    def __init__(self):
        self._entries = []

    def add_iface_route(self, iface_num: int, netaddr: L3Addr, mask_numbits: int, nexthop: L3Addr):
        '''Add a route out the given interface.
        Indicate a local route (no nexthop) by passing L3Addr("0.0.0.0") for nexthop'''

        is_local = nexthop.as_str() == "0.0.0.0"

        # Make sure the netaddr passed in is actually a network address -- host part
        # is all 0s.
        if netaddr.host_part_as_L3Addr(mask_numbits).as_int() != 0:
            netaddr = netaddr.network_part_as_L3Addr(mask_numbits)
        
        # Create a RoutingTableEntry and append to self._entries.
        self._entries.append(RoutingTableEntry(iface_num, netaddr, mask_numbits, nexthop, is_local))

    def add_route(self, ifaces: list, netaddr: L3Addr, mask_numbits: int, nexthop: L3Addr):
        '''Add a route. Indicate a local route (no nexthop) by passing L3Addr("0.0.0.0") for nexthop'''

        is_local = nexthop.as_str() == "0.0.0.0"

        # TODO: find the iface the nexthop address is accessible through.  raise ValueError if it
        # is not accessible out any interface. Store iface in out_iface.

        ic(str(out_iface))
        # Make sure the destaddr passed in is actually a network address -- host part
        # is all 0s.
        # TODO: implement, just as you did in previous method.

        # TODO: Create routing table entry and add to list, similar to previous method.

    def __str__(self):
        ret = f"RoutingTable:\n"
        ret += f"netaddr   mask  nexthop   if\n"
        for e in self._entries:
            ret += f"{e.destaddr.as_str()}  {e.mask_numbits}    "
            ret += "local" if e.is_local else e.nexthop.as_str()
            ret += f"   {e.iface_num}"
            ret += "\n"
        return ret

    def get_best_route(self, dest: L3Addr) -> RoutingTableEntry:  # or None
        '''Use longest-prefix-match (LPM) to find and return the best route
        entry for the given dest address'''
        # TODO: return None if no matches (which means no default route)
        match = None
        longest_match = -1
        for entry in self._entries:
            dest_network_part = dest.network_part_as_L3Addr(entry.mask_numbits)
            #anded_result = format( & dest_network_part.as_int(), '032b')
            if entry.destaddr == dest_network_part and entry.mask_numbits > longest_match:
                match = entry
                longest_match = entry.mask_numbits

        return match


if __name__ == "__main__":
    r = RoutingTable()
    # This next route implies there is a 20.0.0.0 network attached.
    r.add_iface_route(1, L3Addr("30.0.0.0"), 8, L3Addr("20.0.0.2"))

    # Note: the following 2nd arg is not an actual *network* address,
    # so the add function should fix it automatically.
    # And the route is for a locally-attached network
    r.add_iface_route(2, L3Addr("10.0.0.1"), 24, L3Addr("0.0.0.0"))

    r.add_iface_route(3, L3Addr("10.1.2.3"), 8, L3Addr("10.0.78.89"))

    # default route
    r.add_iface_route(1, L3Addr("0.0.0.0"), 0, L3Addr("20.0.0.2"))

    print("Routing table looks like:\n", r)

    assert r.get_best_route(L3Addr("30.1.2.3")).iface_num == 1
    # Matches 2 routes, so should pick interface 2
    assert r.get_best_route(L3Addr("10.0.0.3")).iface_num == 2
    # Matches one route, with shorter prefix
    assert r.get_best_route(L3Addr("10.1.0.3")).iface_num == 3
    assert r.get_best_route(L3Addr("10.1.2.3")).iface_num == 3
    # default route
    assert r.get_best_route(L3Addr("192.168.2.1")).iface_num == 1

    print("Routing: all tests passed!")
