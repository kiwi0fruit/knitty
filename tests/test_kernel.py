import knitty.stitch.stitch as R
import pytest


@pytest.fixture(scope='module')
def global_python_kernel():
    """
    A python kernel anyone can use.
    """
    return R.kernel_factory('python')


@pytest.fixture(scope='function')
def clean_python_kernel(global_python_kernel):
    """
    Takes ``global_python_kernel`` and resets all variables,
    returning the clean kernel.
    """
    R.run_code('%reset -f', global_python_kernel)
    return global_python_kernel


class TestKernel:

    def test_init_python_pre(self):
        kp = R.kernel_factory('python')
        result = R.run_code(
            'import pandas; assert pandas.options.display.latex.repr is False',
            kp)
        assert len(result) == 1

    def test_init_python_latex(self, clean_python_kernel):
        R.initialize_kernel('python', clean_python_kernel)
        result = R.run_code(
            'assert pandas.options.display.latex.repr is False',
            clean_python_kernel
        )
        assert len(result) == 2
