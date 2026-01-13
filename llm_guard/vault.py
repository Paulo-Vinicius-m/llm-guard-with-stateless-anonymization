import threading
from typing import List, Optional, Tuple


class Vault:
    """
    This class serves as a vault to store tuples. These tuples are typically placeholder values
    used for anonymization that need to be retained for later decoding.

    The vault provides methods to append single tuples, extend with a list of tuples, remove a tuple,
    and get the list of all stored tuples.
    """

    def __init__(self, tuples: Optional[List[Tuple]] = None):
        if tuples is None:
            tuples = []

        self._tuples = tuples
        self._lock = threading.Lock()

    def append(self, new_tuple: Tuple):
        with self._lock:
            self._tuples.append(new_tuple)

    def extend(self, new_tuples: List[Tuple]):
        with self._lock:
            self._tuples.extend(new_tuples)

    def remove(self, tuple_to_remove: Tuple):
        with self._lock:
            self._tuples.remove(tuple_to_remove)

    def get(self) -> List[Tuple[str, str]]:
        with self._lock:
            return self._tuples.copy()

    def clear(self):
        """Clear all stored tuples from the vault."""
        with self._lock:
            self._tuples.clear()

    def get_and_clear(self) -> List[Tuple[str, str]]:
        """
        Atomically get all vault data and clear it.
        
        This method is thread-safe and prevents race conditions when retrieving
        and clearing vault data in concurrent request scenarios.
        
        Returns:
            A copy of all stored tuples before clearing.
        """
        with self._lock:
            vault_data = self._tuples.copy()
            self._tuples.clear()
            return vault_data

    def placeholder_exists(self, placeholder: str) -> bool:
        with self._lock:
            for entity_placeholder, _ in self._tuples:
                if placeholder == entity_placeholder:
                    return True
            return False
