from os.path import basename

import gpxpy
import laspy
import argparse

import numpy as np
import open3d as o3d

from pyproj import Transformer

parser = argparse.ArgumentParser()
parser.add_argument(
    "-g", "--path_gpx", type=str, help="Path to .gpx file", required=True
)
parser.add_argument(
    "-l", "--path_las", type=str, help="Path to .las file", default=None
)
parser.add_argument(
    "-c", "--color", type=str, help="Color of the gpx track", default="255 0 0"
)
parser.add_argument("-t", "--top", type=int, help="Value to increase Z", default=0)
args = parser.parse_args()


file_name_no_ext = basename(args.path_gpx).replace(
    "." + args.path_gpx.split(".")[-1], ""
)

all_points = []
all_points_colors = []

# Convert las to xyzrgb format
if args.path_las:
    las_file = laspy.read(args.path_las)

    all_points = np.dstack(
        [
            las_file.x,
            las_file.y,
            las_file.z,
        ]
    )
    all_points_colors = np.dstack(
        [
            las_file.red / 65280,
            las_file.green / 65280,
            las_file.blue / 65280,
        ]
    )

# Reading gpx data
gpx_file = open(args.path_gpx, "r")
gpx = gpxpy.parse(gpx_file)
gpx_color = [int(c) for c in args.color.split(" ")]

points_gpx = [[]]
points_colors_gpx = [[]]
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            transformer = Transformer.from_crs("EPSG:4326", "EPSG:2180")
            y, x, z = transformer.transform(
                point.latitude, point.longitude, point.elevation
            )
            points_gpx[0].append([x, y, z + args.top])
            points_colors_gpx[0].append(
                [gpx_color[0] / 255, gpx_color[1] / 255, gpx_color[2] / 255]
            )

if args.path_las:
    all_points = np.column_stack((all_points, points_gpx))
    all_points_colors = np.column_stack((all_points_colors, points_colors_gpx))
else:
    all_points = points_gpx
    all_points_colors = points_colors_gpx

# Visualization
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(all_points[0])
pcd.colors = o3d.utility.Vector3dVector(all_points_colors[0])
o3d.visualization.draw_geometries([pcd])
