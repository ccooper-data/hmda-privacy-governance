# Fair-Lending Utility and the Privacy–Utility Frontier

## Minimum detectable disparity

The power module calculates the minimum detectable difference between Black non-Hispanic and White
non-Hispanic denial rates among decision actions 1, 2, 3, and 7. It uses a two-sided normal
approximation for two proportions at alpha 0.05 and power 0.80, and reports percentage points.

This is an unadjusted diagnostic. It is useful for showing how suppression changes the number of observations available to detect disparities, but it does not replace the planned adjusted fair-lending model controlling for income, loan-to-value, debt-to-income, loan purpose, and tract characteristics.

## Frontier

Each protection configuration produces one aggregate point containing:

- retained records, retained share, and suppression cost;
- pre-suppression sample uniqueness and post-suppression residual uniqueness;
- prosecutor expected-match risk; and
- minimum detectable denial-rate disparity.

`cfpb_current_unsuppressed` is the actual public status quo. `cfpb_current` is a separate
hypothetical release using the same fields with k≥5 suppression. Keeping both rows prevents a
transformed alternative from being mislabeled as today's public file.

## Interpretation

Lower uniqueness and prosecutor risk indicate stronger privacy protection. A lower minimum detectable disparity indicates greater analytical sensitivity. A preferred configuration therefore moves toward lower risk without materially increasing the minimum detectable disparity or suppressing an unacceptable share of records.
