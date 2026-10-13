"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { calculate } = require("../web/score.js");

const good = {
  cytogenetic_risk: "good", blast_pct: 3, hemoglobin: 9,
  platelets: 80, anc: 1.2
};

test("published complete example and score breakdown", () => {
  const result = calculate(good);
  assert.equal(result.ipss_r_score, 3.5);
  assert.equal(result.risk_category, "Intermediate");
  assert.deepEqual(result.component_scores, {
    cytogenetics: 1, bone_marrow_blasts: 1, hemoglobin: 1,
    platelets: 0.5, anc: 0
  });
});

test("minimum and maximum published scores", () => {
  assert.equal(calculate({
    cytogenetic_risk: "very_good", blast_pct: 0,
    hemoglobin: 12, platelets: 150, anc: 2
  }).ipss_r_score, 0);
  const high = calculate({
    cytogenetic_risk: "very_poor", blast_pct: 12,
    hemoglobin: 7.5, platelets: 45, anc: 0.5
  });
  assert.equal(high.ipss_r_score, 10);
  assert.equal(high.risk_category, "Very High");
});

test("blast thresholds are strict at 2, 5 and 10", () => {
  for (const [value, points] of [[0,0],[2,0],[2.001,1],[4.999,1],[5,2],[10,2],[10.001,3],[100,3]]) {
    assert.equal(calculate({...good, blast_pct:value}).component_scores.bone_marrow_blasts, points);
  }
});

test("hematologic thresholds at Hb 8/10, platelets 50/100 and ANC 0.8", () => {
  for (const [value, points] of [[7.99,1.5],[8,1],[9.99,1],[10,0]]) {
    assert.equal(calculate({...good, hemoglobin:value}).component_scores.hemoglobin, points);
  }
  for (const [value, points] of [[49.99,1],[50,0.5],[99.99,0.5],[100,0]]) {
    assert.equal(calculate({...good, platelets:value}).component_scores.platelets, points);
  }
  assert.equal(calculate({...good,anc:0.7999}).component_scores.anc, 0.5);
  assert.equal(calculate({...good,anc:0.8}).component_scores.anc, 0);
});

test("all five risk boundaries", () => {
  const scenarios = [
    ["very_good",1,12,100,1,"Very Low"],
    ["good",1,9,100,1,"Low"],
    ["intermediate",1,9,100,1,"Low"],
    ["intermediate",3,9,100,1,"Intermediate"],
    ["poor",5,9,100,1,"High"],
    ["very_poor",5,7,49,0.5,"Very High"]
  ];
  for (const [cyto,blasts,hb,plt,anc,expected] of scenarios) {
    assert.equal(calculate({
      cytogenetic_risk:cyto,blast_pct:blasts,hemoglobin:hb,platelets:plt,anc
    }).risk_category, expected);
  }
});

test("reject missing, nonfinite, negative and out-of-range values", () => {
  for (const value of ["",NaN,Infinity,-Infinity,"NaN","Infinity",null,undefined,-1]) {
    assert.throws(() => calculate({...good, blast_pct:value}));
  }
  assert.throws(() => calculate({...good,blast_pct:100.01}));
  assert.throws(() => calculate({...good,hemoglobin:""}));
  assert.throws(() => calculate({...good,platelets:-1}));
  assert.throws(() => calculate({...good,anc:"1e999"}));
  assert.throws(() => calculate({...good,cytogenetic_risk:"__proto__"}));
});

test("static page has valid inline JS and relative asset references", () => {
  const folder = path.join(__dirname, "..");
  const html = fs.readFileSync(path.join(folder,"web","index.html"), "utf8");
  const root = fs.readFileSync(path.join(folder,"index.html"), "utf8");
  assert.match(html, /src="\.\/score\.js"/);
  assert.match(root, /url=\.\/web\//);
  assert.match(html, /window\.IPSSR\.calculate/);
  assert.doesNotMatch(html, /fetch\('/);
  const match = html.match(/<script>([\s\S]*?)<\/script>/);
  assert.ok(match);
  assert.doesNotThrow(() => new vm.Script(match[1]));
});
