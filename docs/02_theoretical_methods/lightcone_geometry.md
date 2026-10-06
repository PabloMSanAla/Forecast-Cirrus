# Cosmological Lightcone Geometry

The primary task of cosmological forward modeling is transforming Euclidean simulation snapshots at discrete times into an observer-centered past lightcone $z(t)$.

---

## 1. Observer-Centered Cone Construction

FORECAST places the virtual observer at the origin $\vec{x}_{\text{obs}} = (0, 0, 0)$ at $z = 0$. The lightcone extends along the line of sight (LOS, chosen along the $z$-axis) up to a maximum source redshift $z_s$, corresponding to a maximum comoving radial distance:

$$D_c(z_s) = \frac{c}{H_0} \int_0^{z_s} \frac{dz'}{\sqrt{\Omega_{m,0}(1+z')^3 + \Omega_{\Lambda,0}}}$$

### Geometry Slicing into Concentric Shells (Planes)
Because cosmological simulations store data at discrete snapshots $\{S_0, S_1, \dots, S_M\}$, the total lightcone volume is partitioned into $N$ concentric spherical shells (referred to as **planes** $i = 0, \dots, N-1$).

Each plane $i$ is defined by:
- A near boundary comoving distance $D_{c,i}$
- A far boundary comoving distance $D_{c,i+1}$
- A slice thickness $\Delta D_{c,i} = D_{c,i+1} - D_{c,i}$
- An associated simulation snapshot $S(i)$ whose cosmological epoch best matches the shell's central redshift $z_i$.

The exact geometry of all planes is pre-computed and stored in `planes_list.txt`.

---

## 2. Periodic Box Replication and Randomization

Simulation volumes have a finite periodic box side length $L_{\text{box}}$ (e.g. $35\,h^{-1}\text{Mpc}$ for TNG50 or $75\,h^{-1}\text{Mpc}$ for TNG100). When the required comoving distance $D_c(z)$ exceeds $L_{\text{box}}$, the simulation box must be replicated periodically.

To prevent the observer from seeing the exact same galaxy structures aligned repetitively along the line of sight, FORECAST applies pseudo-random coordinate transformations for each replication $k$:

$$\vec{x}' = \mathcal{R}_k \cdot \vec{x}_{\text{sim}} + \vec{s}_k$$

where:
- $\mathcal{R}_k \in \text{SO}(3)$ is a 3D orthogonal rotation matrix randomly selected from the 24 symmetry rotations of a cube (or arbitrary 3D Euler angles).
- $\vec{s}_k \in [0, L_{\text{box}}]^3$ is a random 3D translation vector.

---

## 3. Field of View (FoV) Angular Clipping

For a user-specified square Field of View with angular side length $\theta_{\text{FoV}}$ (in degrees):

1. A star particle at rotated comoving coordinates $(x', y', z')$ is projected onto angular coordinates:
   $$\theta_x = \arctan\left(\frac{x'}{z'}\right), \quad \theta_y = \arctan\left(\frac{y'}{z'}\right)$$
2. The particle is accepted into the lightcone plane if and only if:
   $$D_{c,i} \le z' < D_{c,i+1} \quad \text{and} \quad |\theta_x| \le \frac{\theta_{\text{FoV}}}{2}, \quad |\theta_y| \le \frac{\theta_{\text{FoV}}}{2}$$

Accepted particles are stored in the intermediate catalog `coords.lc.<snap>_<plane>.txt`.
