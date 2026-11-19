# B08 review: what's wrong and what changed

## Must do before submitting (tonight)

1. **Run the whole notebook in BigQuery.** Use Colab or Jupyter with `%load_ext bigquery_magics`, then Runtime → Restart and run all. Do this even if nothing else changes:
   - Every code cell has a blank execution count (`[ ]`), so the notebook looks like it was never run.
   - The counts show as `1196.0` and `0.0`. BigQuery returns whole numbers, so those outputs came from the local DuckDB replay, not BigQuery.
   - The original 3.1 text said "Refresh the outputs in BigQuery before submitting", and the last cell said the SQL "was replayed locally". Both are now removed, but they were accurate.
   - The rubric requires "runs Restart & Run All without errors" with visible outputs.
2. **Ten cells are empty until you run them.** They are new or changed: 4.5 (cell 24), the weekday query in 5.2, the confidence interval in 6.1, the staff share in 7.2, 8.3 and 8.4. The DDL cells (`CREATE …`) print nothing, which is normal.
3. **Re-read every number in the text after the run.** `APPROX_QUANTILES` can move a rounded median by about 0.01. Everything else should match exactly (see "Verification" below).
4. **Remove the temporary auth cell**, and check that the file name is exactly `B08-Patterns-in-Boston-311-Service-Delays.ipynb`.
5. **Check the AI disclosure (Section 11)** and edit it so it matches what your team actually did.

## Verification I did

I downloaded the same City CSVs (snapshot of Sep 18, 2026) and the NOAA file, and rebuilt `v_311_clean` in DuckDB. It reproduces 307,791 / 306,756 raw rows, 614,546 cleaned cases, on-time rates of 75.66% and 72.03%, and median days of 0.78 and 0.53. I also checked the numbers in the text against the outputs. They all match except one typo: in 7.2, staff West Roxbury was given as 2.88 but the output is **2.89**. I fixed it.

No silent logic error found in `is_on_time`: zero targeted cases end up with a NULL flag, so the numerator and denominator are consistent.

## Substantive finding: the weather result was confounded by weekday

- Weekends average **555** requests a day, against **955** on weekdays (−42%).
- 16 of the 17 hot days were weekdays, and 10 of the 19 cold days were weekend days.
- Matched on month **and** weekday/weekend:

| Day type | Before (month only) | After (month and weekday) |
|---|---|---|
| Hot | +17.4% | **+2.6%** |
| Cold | −5.5% | **+10.1%** |
| Heavy rain | −9.0% | −9.6% |
| Snow | −16.1% | −16.0% |

- Correlation of max temperature with daily requests: r = 0.41 raw, **0.21** within the same month and weekday group.

The team's own caveat in 8.1 ("we match on month but not on weekday") was right. This is now 8.3 and 8.4, and the weather takeaway, the executive summary and conclusion #4 are updated.

## Rubric gaps fixed

| Rubric item | Gap | Change |
|---|---|---|
| SQL mastery: "MIN, MAX, AVG, STDDEV" | No STDDEV | Added MIN and STDDEV to 4.5 |
| SQL mastery: "correlation-style query" | None | 8.4 uses `CORR` and a named `WINDOW` |
| SQL mastery: "each query should include a clear comment" | About 25 queries had no comment | Added a one-line `--` comment to every query |
| Quality of answers: "uncertainty" | No intervals | 95% CI for the on-time rate (6.1) |
| Problem definition: "success criteria" | Missing | Added a success-criteria paragraph, and replaced the Section 1 takeaway with a business takeaway |
| Conclusions: "risks/limits, next steps" | Only actions and a Phase 3 line | Added Risks and limitations, Next steps and a takeaway |
| Exec summary: 4–6 sentences | 5 sentences | Now 6, including the weather and calendar finding |
| Claim not backed by an output ("staff open over 60% of parking cases") | No query | Added a query (61.5% / 66.0%) |
| Notebook organization | "## 0. How we used AI" placed at the end, plus a stray revision note | Renumbered as 10. References and 11. Generative AI disclosure, with the revision note merged into the disclosure |
| AI disclosure: "truthful" | Said "the team wrote and executed the queries" while the note said Codex added SQL checks | Rewrote it to say who did what (please edit to match reality) |

## Compared with the F1 (B05) notebook

The F1 notebook was strong because it ended with explicit **Risks and limitations** and **Next steps**, labeled every recommendation with impact and effort, checked how sensitive results were (baselines, leave-one-out), and gave a specific, truthful AI disclosure. The B08 notebook already had the impact and feasibility labels. The new risks and next-steps section, the weekday sensitivity check (8.3) and the rewritten disclosure close the remaining gaps.

## Not changed (optional, if you have time)

- `UNION ALL BY NAME` in cell 8 needs BigQuery's newer set-operation syntax. If it errors, use plain `UNION ALL`, which works because both raw tables share the same column order.
- Charts are embedded images, which is fine because charts aren't graded. Don't add Python that does SQL's job: the rubric gives a negative grade for that.
