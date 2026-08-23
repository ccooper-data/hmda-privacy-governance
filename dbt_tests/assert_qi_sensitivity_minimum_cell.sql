select *
from {{ ref('qi_sensitivity_by_race') }}
where record_count < {{ var('minimum_cell_size') }}
