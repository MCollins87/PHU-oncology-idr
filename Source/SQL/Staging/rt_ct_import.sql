CREATE TABLE IF NOT EXISTS staging.rt_ct_import (
    activity_instance_id       text PRIMARY KEY,
    patient_id                 text,
    nhs_number                 text,
    activity_name              text,
    appointment_status         text,
    scheduled_end_datetime     timestamp without time zone,
    activity_start_datetime    timestamp without time zone,
    activity_end_datetime      timestamp without time zone,
    activity_created_by        text,
    source_file                text,
    load_timestamp             timestamp with time zone NOT NULL
                               DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rt_ct_import_patient_id
    ON staging.rt_ct_import (patient_id);

CREATE INDEX IF NOT EXISTS idx_rt_ct_import_nhs_number
    ON staging.rt_ct_import (nhs_number);

CREATE INDEX IF NOT EXISTS idx_rt_ct_import_scheduled_end
    ON staging.rt_ct_import (scheduled_end_datetime);

CREATE INDEX IF NOT EXISTS idx_rt_ct_import_status
    ON staging.rt_ct_import (appointment_status);