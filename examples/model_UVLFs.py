import numpy as np 
import matplotlib.pyplot as plt 
import GalaxyTools

lstyles = ['-', '--', '-.', ':']

#set parameters
par = GalaxyTools.par()
par.file.ps = "CDM_Planck15_pk.dat"

par.code.zmin = 5
par.code.zmax = 40
par.code.Nz   = 50
par.code.dz_prime_lyal = 0.01
par.code.dz_prime_xray = 0.1

par.code.Mmin = 5e5  #5e4
par.code.Mmax = 2e15
par.code.NM   = 100

par.code.kmin = 0.001
par.code.kmax = 100
par.code.Nk   = 90

par.code.Emin = 500
par.code.Emax = 2000
par.code.NE   = 40

par.mf.window = 'tophat'
par.mf.c      = 2.5
par.mf.q      = 0.85
par.mf.p      = 0.3

par.code.MA = 'EXP' #'EPS'

par.lyal.f0 = 0.05 #0.20
par.lyal.g1 = -0.5
par.lyal.g2 = -0.5

par.xray.f0 = 0.05 #0.20
par.xray.g1 = -0.5
par.xray.g2 = -0.5

par.code.Mdark = 1e5

par.lyal.Nal = 5000 
par.lyal.pl_sed = 0.0

par.xray.pl_sed = 1.5
par.xray.cX  = 3.4e40
par.xray.Emin_norm = 500
par.xray.Emax_norm = 2000
par.xray.fX  = 1.0

par.reio.Nion = 2000
par.reio.fesc = 1.0

par.lf.Muv_min = -23.
par.lf.Muv_max = -15 #-10.
par.lf.NMuv  = 20
par.lf.sig_M = 0.2
par.lf.eps_sys = 1.0

print(par.xray.__dict__)
print(par.lf.__dict__)
fig, axs = plt.subplots(1,3,figsize=(14,4))

## HMF
hmf = GalaxyTools.mass_fct(par)

z_plot = [6,7,8]
ax = axs[0] # fig, ax = plt.subplots(1,1,figsize=(6,4))
for ii,zi in enumerate(z_plot):
    z_idx = np.abs(hmf['z']-zi).argmin() 
    ax.loglog(hmf['m'], hmf['dndlnm'][z_idx,:], lw=3, ls=lstyles[ii], label='z={:.1f}'.format(zi))
ax.legend()
ax.axis([3e6,3e12,5e-6,8e2])
ax.set_xlabel(r'$M$ [$h^{-1}$M$_\odot$]', fontsize=13)
ax.set_ylabel(r'$\frac{\mathrm{d}n}{\mathrm{d}lnM}$', fontsize=15)
# plt.tight_layout()
# plt.show()

## UV LFs
M0 = 51.6
kappa  = 1.15e-28  # Msun yr^-1 /(erg s^-1 Hz^-1)
fstars = GalaxyTools.fstar(hmf['z'], hmf['m'], 'xray', par)

z_plot = [6,7,8]
ax = axs[1] # fig, ax = plt.subplots(1,1,figsize=(6,4))
for ii,zi in enumerate(z_plot):
    z_idx = np.abs(hmf['z']-zi).argmin() 
    ax.loglog(hmf['m'], fstars[z_idx,:], lw=3, ls=lstyles[ii], label='z={:.1f}'.format(zi))
ax.legend()
ax.axis([5e5,3e14,5e-6,8e-2])
ax.set_xlabel(r'$M$ [$h^{-1}$M$_\odot$]', fontsize=13)
ax.set_ylabel(r'$\frac{\mathrm{d}n}{\mathrm{d}lnM}$', fontsize=15)
# plt.tight_layout()
# plt.show()

m_ac = GalaxyTools.mass_accr(par, output=hmf)
uvlf = GalaxyTools.UVLF(par)
# out_lf = uvlf.Muv(); print(out_lf.keys())
out_lf = uvlf.UV_luminosity(); # print(out_lf.keys())

B2015_data = np.loadtxt('Bouwen2015_in_SZ21.txt')

z_plot = [6,7,8]
ax = axs[2] # fig, ax = plt.subplots(1,1,figsize=(6,4))
B2015_z6_mean = B2015_data[:,1]/2.+B2015_data[:,2]/2.
B2015_z6_std  = np.abs(B2015_data[:,2]-B2015_z6_mean)
ax.errorbar(B2015_data[:,0], B2015_z6_mean, yerr=B2015_z6_std, c='r', ls=' ')
for ii,zi in enumerate(z_plot):
    z_idx = np.abs(out_lf['z']-zi).argmin() 
    ax.plot(out_lf['uvlf']['Muv_mean'], out_lf['uvlf']['phi_uv'][z_idx,:], lw=3, ls=lstyles[ii], label='z={:.1f}'.format(zi))
ax.set_yscale('log')
ax.legend()
ax.axis([-23.2,-14.8,5e-7,4e-2])
ax.set_xlabel(r'$M_{\rm UV}$', fontsize=13)
ax.set_ylabel(r'$\phi (M_{\rm UV})$', fontsize=15)
plt.tight_layout()
plt.show()

exit()

from scipy.integrate import quad, simps
from scipy.interpolate import splev, splrep, interp1d

def UV_luminosity_SZ21_def(self):
    param  = self.param
    output = self.output
    try: M_AB = output['M_AB']
    except:
        output = self.Muv(M0=51.6, kappa=1.15e-28)
        M_AB = output['M_AB']
    zz = output['z']
    mm = output['m']
    dndlnm = output['dndlnm']
    Muv_edges = np.linspace(param.lf.Muv_min,param.lf.Muv_max,param.lf.NMuv+1)
    Muv_mean  = Muv_edges[1:]/2.+Muv_edges[:-1]/2.
    phi_uv = np.zeros((len(zz),len(Muv_mean)))
    dMab = np.diff(M_AB)
    dMh  = np.diff(mm)
    dMhdMab = -dMh[None,:]/dMab #dMh[None,:]/dMab
    for i in range(zz.size):
        dndm_fct   = interp1d(M_AB[i,:], dndlnm[i,:]/mm, fill_value='extrapolate')
        dMuvdm_fct = interp1d(M_AB[i,1:]/2+M_AB[i,:-1]/2, dMhdMab[i,:], fill_value='extrapolate')
        phi_uv[i,:] = dndm_fct(Muv_mean) * dMuvdm_fct(Muv_mean)
    output['uvlf'] = {'Muv_mean': Muv_mean, 'phi_uv': phi_uv}
    self.output = output
    return output 


out_lf1 = UV_luminosity_SZ21_def(uvlf)

z_plot = [6,7,8]
fig, ax = plt.subplots(1,1,figsize=(6,4))
for ii,zi in enumerate(z_plot):
    z_idx = np.abs(out_lf['z']-zi).argmin() 
    ax.plot(out_lf1['uvlf']['Muv_mean'], out_lf1['uvlf']['phi_uv'][z_idx,:], lw=3, ls=lstyles[ii], label='z={:.1f}'.format(zi))
ax.legend()
# ax.axis([5e5,3e14,5e-6,8e-2])
ax.set_xlabel(r'$M_{\rm UV}$', fontsize=13)
ax.set_ylabel(r'$\phi (M_{\rm UV})$', fontsize=15)
plt.tight_layout()
plt.show()
