# PlasmaSDL2
 
Simple code using python and SDL2 to generate a random plasma effect with a tileset (hence the blocky effect).
The code uses a randomly generated combination of 10 plane waves with randomly selected directions and frequencies. Users can increase the number of waves (as well as the range of parameters). It has little impact on performance but I found that 10 waves is a nice sweet spot. It gives cool effect with a reasonable amount of calculations. Code uses numpy for all vector calculations
 
You need to run plasma2.py.
* grid_size is the size of the tiles used (must be consistent with the downloaded image - e.g. gradient2.pgn which is a tileset of 16x16 images)
* num_shades is the number of images to use from the tileset.
* scale is the scaling factor for the SDL2 renderer - the smaller the finer the plasma. Also the slower. Not gonna lie, I made that code for fun and it's not super fast. For a 640x480 window (so 40x30 tiles) and scale = 1, I get roughly ~350fps with a fairly fast computer and a good GPU. Scale = 0.5 is definitely nicer but also noticeable slower.
* num_effect is the number of waves to use - Again this can be increased with limited impact on performance. But I find no improvement on the effect beyond 10 (personal judgement though)

