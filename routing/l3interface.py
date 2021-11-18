from l3addr import L3Addr
from utils import maskToHostMask, maskToInt
from icecream import ic


class L3Interface:

    def __init__(self, number: int, addr: str, mask_numbits: int):
        self._number = number
        self._mask = maskToInt(mask_numbits)
        ic(self._mask)
        self._mask_numbits = mask_numbits
        self._addr = L3Addr(addr)

    def get_number(self) -> int:
        return self._number

    def get_netaddr(self) -> L3Addr:
        return L3Addr(self._mask & self.get_addr().as_int())

    def get_directed_bcast_addr(self) -> L3Addr:
        host_mask = maskToHostMask(self._mask_numbits)
        # host_mask is all 1 bits in the host part -- which is the same as a bcast value!
        host_bcast = host_mask | self.get_netaddr().as_int()
        return L3Addr(host_bcast)

    def get_mask(self):
        return self._mask_numbits

    def get_mask_as_int(self):
        return self._mask

    def on_same_network(self, addr: L3Addr) -> bool:
        '''return True if the given addr is on this interface's network.'''
        return self.get_netaddr().as_int() == (maskToInt(self.get_mask()) & addr.as_int())

    def get_addr(self):
        return self._addr

    def __str__(self):
        return f"Iface<{self._number}: {self._addr.as_str()}/{self._mask_numbits}>"


if __name__ == "__main__":
    iface = L3Interface(1, "10.10.10.2", 8)
    assert iface.get_mask_as_int() == 4278190080
    iface = L3Interface(1, "10.10.10.2", 16)
    assert iface.get_mask_as_int() == 4294901760
    iface = L3Interface(1, "10.10.10.2", 5)
    assert iface.get_mask_as_int() == 4160749568
    iface = L3Interface(1, "10.10.10.2", 11)
    assert iface.get_mask_as_int() == 4292870144
    iface = L3Interface(1, "10.10.10.2", 28)
    assert iface.get_mask_as_int() == 4294967280
    iface = L3Interface(1, "10.10.10.2", 23)
    assert iface.get_mask_as_int() == 4294966784

    assert iface.on_same_network(L3Addr("10.10.11.3"))
    assert not iface.on_same_network(L3Addr("10.10.12.74"))

    assert iface.get_directed_bcast_addr().as_str() == "10.10.11.255"
    assert iface.get_netaddr().as_str() == "10.10.10.0"

    assert str(iface) == "Iface<1: 10.10.10.2/23>"

    print("All tests passed!")
