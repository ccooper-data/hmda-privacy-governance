select *
from {{ ref('risk_by_release_density') }}
where record_count < 20

