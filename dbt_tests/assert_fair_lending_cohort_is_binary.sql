select *
from {{ ref('fair_lending_modeling_cohort') }}
where is_black not in (0, 1)
   or is_denied not in (0, 1)
