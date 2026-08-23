select *
from {{ ref('risk_metrics_by_race') }}
where record_count < {{ var('minimum_cell_size') }}
