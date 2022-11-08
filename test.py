import laspy
import numpy as np


def func_timer(function):
    import time

    def timer(*args, **kwargs):
        start_time = time.time()
        function(*args)
        end_time = time.time()
        print(f"Done in: {end_time-start_time}")

    return timer


@func_timer
def read_las():
    las_file = laspy.read("data/high_density.las")

    all_points = np.dstack(
        [
            las_file.x,
            las_file.y,
            las_file.z,
        ]
    )


read_las()
