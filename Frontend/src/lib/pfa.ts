// Mirrors pensions.models.PFAChoice on the backend - candidate list for
// display only, none of these are integrated (see the backend's PFAProvider
// docstring).
export const PFA_LABELS: Record<string, string> = {
  stanbic_ibtc: "Stanbic IBTC Pension Managers",
  arm: "ARM Pension Managers",
  leadway_pensure: "Leadway Pensure PFA",
  fcmb: "FCMB Pensions",
  pal: "Pensions Alliance Limited (PAL)",
  trustfund: "Trustfund Pensions",
  crusader_sterling: "Crusader Sterling Pensions",
  premium: "Premium Pension",
  sigma: "Sigma Pensions",
  fidelity: "Fidelity Pension Managers",
  parthian: "Parthian Pensions",
  citizens: "Citizens Pensions",
};

export function pfaLabel(code: string): string {
  return PFA_LABELS[code] ?? code;
}
