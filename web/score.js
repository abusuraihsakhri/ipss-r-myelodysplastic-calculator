"use strict";

/**
 * Deterministic IPSS-R scoring for untreated adult MDS.
 * Source: Greenberg et al., Blood 2012;120:2454-2465.
 * doi:10.1182/blood-2012-03-420489
 */
(function (root, factory) {
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.IPSSR = api;
})(typeof window !== "undefined" ? window : null, function () {
  const cytogenetics = Object.freeze({
    very_good: 0, good: 1, intermediate: 2, poor: 3, very_poor: 4
  });
  const ranges = Object.freeze([
    { limit: 1.5, label: "Very Low" },
    { limit: 3, label: "Low" },
    { limit: 4.5, label: "Intermediate" },
    { limit: 6, label: "High" },
    { limit: 10, label: "Very High" }
  ]);

  function number(value, label, maximum) {
    if (value === "" || value === null || value === undefined) {
      throw new Error(label + " is required.");
    }
    const result = Number(value);
    if (!Number.isFinite(result)) throw new Error(label + " must be a finite number.");
    if (result < 0) throw new Error(label + " cannot be negative.");
    if (maximum !== undefined && result > maximum) {
      throw new Error(label + " cannot exceed " + maximum + ".");
    }
    return result;
  }

  function calculate(input) {
    if (!input || !Object.prototype.hasOwnProperty.call(cytogenetics, input.cytogenetic_risk)) {
      throw new Error("Select a cytogenetic risk category.");
    }
    const blasts = number(input.blast_pct, "Bone marrow blasts", 100);
    const hb = number(input.hemoglobin, "Hemoglobin");
    const platelets = number(input.platelets, "Platelets");
    const anc = number(input.anc, "ANC");
    const components = {
      cytogenetics: cytogenetics[input.cytogenetic_risk],
      bone_marrow_blasts: blasts <= 2 ? 0 : blasts < 5 ? 1 : blasts <= 10 ? 2 : 3,
      hemoglobin: hb >= 10 ? 0 : hb >= 8 ? 1 : 1.5,
      platelets: platelets >= 100 ? 0 : platelets >= 50 ? 0.5 : 1,
      anc: anc >= 0.8 ? 0 : 0.5
    };
    const score = Object.values(components).reduce((sum, value) => sum + value, 0);
    const risk = ranges.find((range) => score <= range.limit);
    return Object.freeze({
      ipss_r_score: score,
      risk_category: risk.label,
      component_scores: Object.freeze(components),
      clinical_recommendation: "Prognostic classification only; treatment requires individualized specialist assessment."
    });
  }

  return Object.freeze({ calculate });
});
