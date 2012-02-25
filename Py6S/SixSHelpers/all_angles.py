import numpy as np
from matplotlib.pyplot import *

class Angles:
  
  @classmethod
  def run_all_angles(cls, s, solar_or_view, na=36, nz=10):
    #if not isinstance(s, GeometryUser):
    #  raise ParameterError("geometry", "To use the all_angles helper you must be using a user-specified geometry (ie. a GeometryUser instance)")
    
    results = []
    
    azimuths = np.linspace(0, 360, na)
    zeniths = np.linspace(0, 89, nz)
      
    for azimuth in azimuths:
      for zenith in zeniths:
        if solar_or_view == 'view':
          s.geometry.view_a = azimuth
          s.geometry.view_z = zenith
        elif solar_or_view == 'solar':
          s.geometry.solar_a = azimuth
          s.geometry.solar_z = zenith
        else:
          raise ParameterException("all_angles", "You must choose to vary either the solar or view angle.")
        s.run()
        print "%d %d" % (azimuth, zenith)
        results.append(s.outputs)
        
    return (results, azimuths, zeniths, s.geometry.solar_a, s.geometry.solar_z)  
  
  @classmethod
  def extract_output(cls, results, output_name):
    """Extracts data for one particular SixS output from a list of SixS.Outputs instances.
    
    Basically just a wrapper around a list comprehension.
    
    Arguments:
    
     * `results` -- A list of :class:`SixS.Outputs` instances
     * `output_name` -- The name of the output to extract. This should be a string containing whatever is put after the `s.outputs` when printing the output, for example `'pixel_reflectance'`.
    
    """
    results_output = [getattr(r, output_name) for r in results]
    
    return results_output
  
  @classmethod
  def plot_all_angles(cls, data, output_name, show_sun=True):
    results, azimuths, zeniths, sa, sz = data
    
    values = cls.extract_output(results, output_name)  
    
    fig, ax, cax = cls.plot_polar_contour(values, azimuths, zeniths)
    
    if show_sun:
      ax.autoscale(False)
      ax.plot(np.radians(sa), sz, '*', markersize=20, markerfacecolor='yellow', markeredgecolor='red')
      show()
    
    return fig, ax
  
  @classmethod
  def plot_polar_contour(cls, values, azimuths, zeniths):
    """Plot a polar contour plot, with 0 degrees at the North.
    
    Arguments:
     
     * `values` -- A list (or other iterable - eg. a NumPy array) of the values to plot on the contour plot (the `z` values)
     * `azimuths` -- A list of azimuths (in degrees)
     * `zeniths` -- A list of zeniths (that is, radii)
    
    The shapes of these lists are important, and are designed for a particular use case (but should be more generally useful).
    The values list should be `len(azimuths) * len(zeniths)` long with data for the first azimuth for all the zeniths, then
    the second azimuth for all the zeniths etc.
    
    This is designed to work nicely with data that is produced using a loop as follows:
    
    values = []
    for azimuth in azimuths:
      for zenith in zeniths:
        # Do something and get a result
        values.append(result)
        
    After that code the azimuths, zeniths and values lists will be ready to be passed into this function.
    
    """
    theta = np.radians(azimuths)
    zeniths = np.array(zeniths)
  
    values = np.array(values)
    values = values.reshape(len(azimuths), len(zeniths))
  
    r, theta = np.meshgrid(zeniths, np.radians(azimuths))
    fig, ax = subplots(subplot_kw=dict(projection='polar'))
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    autumn()
    cax = ax.contourf(theta, r, values, 30)
    autumn()
    cb = fig.colorbar(cax)
    cb.set_label("Pixel reflectance")
    
    return fig, ax, cax
  
  @classmethod
  def run_and_plot_all_angles(cls, s, solar_or_view, output_name, show_sun=True, na=36, nz=10):
    """Runs Py6S for lots of angles to produce a polar contour plot.
    
    Arguments:
    
     * `s` -- A SixS instance configured with all of the parameters you want to run the simulation with
     * `solar_or_view` -- Set to `'solar'` if you want to iterate over the solar zenith/azimuth angles or `'view'` if you want to iterate over the view zenith/azimuth angles
     * `output_name` -- The name of the output from SixS to plot. This should be a string containing exactly what you would put after `s.outputs` to print the output. For example `pixel_reflectance`.
     * `show_sun` -- (Optional) Whether to place a marker showing the location of the sun on the contour plot (defaults to True, has no effect when `solar_or_view` set to `'solar'`.)
     * `na` -- (Optional) The number of azimuth angles to iterate over to generate the data for the plot (defaults to 36, giving data every 10 degrees)
     * `nz` -- (Optional) The number of zenith angles to iterate over to generate the data for the plot (defaults to 10, giving data every 10 degrees)
    
    For example::
    
    s = SixS()
    s.ground_reflectance = GroundReflectance.HomogeneousWalthall(0.48, 0.50, 2.95, 0.6)
    s.geometry.solar_z = 30
    s.geometry.solar_a = 0
    SixSHelpers.Angles.run_and_plot_all_angles(s, 'view', 'pixel_reflectance')
    
    """
    if solar_or_view == 'solar':
      show_sun = False
    
    res = cls.run_all_angles(s, solar_or_view, na, nz)  
    plot_res = cls.plot_all_angles(res, output_name, show_sun)
    
    return plot_res
  
  @classmethod
  def run_principal_plane(cls, s):
    # Get the solar azimuth and zenith angles from the SixS instance
    sa = s.geometry.solar_a
    sz = s.geometry.solar_z
    
    ## Compute the angles in the principal plane
    
    # Get the equivalent view zenith for the solar zenith angle
    vz_for_sz = 90 - sz
    # Get the solar azimuth on the opposite side for the other half of the principal plane
    opp_sa = (sa + 180) % 360
    
    # Calculate the first side (the solar zenith angle side)
    first_side_z = np.arange(vz_for_sz, -5, -5)
    first_side_a = np.repeat(sa, len(first_side_z))
    
    # Calculate the other side
    temp = first_side_z[:-1]
    second_side_z = temp[::-1] # Reverse array
    second_side_a = np.repeat(opp_sa, len(second_side_z))
    
    # Join the two sides together
    all_zeniths = np.hstack((first_side_z, second_side_z))
    all_azimuths = np.hstack((first_side_a, second_side_a))
    
    ## Iterate over these angles and get the results
    
    results = []
    
    for i in range(len(all_zeniths)):
      print all_zeniths[i]
      print all_azimuths[i]
      
      s.geometry.view_z = all_zeniths[i]
      s.geometry.view_a = all_azimuths[i]
      s.run()
      results.append(s.outputs.pixel_reflectance)
    
      
    # Must deal with zeniths and make half of them negative before returning, so plotting works
    return all_zeniths, results
