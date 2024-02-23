"""
Basic tests for loading a catalogue.
"""

from velociraptor import load
from .helper import requires


@requires("cosmo_0000.properties")
def test_basic_load_catalogue_no_crash(filename="test_data/cosmo_0000.properties",):
    catalogue = load(filename)

    return


if __name__ == "__main__":
    # Run all tests.

    test_basic_load_catalogue_no_crash()
