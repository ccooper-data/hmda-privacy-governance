# Protection Engine

## Generalization hierarchy

HMDA census-tract identifiers use an 11-digit geography code. The engine supports tract, county (first five digits), state (first two digits), and national levels. Income and loan amounts can be placed into configurable equal-width bands.

## Suppression

The engine removes entire equivalence classes below a configured k threshold. It never exports a list of suppressed source records.

## l-diversity and t-closeness

Distinct l-diversity counts sensitive-attribute values within each equivalence class. The first t-closeness implementation uses total-variation distance between the class and global sensitive-attribute distributions. Reports summarize the number and share of records failing declared thresholds.

## Differential privacy

Aggregate group counts use the Laplace mechanism with scale `sensitivity / epsilon`, followed by rounding and clamping at zero. The implementation is event-level private only under a one-row-per-person contribution assumption. Before a production release, the pipeline must enforce a person-level contribution bound and account for privacy-budget composition across queries.

