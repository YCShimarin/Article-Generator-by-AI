> **AI Generated Metadata**
> - Model: stepfun/step-3.5-flash:free
> - Mode: 🔬 Science / Academic (with LaTeX)
> - Time: 105s
> - Words: 952

# The Mathematics of a Prism: How White Light Decomposes into a Rainbow

## Fundamentals of Light and Prisms

White light, such as sunlight, is a superposition of electromagnetic waves across the visible spectrum (approximately 380 nm to 750 nm). When this composite beam encounters a prism, its constituent wavelengths separate spatially—a phenomenon known as dispersion. This occurs because the refractive index, $n$, of the prism material (e.g., crown glass) is not constant but varies with wavelength, $\lambda$. This wavelength dependence is described by empirical relations such as the Sellmeier equation:

$$
n^2(\lambda) = 1 + \sum_{j} \frac{B_j \lambda^2}{\lambda^2 - C_j}
$$

where $B_j$ and $C_j$ are material-specific coefficients, and $\lambda$ is in micrometers. The fundamental mechanism governing the bending of light at the air-glass interface is Snell’s Law:

$$
n_{\text{air}} \sin\theta_i = n(\lambda) \sin\theta_t(\lambda)
$$

Here, $\theta_i$ is the angle of incidence, $\theta_t(\lambda)$ is the transmitted angle specific to wavelength $\lambda$, and $n_{\text{air}} \approx 1.0003$. Because $n(\lambda)$ decreases with increasing $\lambda$ in the visible range (normal dispersion), blue light ($\lambda \approx 450$ nm) refracts more strongly than red light ($\lambda \approx 650$ nm). Consequently, a monochromatic beam entering the prism at a fixed $\theta_i$ exits at an angle $\theta_t(\lambda)$ that varies with $\lambda$. The prism thus acts as a spectral “un-mixer,” translating small differences in refractive index into a measurable angular separation, $\Delta\theta$, between extreme wavelengths. This angular dispersion is the principle behind spectroscopic instruments.

## Refraction and Snell's Law

When a light ray traverses the boundary between two transparent media, its direction changes due to a variation in propagation speed. This phenomenon, termed refraction, is quantitatively governed by Snell's Law (or the law of refraction). At the planar interface separating two media with refractive indices \( n_1 \) and \( n_2 \) (dimensionless), the incident ray (angle \( \theta_1 \)) and the refracted ray (angle \( \theta_2 \)) lie in the same plane as the interface normal. Their relationship is defined by:

$$
n_1 \sin\theta_1 = n_2 \sin\theta_2
$$

Here, \( \theta_1 \) and \( \theta_2 \) are measured from the normal, typically in degrees. The refractive index \( n = c/v \) represents the ratio of the speed of light in vacuum \( c \) to its phase velocity \( v \) in the medium. For air, \( n \approx 1.0003 \), while for common glass, \( n \approx 1.5 \). Consequently, when light enters a denser medium (higher \( n \)), it bends toward the normal (\( \theta_2 < \theta_1 \)).

In a triangular glass prism, this law applies at both entrance and exit faces. The precise angular deviation depends on the prism's apex angle and the angle of incidence. Critically, the refractive index is wavelength-dependent—a property known as dispersion. For violet light, \( n \) is slightly larger than for red light. Therefore, according to Snell’s Law, violet rays are refracted more strongly than red rays at each interface. This differential refraction is the fundamental mechanism by which a prism spatially separates the constituent wavelengths of white light, forming a continuous spectrum.

## Dispersion and the Cauchy Equation

Dispersion is the phenomenon whereby the refractive index $n$ of a material varies with the wavelength $\lambda$ of incident light. This wavelength dependence is the fundamental physical cause of a prism's ability to separate white light into its constituent colors, as each wavelength is refracted by a different angle according to Snell's law.

The empirical relationship most commonly used to describe this variation in the visible spectrum is the Cauchy equation, an early and historically significant approximation. It is expressed as:

$$
n(\lambda) = A + \frac{B}{\lambda^2} + \frac{C}{\lambda^4} + \cdots
$$

Here, $n$ is a dimensionless refractive index. The wavelength $\lambda$ is typically expressed in micrometers ($\mu m$). The coefficients $A$, $B$, and $C$ are material-specific constants determined experimentally; $A$ represents the refractive index as $\lambda$ approaches infinity. For example, for typical crown glass, $A \approx 1.5046$, $B \approx 0.00420 \ \mu m^2$, and $C \approx 0.00000 \ \mu m^4$ (often negligible in the visible range). Using the sodium D-line wavelength $\lambda = 0.589 \ \mu m$, this equation yields a value consistent with measured $n_D$.

While useful for simple calculations, the Cauchy equation is an empirical fit with limited accuracy, particularly in the ultraviolet and infrared regions. More precise modern descriptions, such as the Sellmeier equation, are based on resonant frequency models of the material's electronic structure. Nevertheless, the Cauchy equation remains a standard pedagogical tool for illustrating the systematic variation of $n$ with $\lambda$ that underpins dispersion.

## Calculating Angular Spread

The angular spread Δδ of a dispersed spectrum is determined by the difference in the angle of minimum deviation, δ_min, for two extreme wavelengths (e.g., red and blue). For a prism with apex angle α and refractive index n(λ), δ_min is given by:

$$
\delta_{\text{min}}(\lambda) = 2 \arcsin\left( n(\lambda) \sin\frac{\alpha}{2} \right) - \alpha
$$

Here, α and δ_min are measured in radians or degrees, while n(λ) is dimensionless. The wavelength dependence of n(λ)—a property known as **material dispersion**—is the fundamental cause of angular separation. The angular spread Δδ between wavelengths λ₁ and λ₂ is therefore:

$$
\Delta\delta = \delta_{\text{min}}(\lambda_1) - \delta_{\text{min}}(\lambda_2)
$$

For a typical glass prism (e.g., crown glass) with α = 60°, n(λ) decreases with increasing wavelength (normal dispersion). Consequently, δ_min(λ_red) < δ_min(λ_blue), yielding a positive Δδ. The magnitude of Δδ increases with both the dispersion strength (dn/dλ) of the material and the prism's apex angle α, provided α is less than the angle for total internal reflection at the exit face. This quantitative relationship allows for the prediction and optimization of spectral separation in spectroscopic instruments.



---
<details>
<summary>🔍 SEO_OPTIMIZATION_METADATA (Click to Expand)</summary>

**Focus Keywords:** prism dispersion, white light decomposition, rainbow formation, refractive index math, spectrum separation
**Meta Description:** Explore the math behind prism dispersion: how a prism's varying refractive index splits white light into a spectral rainbow.
**Suggested Slug:** mathematics-prism-dispersion

</details>