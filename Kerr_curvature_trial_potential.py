import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm



########################################################################## CONSTANTS ##################################################################################

G_newton = 6.67430e-11
c_light = 299792458.0
M_sun = 1.98847e30

hbar = 1.054571817e-34                                      # Reduced Planck constant (J s)

M_BH = 10.0 * M_sun                                         # Black-hole mass

r_g = G_newton * M_BH / c_light**2                          # Gravitational length


E_cutoff_GeV = 1.0
GeV_to_joule = 1.602176634e-10

E_cutoff_J = E_cutoff_GeV * GeV_to_joule

Lambda_hat_physical = r_g * E_cutoff_J / (hbar * c_light)


############################################################### HIGGS POTENTIAL MASS PARAMETER #########################################################################

mu_physical_GeV = 88.0

mu_physical_J = mu_physical_GeV * GeV_to_joule
mu_hat = r_g * mu_physical_J / (hbar * c_light)

mu_squared_physical = mu_hat**2


################################################################## KERR BLACKHOLE PARAMETERS ##########################################################################
  
a_star= 0.9                                                 # Dimensionless spin parameter
x_plus= 1 + np.sqrt(1 - a_star**2)                          # Outer event horizon

x = np.linspace(1.02 * x_plus, 10.0, 2400)                  # Radius values with a 2 % safety margin
theta = np.linspace(0, np.pi, 1081)                         # Angle values from North pole to South pole

x_ergo = 1 + np.sqrt(1 - a_star**2 * np.cos(theta)**2)      # Ergosphere

X, TH= np.meshgrid(x, theta)                                # Using radius and angles to form seperate grids


################################################################# DEFINING KRETSCHMANN SCALAR ##########################################################################

c= (a_star * np.cos(TH))**2

numerator= X**6 - 15 * X**4 * c + 15 * X**2 * c**2 - c**3

denominator= (X**2 + c)**6

K= 48 * numerator / denominator

###################################################################### CURVATURE GRADIENTS #############################################################################
  
dK_dx= np.gradient(K, x, axis=1, edge_order=2)                                   # Calculates how the curvature changes as we move radially outward from the black hole

N= X**6 - 15 * X**4 * c + 15 * X**2 * c**2 - c**3
N_prime = 6 * X**5 - 60 * X**3 * c + 30 * X * c**2

dK_dx_analytic= 48 * ( N_prime * (X**2 + c) - 12 * X * N ) / (X**2 + c)**7

radial_error= np.abs(dK_dx - dK_dx_analytic)


i_theta, i_x = np.unravel_index(
    np.argmax(radial_error),
    radial_error.shape
)





dK_dtheta = np.gradient(K, theta, axis=0, edge_order= 2)                        # Calculates how the curvature changes as we move from the north pole to it's south pole


N_c = -15 * X**4 + 30 * X**2 * c - 3 * c**2
c_theta = -2 * a_star**2 * np.sin(TH) * np.cos(TH)

dK_dc = 48 * ( N_c * (X**2 + c) - 6 * N ) / (X**2 + c)**7

dK_dtheta_analytic = dK_dc * c_theta


angular_error = np.abs(dK_dtheta - dK_dtheta_analytic)


Sigma = X**2 + (a_star * np.cos(TH))**2
Delta = X**2 - 2 * X + a_star**2


G_K = ( (Delta / Sigma) * dK_dx_analytic**2 + (1 / Sigma) * dK_dtheta_analytic**2 )


################################################################## TRIAL POTENTIAL PARAMETERS #########################################################################

mu_squared = 1.0
lam = 0.5                                                                                     # Dimensionless toy-model parameters
gamma = 1.0

Lambda_hat = 1.0                                                                              # Dimensionless cutoff: Lambda_hat = r_g * E_cutoff / (hbar * c)

alpha = gamma / Lambda_hat**8

correction = alpha * G_K                                                                      # Relative size of trial correction

physical_correction = gamma * G_K * (1.0 / Lambda_hat_physical)**8

relative_correction = physical_correction / mu_squared_physical

q_min = np.maximum( mu_squared - gamma * G_K / Lambda_hat**8, 0 ) / (2 * lam)


############################################################# VALIDATING NON-ROTATING SCHWARZSCHILD LIMIT ##############################################################

K_schwarzschild= 48 / X**6

##################################################################### VALIDATING ZERO SPIN CASE #######################################################################

a_zero= 0.0
c_zero= (a_zero * np.cos(TH))**2

numerator_zero= ( X**6 - 15 * X**4 * c_zero + 15 * X**2 * c_zero**2 - c_zero**3 )

denominator_zero= (X**2 + c_zero)**6

K_zero= 48 * numerator_zero / denominator_zero


difference = np.abs(K_zero - K_schwarzschild)                                          # Compare against the Schwarzschild reference


################################################################## VALIDATING EQUATORIAL CASE #########################################################################

equator_index= np.argmin(np.abs(theta - np.pi / 2))

K_equator = K[equator_index, :]
K_equator_reference = 48 / x**6

equator_difference = np.abs(K_equator - K_equator_reference)


############################################################## VALIDATING SYMMETRY ACROSS EQUATORIAL PLANE ############################################################

K_reflected = K[::-1, :]

reflection_difference = np.abs(K - K_reflected)



########################################################################### SANITY CHECKS #############################################################################


alpha_crit = mu_squared / G_K.max()                                                         # Analytical threshold for the first zero-minimum grid point

print("\nPredicted critical coupling:", alpha_crit)

for alpha_test in [0.99 * alpha_crit, alpha_crit, 1.01 * alpha_crit]:                                 
    q_test = np.maximum( mu_squared - alpha_test * G_K, 0 ) / (2 * lam)

    print( f"alpha = {alpha_test:.8f}, " f"zero points = {np.sum(q_test == 0)}" )

alpha_values = np.linspace(0.0, 0.1, 101)

zero_fractions = []

for alpha_test in alpha_values:
    q_test = np.maximum(mu_squared - alpha_test * G_K, 0) / (2 * lam)
    zero_fractions.append(np.mean(q_test == 0))    


############################################################################## PLOTTING ################################################################################


norm = SymLogNorm(
    linthresh=1e-3,
    vmin=float(K.min()),                                 # Defining color normalization
    vmax=float(K.max()),
    base=10 )



fig, ax = plt.subplots(figsize=(10, 6))


mesh = ax.pcolormesh(
    X,
    TH,
    K,
    shading="auto",
    cmap="RdBu_r",
    norm=norm
)


ax.contour(
    X, TH, K,
    levels=[0],                                           # Zero-curvature contour
    colors="black",
    linewidths=1.2
)



ax.plot(
    x_ergo,
    theta,
    color="gold",                                         # Outer ergosphere
    linestyle="--",
    linewidth=1.5,
    label="Outer ergosphere"
)


fig.colorbar(mesh, ax=ax, label=r"$M^4 K$")

ax.set_xlabel(r"$r/M$")
ax.set_ylabel(r"$\theta$ (radians)")
ax.set_title(r"Kerr Curvature Map ($a_* = 0.9$)")
ax.legend(loc="upper right")

fig.tight_layout()
fig.savefig("kerr_curvature_map.png", dpi=300, bbox_inches="tight")
plt.show()


##################################################################### PLOTTING TRIAL POTENTIAL MINIMUM #################################################################

fig, ax = plt.subplots(figsize=(10, 6))

mesh = ax.pcolormesh(
    X, TH, q_min,
    shading="auto",
    cmap="viridis",
    vmin=0,
    vmax=1
)

fig.colorbar(mesh, ax=ax, label=r"$q_{\min}$")
ax.set_xlabel(r"$r/M$")
ax.set_ylabel(r"$\theta$ (radians)")
ax.set_title(r"Local Scalar-Potential Minimum in Kerr Spacetime ($a_*=0.9$)")
ax.set_xlim(x.min(), 4.0)

fig.tight_layout()
fig.savefig("scalar_potential_minimum.png", dpi=300, bbox_inches="tight")
plt.show()



##################################################################### PLOT OF COUPLING SENSITIVITY #####################################################################



fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(alpha_values, zero_fractions, linewidth=2)
ax.axvline(alpha_crit, color="red", linestyle="--",
           label="Critical coupling")

ax.set_xlabel(r"Effective coupling $\alpha$")
ax.set_ylabel(r"Fraction of sampled grid points with $q_{\min}=0$")
ax.set_title("Sensitivity of Local Potential Minimum to Coupling")
ax.legend()

fig.tight_layout()
fig.savefig("coupling_sensitivity.png", dpi=300, bbox_inches="tight")
plt.show()

