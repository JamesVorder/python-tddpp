import pytest
import generated.test_class


@pytest.mark.parametrize("num1, num2, expected1, expected2", [
    (5, 3, 4, 2),
    (-1, 1, -2, 0),
    (0, 0, -1, -1),
    (-10, 5, -11, 4)
])
def test_init(num1, num2, expected1, expected2):
    # Let's make a test with a tricky expectation.
    # When we initialize TestClass, we should subtract 1 from x and y.
    instance = generated.test_class.ExampleClass(num1, num2)
    assert instance.x == expected1
    assert instance.y == expected2
