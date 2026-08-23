select *
from {{ ref('risk_metrics_by_race') }}
where record_count < 20

