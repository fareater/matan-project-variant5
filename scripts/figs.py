import nbformat, numpy as np, sympy as sp, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.optimize import minimize, minimize_scalar, brentq

nb = nbformat.read('project_team_N.ipynb', 4)
src = "\n".join(c.source for i, c in enumerate(nb.cells) if c.cell_type == 'code' and i in (1, 9, 13))
src = src.replace("print(", "(lambda *a, **k: None)(")
exec(src)

PUR, PINK, DARK, TEAL, GRAY = '#9600FF', '#E0309A', '#1E1E1E', '#00A6A6', '#8C8C8C'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.edgecolor': '#BBBBBB', 'axes.labelcolor': DARK,
                     'xtick.color': '#555555', 'ytick.color': '#555555', 'axes.grid': True,
                     'grid.color': '#EEEEEE', 'legend.frameon': False, 'mathtext.fontset': 'dejavusans'})
os.makedirs('figs', exist_ok=True)

def split(B, **kw):
    if B <= 0: return 0.0, 0.0, E(0, 0, **kw)
    r = minimize_scalar(lambda s: E(s, B - s, **kw), bounds=(0, B), method='bounded', options={'xatol': 1e-7})
    return r.x, B - r.x, r.fun

# ---------- 1. C(B), E(B), lambda(B)
Bs = np.linspace(0, 4, 81)
S = np.array([split(B) for B in Bs])
lam = []
for B, (s1, s2, _) in zip(Bs, S):
    lam.append(np.nan if B == 0 else -grad_E(s1, s2)[0] if s1 > 1e-4 else -grad_E(s1, s2)[1])
lam = np.array(lam)
Bst = 1.626
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
ax[0].plot(Bs, Bs + S[:, 2], color=PUR, lw=3, label='Общие потери C(B) = B + E*(B)')
ax[0].plot(Bs, S[:, 2], color=PINK, lw=2, ls='--', label='Ожидаемые убытки E*(B)')
ax[0].plot(Bs, Bs, color=GRAY, lw=1.5, ls=':', label='Затраты на защиту B')
ax[0].scatter([Bst], [Bst + split(Bst)[2]], s=90, color=PINK, zorder=5)
ax[0].annotate('B* = 1,63 млн\nC* = 3,85 млн', (Bst, 3.85), (2.3, 4.6), arrowprops=dict(arrowstyle='->', color=DARK), fontsize=12)
ax[0].set_xlabel('Бюджет защиты B, млн ₽'); ax[0].set_ylabel('млн ₽'); ax[0].legend(fontsize=10, loc='lower right'); ax[0].set_ylim(0, 6)
ax[1].plot(Bs, lam, color=PUR, lw=3)
ax[1].axhline(1, color=PINK, ls='--'); ax[1].axvline(Bst, color=GRAY, ls=':')
ax[1].text(2.6, 1.08, 'λ = 1: рубль защиты\nспасает ровно рубль', color=PINK, fontsize=11)
ax[1].fill_between(Bs, lam, 1, where=lam > 1, color=PUR, alpha=.08)
ax[1].set_xlabel('Бюджет защиты B, млн ₽'); ax[1].set_ylabel('λ(B) = −∂E/∂x')
ax[1].set_title('Множитель Лагранжа — предельная отдача', fontsize=12)
ax[0].set_title('Кривая «затраты — потери»', fontsize=12)
plt.tight_layout(); plt.savefig('figs/lambda.png', dpi=200); plt.close()

# ---------- 2. 3D
gx = np.linspace(0, 3, 36); gy = np.linspace(0, 3, 36)
X, Y = np.meshgrid(gx, gy)
Z = np.vectorize(lambda a1, a2: a1 + a2 + E(a1, a2))(X, Y)
fig = plt.figure(figsize=(12, 5))
ax = fig.add_subplot(121, projection='3d')
ax.plot_surface(X, Y, Z, cmap='PuRd_r', alpha=1.0, rstride=1, cstride=1, linewidth=0, antialiased=True)
ax.set_xlabel('x₁ предотвращение, млн', labelpad=8); ax.set_ylabel('x₂ обнаружение, млн', labelpad=8); ax.set_zlabel('C, млн ₽', labelpad=6)
ax.view_init(30, -60); ax.set_title('C(x₁,x₂) = x₁ + x₂ + E(x₁,x₂)', fontsize=13)
ax2 = fig.add_subplot(122)
cs = ax2.contourf(X, Y, Z, levels=20, cmap='PuRd_r'); fig.colorbar(cs, ax=ax2, label='C, млн ₽')
ax2.contour(X, Y, Z, levels=[3.9, 4.0, 4.2], colors='white', linewidths=1)
ax2.plot([0, 3], [3, 0], color='white', ls='--', lw=1); ax2.text(2.05, 0.75, 'x₁+x₂ = 3', color='white', fontsize=10, rotation=-38)
ax2.scatter([0.985], [0.642], s=110, color='white', edgecolor=DARK, zorder=5)
ax2.annotate('оптимум (0,99; 0,64)\nC* = 3,85 млн', (0.985, 0.642), (1.45, 1.7), color='white', fontsize=12,
             arrowprops=dict(arrowstyle='->', color='white'))
ax2.set_xlabel('x₁ предотвращение, млн'); ax2.set_ylabel('x₂ обнаружение, млн'); ax2.grid(False)
ax2.set_title('Линии уровня C = const', fontsize=13)
plt.tight_layout(); plt.savefig('figs/surface3d.png', dpi=200, bbox_inches='tight'); plt.close()

# ---------- 3. slider states
fig, axs = plt.subplots(1, 3, figsize=(12, 3.6), sharey=True)
Bg = np.linspace(0, 4, 41)
for axx, m in zip(axs, [0.3, 0.5, 0.7]):
    kw = dict(A=6 * m, Bb=6 * (1 - m))
    rr = np.array([split(B, **kw) for B in Bg]); Ct = Bg + rr[:, 2]; k = Ct.argmin()
    axx.plot(Bg, Ct, color=PUR, lw=3, label='C(B)'); axx.plot(Bg, rr[:, 2], color=PINK, ls='--', label='E*(B)')
    axx.bar(Bg[k], rr[k, 0], width=.18, color=DARK, label='x₁*'); axx.bar(Bg[k], rr[k, 1], bottom=rr[k, 0], width=.18, color=TEAL, label='x₂*')
    axx.set_title(f'q̄ = {m}:  B* ≈ {Bg[k]:.1f},  x₁/x₂ = {rr[k,0]:.1f}/{rr[k,1]:.1f}', fontsize=11)
    axx.set_xlabel('B, млн ₽')
axs[0].set_ylabel('млн ₽'); axs[0].legend(fontsize=9, loc='upper right')
plt.tight_layout(); plt.savefig('figs/slider.png', dpi=200); plt.close()

# ---------- 4. boundaries
rows = []
for m in np.linspace(0.1, 0.95, 35):
    kw = dict(A=6 * m, Bb=6 * (1 - m))
    r = minimize(lambda x: x[0] + x[1] + E(x[0], x[1], **kw), [0.8, 0.5], bounds=[(0, 10), (0, 10)], method='L-BFGS-B')
    rows.append((m, *r.x))
bd = np.array(rows)
rows = []
for gv in np.linspace(0.005, 0.12, 47):
    r = minimize(lambda x: x[0] + x[1] + E(x[0], x[1], g_=gv), [0.8, 0.5], bounds=[(0, 10), (0, 10)], method='L-BFGS-B')
    rows.append((gv, *r.x))
bgv = np.array(rows)
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(bd[:, 0], bd[:, 1], color=DARK, lw=2.5, label='x₁* предотвращение'); ax[0].plot(bd[:, 0], bd[:, 2], color=TEAL, lw=2.5, label='x₂* обнаружение')
ax[0].axvspan(0.72, 0.95, color=PINK, alpha=.12); ax[0].text(0.74, 0.55, 'APT-зона:\nx₁* = 0', color=PINK, fontsize=11)
ax[0].set_xlabel('средняя квалификация злоумышленника q̄'); ax[0].set_ylabel('млн ₽'); ax[0].legend(fontsize=10, loc='upper left')
ax[1].plot(bgv[:, 0], bgv[:, 1], color=DARK, lw=2.5, label='x₁*'); ax[1].plot(bgv[:, 0], bgv[:, 2], color=TEAL, lw=2.5, label='x₂*')
ax[1].axvspan(0.005, 0.022, color=TEAL, alpha=.10); ax[1].axvspan(0.060, 0.12, color=GRAY, alpha=.12)
ax[1].text(0.006, 2.2, 'только\nмониторинг', color=TEAL, fontsize=10); ax[1].text(0.072, 0.35, 'только\nпредотвращение', color=DARK, fontsize=10)
ax[1].axvline(0.04, color=PINK, ls=':'); ax[1].text(0.041, 0.05, 'наш g', color=PINK, fontsize=10)
ax[1].set_xlabel('скорость нанесения ущерба g, 1/день'); ax[1].legend(fontsize=10, loc='upper center')
plt.tight_layout(); plt.savefig('figs/bounds.png', dpi=200); plt.close()

# ---------- 5. noise
np.random.seed(1)
x_opt = np.array([0.985, 0.642]); out = []
for _ in range(300):
    an, bn, gn = a * np.random.normal(1, .1), b * np.random.normal(1, .1), g * np.random.normal(1, .1)
    cost = np.random.normal(1, .2)
    r = minimize(lambda x: cost * (x[0] + x[1]) + E(x[0], x[1], a_=an, b_=bn, g_=gn), [1, .6], bounds=[(0, 10), (0, 10)], method='L-BFGS-B')
    out.append((r.x.sum(), cost * x_opt.sum() + E(*x_opt, a_=an, b_=bn, g_=gn) - r.fun, r.fun))
out = np.array(out)
np.save('figs/noise.npy', out)
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
ax[0].hist(out[:, 0], bins=25, color=PUR, alpha=.85); ax[0].axvline(1.626, color=PINK, lw=2.5)
ax[0].set_xlabel('оптимальный бюджет B* при шуме, млн ₽'); ax[0].set_ylabel('число прогонов')
ax[0].set_title(('B* «гуляет»: 90 %% в [%.2f; %.2f]' % tuple(np.percentile(out[:, 0], [5, 95]))).replace('.', ','), fontsize=12)
ax[1].hist(out[:, 1], bins=25, color=TEAL, alpha=.85)
ax[1].set_xlabel('потеря от номинального решения, млн ₽'); ax[1].set_title(('…а потери почти не меняются: медиана %.3f' % np.median(out[:, 1])).replace('.', ','), fontsize=12)
plt.tight_layout(); plt.savefig('figs/noise.png', dpi=200); plt.close()
print('5/95 B*', np.percentile(out[:, 0], [5, 50, 95]), 'regret', np.percentile(out[:, 1], [50, 95]), out[:, 1].max())

# ---------- formulas
def formula(tex, name, fs=22, w=9, h=0.9, color=DARK):
    fig = plt.figure(figsize=(w, h)); fig.patch.set_alpha(0)
    fig.text(0.0, 0.5, tex, fontsize=fs, va='center', ha='left', color=color)
    plt.savefig(f'figs/{name}.png', dpi=250, transparent=True, bbox_inches='tight', pad_inches=0.02); plt.close()
formula(r'$E(x_1,x_2)=\int_0^1\!\int_0^{T(x_2)} P(x_1,q)\;L(q,t)\;f(q)\;\frac{1}{T(x_2)}\;dt\,dq$', 'f_E', fs=24)
formula(r'$C(x_1,x_2)=x_1+x_2+E(x_1,x_2)\;\rightarrow\;\min$', 'f_C', fs=22)
formula(r'$P=e^{-a\,x_1(1-q)}$', 'f_P', fs=20)
formula(r'$T(x_2)=\frac{T_0}{1+b\,x_2}$', 'f_T', fs=20)
formula(r'$L=V\,(1-e^{-g\,q\,t})$', 'f_L', fs=20)
formula(r'$f(q)=6q(1-q)$', 'f_f', fs=20)
formula(r'$\frac{1}{T}\int_0^{T}(1-e^{-gqt})\,dt=1-\frac{1-e^{-gqT}}{gqT}$', 'f_inner', fs=20)
formula(r'$\frac{\partial E}{\partial x_2}=\int_0^1 P\,V\,\varphi\,^{\prime}(gqT)\,g\,q\,T^{\prime}(x_2)\,f(q)\,dq$', 'f_leib', fs=20)
formula(r'$\mathcal{L}=E(x_1,x_2)+\lambda\,(x_1+x_2-B)$', 'f_lag', fs=20)
formula(r'$\frac{\partial E}{\partial x_1}=\frac{\partial E}{\partial x_2}=-\lambda,\quad \lambda(B^*)=1$', 'f_lag2', fs=20)
