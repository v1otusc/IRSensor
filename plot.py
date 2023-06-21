#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
from mpl_interactions import hyperslicer
import matplotlib.pyplot as plt
from matplotlib.transforms import Affine2D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from mpl_toolkits.mplot3d import Axes3D


def calculate_distance_xy(p1, p2):
    """
    calculate distance between two points in xy plane
    """
    x1, y1 = p1
    x2, y2 = p2
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)

def calculate_distance(p1, p2):
    """
    calculate distance between two points in 3D space
    """
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    return np.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)

def read_points_data(file_name):
    """
    read points data from file by frame
    """
    data = []
    frame_data = []
    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip()
            if line == "==========":
                if frame_data:
                    data.append(frame_data)
                    frame_data = []
            else:
                x, y, z = line.split(',')
                frame_data.append((float(x), float(y), float(z)))

    if frame_data:
        data.append(frame_data)

    return data

def plot_points(data):
    """
    main func to plot points
    """
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.grid(False)

    frame_index = 0
    total_frame = len(data)

    # keep the view consistency
    current_scale = 1.0
    current_elev = ax.elev
    current_azim = ax.azim

    # whether to draw the bounding box
    draw_bbox = True

    # mesured points
    selected_points = []

    # can select points
    can_select = False

    # drag start and end -- to keep the view consistency
    drag_start = []
    drag_end = []

    def get_bbox(frame_data):
        """
        get bounding box of frame data
        """
        xs = [p[0] for p in frame_data]
        ys = [p[1] for p in frame_data]
        zs = [p[2] for p in frame_data]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        zmin, zmax = min(zs), max(zs)
        return xmin, xmax, ymin, ymax, zmin, zmax

    def plot_next_frame():
        """
        plot next frame
        """
        nonlocal frame_index
        if frame_index + 1 < total_frame:
            frame_index += 1
            plot_current_frame()
    
    def plot_prev_frame():
        """
        plot prev frame
        """
        nonlocal frame_index
        if frame_index > 0:
            frame_index -= 1
            plot_current_frame()
    
    def plot_current_frame():
        """
        plot current frame
        """
        nonlocal frame_index
        nonlocal current_scale
        nonlocal selected_points
        nonlocal drag_start, drag_end

        frame_data = data[frame_index]
        xs = [p[0] for p in frame_data]
        ys = [p[1] for p in frame_data]
        zs = [p[2] for p in frame_data]
        ax.clear()
        ax.grid(False)
        ax.axis('off')

        ax.scatter(xs, ys, zs, s=1)

        origin = [0, 0, 0]
        ax.plot([origin[0], 0.1], [origin[1], 0], [origin[2], 0], color='r')
        ax.plot([origin[0], 0], [origin[1], 0.1], [origin[2], 0], color='g')
        ax.plot([origin[0], 0], [origin[1], 0], [origin[2], 0.1], color='b')

        selected_points = []

        # curren limit
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        zlim = ax.get_zlim()

        ax.view_init(elev=current_elev, azim=current_azim)

        # Add text labels
        ax.text2D(0.75, 0.95, f'xmax: {max(xs):.5f}', transform=ax.transAxes, ha='center', va='center', fontsize=10)
        ax.text2D(0.75, 0.93, f'xmin: {min(xs):.5f}', transform=ax.transAxes, ha='center', va='center', fontsize=10)
        ax.text2D(0.75, 0.91, f'ymax: {max(ys):.5f}', transform=ax.transAxes, ha='center', va='center', fontsize=10)
        ax.text2D(0.75, 0.89, f'ymin: {min(ys):.5f}', transform=ax.transAxes, ha='center', va='center', fontsize=10)
        ax.text2D(0.75, 0.87, f'zmax: {max(zs):.5f}', transform=ax.transAxes, ha='center', va='center', fontsize=10)
        ax.text2D(0.75, 0.85, f'zmin: {min(zs):.5f}', transform=ax.transAxes, ha='center', va='center', fontsize=10)
        ax.text2D(0.75, 0.83, f'frame: {frame_index}', transform=ax.transAxes, ha='center', va='center', fontsize=10)

        # update drag move
        if drag_start and drag_end:
            dx = drag_end[0] - drag_start[0]
            dy = drag_end[1] - drag_start[1]
            # trans = ax.transData + Affine2D().translate(dx, dy)
            # ax.transData = trans
            # print(f'dx: {dx}, dy: {dy}')
        else:
            dx = 0
            dy = 0

        # update scale
        ax.set_xlim(xlim[0] * current_scale, xlim[1] * current_scale)
        ax.set_ylim(ylim[0] * current_scale, ylim[1] * current_scale)
        ax.set_zlim(zlim[0] * current_scale, zlim[1] * current_scale)

        plt.draw()


    def plot_bounding_box():
        # get the data of current frame
        frame_data = data[frame_index]

        xs = [p[0] for p in frame_data]
        ys = [p[1] for p in frame_data]
        zs = [p[2] for p in frame_data]

        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        z_min, z_max = min(zs), max(zs)

        vertices = [
            (x_min, y_min, z_min),
            (x_min, y_max, z_min),
            (x_max, y_max, z_min),
            (x_max, y_min, z_min),
            (x_min, y_min, z_max),
            (x_min, y_max, z_max),
            (x_max, y_max, z_max),
            (x_max, y_min, z_max)
        ]

        edges = [
            [vertices[0], vertices[1]],
            [vertices[1], vertices[2]],
            [vertices[2], vertices[3]],
            [vertices[3], vertices[0]],
            [vertices[0], vertices[4]],
            [vertices[1], vertices[5]],
            [vertices[2], vertices[6]],
            [vertices[3], vertices[7]],
            [vertices[4], vertices[5]],
            [vertices[5], vertices[6]],
            [vertices[6], vertices[7]],
            [vertices[7], vertices[4]]
        ]

        ax.add_collection3d(Line3DCollection(edges, colors='k', linewidths=0.5))

        plt.draw()

    def on_scroll(event):
        """
        on_scroll
        """
        axtemp = event.inaxes
        xlim = axtemp.get_xlim()
        ylim = axtemp.get_ylim()
        zlim = axtemp.get_zlim()

        scale = 1.1 if event.button == 'down' else 1 / 1.1
        nonlocal current_scale
        current_scale *= scale
        axtemp.set_xlim(xlim[0] * scale, xlim[1] * scale)
        axtemp.set_ylim(ylim[0] * scale, ylim[1] * scale)
        axtemp.set_zlim(zlim[0] * scale, zlim[1] * scale)
        fig.canvas.draw()

    def on_key(event):
        """
        space to plot next frame
        """
        nonlocal current_elev, current_azim
        nonlocal draw_bbox
        nonlocal can_select
        if event.key == ' ':
            current_elev = ax.elev
            current_azim = ax.azim
            plot_next_frame()
            if draw_bbox:
                plot_bounding_box()
        elif event.key == "2":
            current_elev = ax.elev
            current_azim = ax.azim
            current_transData = ax.transData
            plot_prev_frame()
            if draw_bbox:
                plot_bounding_box()
        elif event.key == "b":
            draw_bbox = not draw_bbox
        elif event.key == "w":
            # write figure to file
            # plt.savefig(f"frame_{frame_index-1}.png")
            pass
        elif event.key == "p":
            can_select = not can_select 
        elif event.key == "q":
            plt.close()
        elif event.key == '1':
            # clear selected points
            current_elev = ax.elev
            current_azim = ax.azim
            current_transData = ax.transData
            plot_current_frame()
            if draw_bbox:
                plot_bounding_box()
            
    def on_click(event):
        """
        click and measure distance
        NOTE: not that accurate because of the attempt guess of ax.format_coord
        """
        if can_select:
            if event.inaxes is None:
                return
            
            nonlocal selected_points
            if event.button == 1:
                x, y = event.xdata, event.ydata
                # HACK
                # we can get the x, y, z format or we can only get the angular coordinates
                # https://stackoverflow.com/questions/50283031/matplotlib-ax-format-coord-in-3d-trisurf-plot-return-x-y-z-instead-of-az
                b = ax.button_pressed
                ax.button_pressed = -1
                coords = ax.format_coord(x, y)
                ax.button_pressed = b

                coords = coords.replace('x=', '').replace('y=', '').replace('z=', '').replace('−', '-')
                coords = coords.split(',')
                x_data, y_data, z_data = [coord.strip() for coord in coords]
                print(f"Clicked point: ({x_data}, {y_data}, {z_data})")

                # nearest point
                distances = []
                for point in data[frame_index]:
                    if point in selected_points:
                        distances.append(100000000)
                    distances.append(calculate_distance((float(x_data), float(y_data), float(z_data)), point))
            
                index = distances.index(min(distances))
                nearest_point = data[frame_index][index]
                print(f"Data point: ({nearest_point[0]:.5f}, {nearest_point[1]:.5f}, {nearest_point[2]:.5f})")
                selected_points.append(nearest_point)
        
            if len(selected_points) > 2:
                plot_current_frame()
                plot_bounding_box()
                selected_points = []
            
            # plot selected points
            if len(selected_points) == 1:
                ax.scatter(*selected_points[0], c='r', s=20)
            elif len(selected_points) == 2:
                ax.scatter(*selected_points[1], c='r', s=20)
                ax.plot(*zip(*selected_points), c='r', linewidth=1)
                distance = calculate_distance(*selected_points)
                print(f"Distance: {distance:.5f}")
            plt.draw()

    def middle_button_press(event):
        """
        middle button press
        """
        if event.button == 2:
            nonlocal drag_start
            drag_start = (event.xdata, event.ydata)
    
    def middle_button_release(event):
        """
        middle button release
        """
        if event.button == 2 and drag_start is not None:
            nonlocal drag_end
            drag_end = (event.xdata, event.ydata)
            dx = drag_end[0] - drag_start[0]
            dy = drag_end[1] - drag_start[1]

            axtemp = event.inaxes
            trans = axtemp.transData + Affine2D().translate(dx, dy)
            axtemp.transData = trans
            fig.canvas.draw()

            
    fig.canvas.mpl_connect('scroll_event', on_scroll)
    fig.canvas.mpl_connect('key_press_event', on_key)
    fig.canvas.mpl_connect('button_press_event', on_click)
    fig.canvas.mpl_connect('button_press_event', middle_button_press)
    fig.canvas.mpl_connect('button_release_event', middle_button_release)

    plot_current_frame()
    if draw_bbox:
        plot_bounding_box()
    plt.show()


if __name__ == '__main__':
    file_name = "ld_line.csv"
    if len(sys.argv) > 1:
        file_name = sys.argv[1]

    data = read_points_data(file_name)
    plot_points(data)
