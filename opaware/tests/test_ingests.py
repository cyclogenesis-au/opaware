import os
import opaware
import numpy as np

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')


def test_ambient_ingest():
    with open(os.path.join(DATA_PATH, 'test_data.json')) as textfile:
        data = textfile.readlines()

    test_data = opaware.ingests.ingest_ambient(data)
    np.testing.assert_allclose(test_data.outside_dewpoint.values[0], 0.02415593,
                               rtol=1e-7)