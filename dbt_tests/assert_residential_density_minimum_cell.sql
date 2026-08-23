select *
from {{ ref('risk_by_residential_density') }}
where record_count < {{ var('minimum_cell_size') }}
