select *
from {{ ref('qi_sensitivity_by_race') }}
where record_count < 20

