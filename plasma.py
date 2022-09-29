import logging
import numpy as np
import win32api
from sdl2 import *
from sdl2 import sdlimage


def plane_plasma(pos, length=None, speed=None, phase=None, phase_multiplier=1, phase_start=0):
    return (1 + np.sin(length * np.dot(pos, speed) + phase * phase_multiplier + phase_start)) / 2


def radial_plasma(pos, length=None, center=None, phase=None, phase_multiplier=1):
    n, m, _ = pos.shape
    dist = (pos - center) ** 2
    dist = np.sqrt(np.array([(dist[:, i] ** 2).sum(axis=1) for i in range(m)])).T
    return (1 + np.sin(length * dist + phase * phase_multiplier)) / 2


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
    num_x = int(40 / scale)
    num_y = int(30 / scale)

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

    plasma_params = {'planar1': {'params': {'length': 1 / 50,
                                            'speed': np.array([1, 1])
                                            },
                                 'function': plane_plasma
                                 },
                     # 'radial1': {'params': {'length': 1 / 20,
                     #                        'center': np.array([320, 240]),
                     #                        'phase_multiplier': 5
                     #                        },
                     #             'function': radial_plasma
                     #             },
                     # 'radial2': {'params': {'length': 1 / 5,
                     #                        'center': np.array([160, 120]),
                     #                        'phase_multiplier': 7
                     #                        },
                     #             'function': radial_plasma
                     #             },
                     # 'radial3': {'params': {'length': 1 / 2,
                     #                        'center': np.array([480, 360]),
                     #                        'phase_multiplier': 2
                     #                        },
                     #             'function': radial_plasma
                     #             },
                     'planar2': {'params': {'length': 1 / 50,
                                            'speed': np.array([0, 1])
                                            },
                                 'function': plane_plasma
                                 },
                     'planar3': {'params': {'length': 1 / 50,
                                            'speed': np.array([1, 0])
                                            },
                                 'function': plane_plasma
                                 },
                     'planar4': {'params': {'length': 1 / 50,
                                            'speed': np.array([1, -1]),
                                            'phase_start': 1 / 50
                                            },
                                 'function': plane_plasma
                                 },
                     }
    time_shift = 0
    time_shift_default = 1 / 500

    zero_tile = [[0] * num_x for _ in range(num_y)]
    pos_vecs = np.array([np.array([[(i + 0.5) * grid_size, (j + 0.5) * grid_size] for i in range(num_x)])
                         for j in range(num_y)])

    max_iteration = 5 * 120 * scale * 10
    iteration = 0

    while iteration < max_iteration:
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
        print(iteration)
        iteration += 1

    SDL_DestroyRenderer(renderer)
    SDL_DestroyWindow(window)
    print('Done')
