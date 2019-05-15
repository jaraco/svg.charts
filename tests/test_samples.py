import pytest

import samples


@pytest.mark.parametrize(
    'sample', [chart for name, chart in samples.generate_samples()]
)
def test_sample(sample):
    sample.burn()
