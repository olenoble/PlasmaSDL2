import logging
import numpy as np
import win32api
from sdl2 import *
from sdl2 import sdlimage
from time import time


def plane_plasma(pos, length=None, speed=None, phase=None, phase_multiplier=1, phase_start=0):
    return (1 + np.sin(length * np.dot(pos, speed) + phase * phase_multiplier + phase_start)) / 2


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)

    # device check
    device = win32api.EnumDisplayDevices()
    settings = win32api.EnumDisplaySettings(device.DeviceName, -1)
    vsync_freq = settings.DisplayFrequency
    logging.info('Screen refresh rate = %i' % round(vsync_freq))

    # set up the window
    grid_size = 16
    num_shades = 24

    scale = 1
    window_size = (800, 600)
    num_x = int(window_size[0] / grid_size / scale)
    num_y = int(window_size[1] / grid_size / scale)

    width = num_x * grid_size
    height = num_y * grid_size

    window = SDL_CreateWindow(str.encode('PLASMA'), SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
                              int(width * scale), int(height * scale), 0)
    # renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC)
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED)
    SDL_RenderSetScale(renderer, scale, scale)

    # load image of reference
    surf = sdlimage.IMG_Load(str.encode('./gradient2.png'))
    texture = SDL_CreateTextureFromSurface(renderer, surf)

    # pre-slice the image since it will be a lot fast
    tile_from = {}
    for i in range(num_shades):
        tile_from[i] = SDL_Rect(int(i) * grid_size, 0, grid_size, grid_size)

    # pre slice the output on the window as well
    tile_to = {}
    for j in range(num_y):
        for i in range(num_x):
            tile_to[j * num_x + i] = SDL_Rect(int(i) * grid_size, int(j) * grid_size, grid_size, grid_size)

    # plot everything
    SDL_RenderClear(renderer)

    lg_range = [1 / 500, 1 / 50]
    sp_range = [-1, 1]
    ps_range = [-1 / 50, 1 / 50]
    num_effect = 10
    plasma_params = {}
    for k in range(num_effect):
        plasma_params['planar' + str(k)] = {'params': {'length': np.random.uniform(lg_range[0], lg_range[1]),
                                                       'speed': np.array([np.random.uniform(sp_range[0], sp_range[1]),
                                                                          np.random.uniform(sp_range[0], sp_range[1])]),
                                                       'phase_start': np.random.uniform(ps_range[0],
                                                                                        ps_range[1]),
                                                       },
                                            'function': plane_plasma
                                            }

    time_shift = 0
    time_shift_default = 1 / 250

    zero_tile = [[0] * num_x for _ in range(num_y)]
    pos_vecs = np.array([np.array([[(i + 0.5) * grid_size, (j + 0.5) * grid_size] for i in range(num_x)])
                         for j in range(num_y)])

    import ctypes
    event_size = 10
    event_array = ctypes.cast((SDL_Event * event_size)(), POINTER(SDL_Event))
    stop_iteration = False
    iteration = 0
    time0 = time()

    while not stop_iteration:
        choices_defaults = np.array(zero_tile)
        num_effects = 0
        for _, v in plasma_params.items():
            num_effects += 1
            choices_defaults = choices_defaults + v['function'](pos_vecs, **v['params'], phase=time_shift)

        choices_defaults = choices_defaults * (num_shades - 1) / num_effects
        for j in range(num_y):
            for i in range(num_x):
                SDL_RenderCopy(renderer, texture, tile_from[int(choices_defaults[j][i])], tile_to[j * num_x + i])

        SDL_RenderPresent(renderer)
        time_shift += time_shift_default / scale

        SDL_PumpEvents()
        event_count = SDL_PeepEvents(event_array, event_size, SDL_GETEVENT, SDL_FIRSTEVENT, SDL_LASTEVENT)
        for k in range(event_count):
            event = event_array[k]
            stop_iteration = event.type == SDL_KEYUP
           
        iteration += 1

    SDL_DestroyRenderer(renderer)
    SDL_DestroyWindow(window)
    
    time1 = time()
    fps = iteration / (time1 - time0)
    print('FPS = %s' % fps)
    print('Done')
