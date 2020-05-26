import numpy
import matplotlib.pyplot
import matplotlib.path
import matplotlib.patches
import scipy.spatial
import time

# we also want the 3D stuff for the time being
from mpl_toolkits.mplot3d import Axes3D

import builtins

# use this so we can avoid profiler issues
try:
    builtins.profile
except AttributeError:
    # this is the case when we're not running a profiler
    def profile(func): return func
    builtins.profile = profile

# define the vertices of the paths
_verts = numpy.array([(0.2, 0.0),
                      (0.8, 0.0), # start of the lower right corner
                      (1.0, 0.0), # intermediate point (as if it wasn't rounded)
                      (1.0, 0.2), # end point of the lower right corner
                      (1.0, 0.8), # move to the next point etc.
                      (1.0, 1.0),
                      (0.8, 1.0),
                      (0.2, 1.0),
                      (0.0, 1.0),
                      (0.0, 0.8),
                      (0.0, 0.2),
                      (0.0, 0.0),
                      (0.2, 0.0)])

_scale = numpy.array([1, 1.5])

# and the associated curves
_codes = numpy.array([matplotlib.path.Path.MOVETO,
                      matplotlib.path.Path.LINETO,
                      matplotlib.path.Path.CURVE3,
                      matplotlib.path.Path.CURVE3,
                      matplotlib.path.Path.LINETO,
                      matplotlib.path.Path.CURVE3,
                      matplotlib.path.Path.CURVE3,
                      matplotlib.path.Path.LINETO,
                      matplotlib.path.Path.CURVE3,
                      matplotlib.path.Path.CURVE3,
                      matplotlib.path.Path.LINETO,
                      matplotlib.path.Path.CURVE3,
                      matplotlib.path.Path.CURVE3])

# and make the path
def _rounded_verts(x_offset, y_offset):
    return matplotlib.path.Path(_verts * _scale + numpy.array([x_offset, y_offset]), _codes)


# this will hold the offsets (duplicate coordinates) for the periodic boundary conditions
_offset_cubes = numpy.array([(i, j, k) for i in range(-1, 2) for j in range(-1, 2) for k in range(-1, 2)])

class Points():

    def __init__(self, n, force=2, dim=3, scale=10, periodic=False):
        # first make the random points in a 1x1x1 cube centred at the origin
        self.points = numpy.random.random((n, 3)) * scale
        self.scale = scale

        # we'll define these auxillary attributes to make them easier to find later
        self.x = self.points[:, 0]
        self.y = self.points[:, 1]
        self.z = self.points[:, 2]

        # store the force strength and number of dimensions
        self.force = force
        self.dim = dim  # this defines the drop off of the force with distance

        # we'll store the deltas too
        self.delta = numpy.zeros(self.points.shape)

        self.fixed = numpy.array([True] + [False] * (n - 1))
        self.periodic = periodic

    def get_normed_points(self):
        """Return the normalised points."""
        return self.points / self.scale

    @profile
    def _get_distances(self):
        """Calculate the separation between each pair of points."""

        # here we want to account for periodic boundary conditions
        if self.periodic:
            # we want to duplicate the volume on each side of the cube
            offsets = numpy.repeat(_offset_cubes, self.points.shape[0], axis=0) * self.scale
            new_points = numpy.tile(self.points, (_offset_cubes.shape[0], 1)) + offsets

            # now find the distances between the original points and the new points
            dist = scipy.spatial.distance.cdist(self.points, new_points)

            # reshape for improved performance
            dist = dist.reshape((self.points.shape[0], new_points.shape[0] // self.points.shape[0], self.points.shape[0]))
            result2 = numpy.min(dist, axis=1)

            return result2


        return scipy.spatial.distance.cdist(self.points, self.points)

    @profile
    def _move(self, dt=1):
        """Separate the points according to the repulsive force between them."""
        # first get the distances
        dist = self._get_distances()
        # mask = ~numpy.eye(dist.shape[0], dtype=numpy.bool)

        # and the vectors
        vectors = self.points - self.points[:, None]

        # now we can calculate the forces
        forces = numpy.zeros(vectors.shape)
        forces[dist != 0] = self.force * vectors[dist != 0]  / dist.reshape(vectors.shape[0], vectors.shape[1], 1)[dist != 0]**self.dim
        # forces[mask] = self.force * vectors[mask]  / dist.reshape(vectors.shape[0], vectors.shape[1], 1)[mask]**self.dim

        # now sum the forces for each point
        total_forces = forces.sum(axis=0)

        # and update the positions of each of the points
        self.points[~self.fixed] += total_forces[~self.fixed] * dt

        # and account for the bounding box
        if self.periodic:
            self.points[self.points >= self.scale] -= self.scale
            self.points[self.points <= 0] += self.scale
        else:
            self.points[self.points >= self.scale] = self.scale
            self.points[self.points <= 0] = 0


    def spread(self, times=200, dt=1):
        """Spread the points throughout the available space."""
        for i in range(times):
            self._move(dt)


def _visualise_movement():
    numpy.random.seed(0)
    points = Points(20, force=10, dim=8, periodic=True)

    # make the plot interactive
    matplotlib.pyplot.ion()
    figure = matplotlib.pyplot.figure()

    ax = figure.add_subplot(1, 1, 1, projection='3d')

    scatter = ax.scatter(points.x, points.y, points.z, color='g')

    matplotlib.pyplot.draw()
    for i in range(200):
        points._move(1)
        scatter._offsets3d = (points.x, points.y, points.z)

        # update the plot
        figure.canvas.draw()
        matplotlib.pyplot.pause(0.1)

    matplotlib.pyplot.waitforbuttonpress()

_balances = {'D65': (95.0489, 100, 108.8840)}
_xyz_srgb_matrix = numpy.array([[3.2404542, -1.5371385, -0.4985314],
                                [-0.9692660,  1.8760108,  0.0415560],
                                [0.0556434, -0.2040259,  1.0572252]])

class Colour():


    def __init__(self, value, illuminant='D65'):
        self.L = value[0]
        self.a = value[1]
        self.b = value[2]

        # we should get the appropriate white balance transformation
        self.xyz_norm = _balances[illuminant]
        self.xyz_matrix = _xyz_srgb_matrix

        # perform the in-situ conversion between the colours
        self.xyz = self._to_xyz()
        self.rgb = self._to_rgb()
        self.lab = numpy.array(value)  # using the list in case it's a tuple

        self.hex = self._get_hex()

    def _get_hex(self):
        """Get the hex code for Colour."""
        r, g, b = self.rgb.astype(numpy.int)
        return "#{0:02x}{1:02x}{2:02x}".format(r, g, b)  # strip off the hex garbage

    def _f_prime(self, t):
        """The inverse weighting function for Lab -> XYZ."""
        delta = 6 / 29  # some constant

        if t > delta:
            return t**3
        else:
            return 3 * delta**2 * (t - 4 / 29)

    def _to_rgb(self):
        """Return the RGB representation of the colour."""
        # this will involve some matrix elements
        rgb = self.xyz_matrix @ self.xyz.T

        # now we have to compand(?) it
        RGB = numpy.empty(rgb.shape)
        mask = rgb <= 0.0031308
        RGB[mask] = 12.92 * rgb[mask]
        RGB[~mask] = 1.055 * rgb[~mask]**(1/2.4) - 0.055

        # and clip the values
        RGB[RGB >= 1] = 1
        RGB[RGB <= 0] = 0
        return numpy.round_(RGB * 255)

    def _to_xyz(self):
        """Return the XYZ representation of the colour."""
        # these are the known transforms from Lab to XYZ
        x = self.xyz_norm[0] * self._f_prime((self.L + 16) / 116 + self.a / 500)
        y = self.xyz_norm[1] * self._f_prime((self.L + 16) / 116)
        z = self.xyz_norm[2] * self._f_prime((self.L + 16) / 116 - self.b / 200)
        return numpy.array([x, y, z]) / 100


class ColourScheme():


    def __init__(self, n):
        """Generate a colour scheme of n colours."""
        self.size = n

        self.hue_limit = [0, 2*numpy.pi]
        self.chroma_limit = [0, 100]
        self.light_limit = [0, 100]

        self.colours = self._find_colours()

    def reroll(self):
        """Regenerate the colours."""
        self.colours = self._find_colours()
        self.show()

    def set_chroma_limit(self, a, b):
        """Set the limits on the chroma scale."""
        assert(a <= b)
        
        self.chroma_limit = [a, b]
    
    def set_hue_limit(self, a, b):
        """Set the limits on the hue scale."""
        assert(a <= b)
        
        self.hue_limit = [a * numpy.pi / 180, b * numpy.pi / 180]
    
    def set_light_limit(self, a, b):
        """Set the limits on the light scale."""
        assert(a <= b)
        
        self.light_limit = [a, b]

    def _hcl_lab_limits(self):
        """Generate the limits of Lab given the HCL limitations."""
        # first find the limits for a
        if self.hue_limit[0] <= numpy.pi and self.hue_limit[1] >= numpy.pi:
            # then the minimum value is -1
            a_min_scale = -1
        else:
            a_min_scale = min(numpy.cos(self.hue_limit[0]),
                              numpy.cos(self.hue_limit[1]))

        # the max is just the max in the values
        a_max_scale = max(numpy.cos(self.hue_limit[0]),
                          numpy.cos(self.hue_limit[1])) 

        # now check the sign of the interval
        if numpy.cos(self.hue_limit[0]) * numpy.cos(self.hue_limit[1]) > 0:
            # then they have the same sign
            if numpy.cos(self.hue_limit[0]) < 0:
                # in this the interval is negative a only
                a_min = a_max_scale * self.chroma_limit[1]
                a_max = a_min_scale * self.chroma_limit[0]
            else:
                a_max = a_max_scale * self.chroma_limit[1]
                a_min = a_min_scale * self.chroma_limit[0]

        else:  # this is the limit where there's a zero included
            a_min = a_min_scale * self.chroma_limit[1]
            a_max = a_max_scale * self.chroma_limit[1]

        # now we need to do the same thing for b
        if self.hue_limit[0] <= 3 * numpy.pi / 2 and self.hue_limit[1] >= 3 * numpy.pi / 2:
            # then the minimum value is -1
            b_min_scale = -1
        else:
            b_min_scale = min(numpy.sin(self.hue_limit[0]),
                              numpy.sin(self.hue_limit[1]))

        # the max is just the max in the values
        if self.hue_limit[0] <= numpy.pi / 2 and self.hue_limit[1] >= numpy.pi / 2:
            b_max_scale = 1
        else:
            b_max_scale = max(numpy.sin(self.hue_limit[0]),
                              numpy.sin(self.hue_limit[1])) 

        # now check the sign of the interval
        if numpy.sin(self.hue_limit[0]) * numpy.sin(self.hue_limit[1]) > 0:
            # then they have the same sign
            if numpy.sin(self.hue_limit[0]) < 0:
                # in this the interval is negative a only
                b_min = b_max_scale * self.chroma_limit[1]
                b_max = b_min_scale * self.chroma_limit[0]
            else:
                b_max = b_max_scale * self.chroma_limit[1]
                b_min = b_min_scale * self.chroma_limit[0]

        else:  # this is the limit where there's a zero included
            b_min = b_min_scale * self.chroma_limit[1]
            b_max = b_max_scale * self.chroma_limit[1]

        a_min / 100 * 127
        b_min / 100 * 127
        a_max / 100 * 127
        b_max / 100 * 127

        return a_min, a_max, b_min, b_max


    def _find_colours(self):
        """Find the colours in perceptually uniform space."""
        # first we should make a set of points
        # the dimension and force should be tweaked to make sure we're getting some nice
        # separation of the values
        points = Points(self.size, periodic=True, dim=8, force=20)
        points.spread(200)  # and spread them throughout the space

        # convert those into CIELab values
        # make sure we consider the contraints in the ranges
        a_min, a_max, b_min, b_max = self._hcl_lab_limits()
        lab_values = points.get_normed_points() * numpy.array([self.light_limit[1] - self.light_limit[0],
                                                               a_max - a_min, b_max - b_min])
        lab_values += numpy.array([self.light_limit[0], a_min, b_min])  # remove the offsets

        # now convert those points into Colour objects
        colours = [Colour(i) for i in lab_values]

        return colours 

    def get_rgb(self):
        """Print the RGB values of the colours in the scheme."""
        for colour in self.colours:
            print(colour.rgb)

    def show(self, x_offset=1.5, y_offset=2, ncol=5):
        """Show the colour scheme."""
        figure = matplotlib.pyplot.figure()

        ax = figure.add_subplot(1, 1, 1, aspect='equal')
        ax.axis('off')

        # now let's make the patches
        for index, colour in enumerate(self.colours):
            patch = matplotlib.patches.PathPatch(_rounded_verts(x_offset * (index % ncol), -y_offset * (index // ncol)),
                                                 facecolor=colour.rgb/255, lw=0.5)

            ax.add_patch(patch)

        ax.set_ylim(-5, 5)
        ax.set_xlim(0, 10)

        matplotlib.pyplot.show()


def _interval_testing():

    h_range = numpy.linspace(280, 335, 100) * numpy.pi / 180
    c_range = numpy.linspace(0.2, 0.7, 100)

    test = c_range[:, None] * numpy.cos(h_range)
    test = test.flatten()

    # let's see what we can do with a uniform distribution
    uniform = numpy.linspace(0, 1, 100)

    figure = matplotlib.pyplot.figure()

    ax = figure.add_subplot(1, 1, 1)

    ax.hist(test, bins=100, range=(-1, 1), density=True)

    matplotlib.pyplot.show()




if __name__ == "__main__":
    
    # _visualise_movement()
    points = Points(20, periodic=True)
    for i in range(200):
        points._move()
