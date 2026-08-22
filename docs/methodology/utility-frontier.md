# Fair-Lending Utility and the Privacy–Utility Frontier

## Minimum detectable disparity

The initial power module calculates the minimum detectable difference between two denial rates using a two-sided normal approximation for two proportions. It reports the result in percentage points at a declared alpha and power.

This is an unadjusted diagnostic. It is useful for showing how suppression changes the number of observations available to detect disparities, but it does not replace the planned adjusted fair-lending model controlling for income, loan-to-value, debt-to-income, loan purpose, and tract characteristics.

## Frontier

Each protection configuration produces one aggregate point containing:

- retained records and retained share;
- sample-uniqueness rate;
- prosecutor expected-match risk; and
- minimum detectable denial-rate disparity.

The `cfpb_current` configuration is explicitly marked as the current baseline. This prevents a visualization from implying that a transformed alternative is the status quo.

## Interpretation

Lower uniqueness and prosecutor risk indicate stronger privacy protection. A lower minimum detectable disparity indicates greater analytical sensitivity. A preferred configuration therefore moves toward lower risk without materially increasing the minimum detectable disparity or suppressing an unacceptable share of records.

