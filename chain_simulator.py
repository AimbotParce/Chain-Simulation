from dataclasses import field
from typing import Tuple, List
import tkinter as tk
from numpy import array
from numpy.linalg import norm as distance
from time import time_ns
from copy import deepcopy


class Config:
    SCREEN_SIZE: Tuple[int, int] = (900, 700)
    BACKGROUND: str = "#191E29"
    POINT_SIZE: int = 16  # In pixels
    POINT_COLOR: str = "#FFFFFF"
    LOCKED_POINT_COLOR: str = "#E6394C"
    STICK_WIDTH: int = 10
    STICK_COLOR: int = "#292E39"
    GRAVITY_DIRECTION: array = array([0, 1])
    GRAVITY: float = 980
    STICK_ITERATIONS: int = 10


class Point:
    def __init__(self, position: Tuple[float, float], locked=False):
        self.position: array = array([float(position[0]), float(position[1])])
        self.locked: bool = locked
        self.prevPosition: array = array([float(position[0]), float(position[1])])
        self.body: tk.Canvas.create_oval = field(repr=False, init=False)


class Stick:
    def __init__(self, pointA: Point, pointB: Point, length: float):
        self.pointA: Point = pointA
        self.pointB: Point = pointB
        self.length: float = length
        self.body: tk.Canvas.create_line = field(repr=False, init=False)


class Screen:
    def __init__(self):
        self.points: List[Point] = []
        self.sticks: List[Stick] = []
        self.master = tk.Tk()
        self.canvas: tk.Canvas = self.init_canvas()

    def init_canvas(self) -> tk.Canvas:
        canvas = tk.Canvas(
            master=self.master,
            width=Config.SCREEN_SIZE[0],
            height=Config.SCREEN_SIZE[1],
            background=Config.BACKGROUND,
        )
        canvas.pack()
        canvas.bind("<ButtonPress-1>", self.click)
        canvas.bind("<ButtonRelease-1>", self.release)
        return canvas

    def create_point(self, x, y) -> None:
        self.points.append(Point(array((x, y))))

    def create_stick(self, pointA: Point, pointB: Point) -> None:
        self.sticks.append(
            Stick(
                pointA=pointA,
                pointB=pointB,
                length=distance(pointA.position - pointB.position),
            )
        )

    def click(self, event) -> None:
        position = array([event.x, event.y])
        for point in self.points:
            if distance(position - point.position) < Config.POINT_SIZE:
                self.tempPoint = point
                return

    def release(self, event) -> None:
        position = array([event.x, event.y])
        for point in self.points:
            if distance(position - point.position) < Config.POINT_SIZE:
                if point is self.tempPoint:
                    point.locked = not point.locked
                    self.draw_screen()
                    return
                self.create_stick(self.tempPoint, point)
                del self.tempPoint
                self.draw_screen()
                return
        self.create_point(event.x, event.y)
        self.draw_screen()

    def draw_points(self) -> None:
        for point in self.points:
            self.canvas.delete(point.body)
            point.body = self.canvas.create_oval(
                point.position[0] - Config.POINT_SIZE,
                point.position[1] - Config.POINT_SIZE,
                point.position[0] + Config.POINT_SIZE,
                point.position[1] + Config.POINT_SIZE,
                fill=Config.LOCKED_POINT_COLOR if point.locked else Config.POINT_COLOR,
                width=0,
            )

    def draw_sticks(self) -> None:
        for stick in self.sticks:
            self.canvas.delete(stick.body)
            stick.body = self.canvas.create_line(
                stick.pointA.position[0],
                stick.pointA.position[1],
                stick.pointB.position[0],
                stick.pointB.position[1],
                fill=Config.STICK_COLOR,
                width=Config.STICK_WIDTH,
            )

    def draw_screen(self) -> None:
        self.draw_sticks()
        self.draw_points()

    def simulate_frame(self, deltaTime: float) -> None:
        for point in self.points:
            if not point.locked:
                prevPosition = deepcopy(point.position)
                point.position += (
                    point.position
                    - point.prevPosition
                    + Config.GRAVITY_DIRECTION
                    * Config.GRAVITY
                    * deltaTime
                    * deltaTime
                    / 2
                )
                point.prevPosition = prevPosition
        for _ in range(Config.STICK_ITERATIONS):
            for stick in self.sticks:
                stickCenter = (stick.pointB.position + stick.pointA.position) / 2
                stickDirection = (
                    stick.pointA.position - stick.pointB.position
                ) / distance(stick.pointB.position - stick.pointA.position)
                if not stick.pointA.locked:
                    stick.pointA.position = (
                        stickCenter + stickDirection * stick.length / 2
                    )
                if not stick.pointB.locked:
                    stick.pointB.position = (
                        stickCenter - stickDirection * stick.length / 2
                    )
        self.draw_screen()

    def simulate_continuous(self):
        time = time_ns()
        while True:
            deltaTime_ns = time_ns() - time
            time = time_ns()
            self.simulate_frame(deltaTime_ns / 1e9)
            self.canvas.update()
            self.canvas.update_idletasks()


pantalla = Screen()
tk.Button(pantalla.master, text="Simulate", command=pantalla.simulate_continuous).pack()
pantalla.canvas.mainloop()
