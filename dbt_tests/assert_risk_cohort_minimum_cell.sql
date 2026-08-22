select *
from {{ ref('risk_cohort_counts') }}
where record_count < 20

