/*
Object:     mart.vw_patient_geography
Purpose:    Assign patients to local geography groups based on postcode.

Author:     Mark Collins
Created:    2026-08-26

Business Rule:
Portsmouth: PO1 - PO6
South East Hampshire: PO7 - PO11
Gosport and Fareham: PO12 - PO17, SO31
West Sussex: PO18 - PO22, GU28 - GU29
Isle of Wight: PO30 - PO41
North East Hampshire: GU30 - GU34
Sussex: BN*
Surrey: RH*, GU* excluding GU28-GU34
Southampton: SO* excluding SO31
Other / Outside Area: Everything else
*/

CREATE OR REPLACE VIEW mart.vw_patient_geography AS
SELECT

    p.patient_sk,
    p.nhs_number,
    p.postcode,

    COALESCE(

        (
            SELECT g.geography_area
            FROM reference.dim_geography g
            WHERE REPLACE(UPPER(p.postcode),' ','')
                    LIKE g.postcode_prefix || '%'
            ORDER BY LENGTH(g.postcode_prefix) DESC
            LIMIT 1
        ),

        CASE
            WHEN REPLACE(UPPER(p.postcode),' ','')
                    LIKE 'BN%'
            THEN 'Sussex'
            WHEN REPLACE(UPPER(p.postcode),' ','')
                    LIKE 'SO%'
            THEN 'Southampton'
            WHEN REPLACE(UPPER(p.postcode),' ','')
                    LIKE 'GU%'
            THEN 'Surrey'
            WHEN REPLACE(UPPER(p.postcode),' ','')
                    LIKE 'RH%'
            THEN 'Surrey'
            ELSE 'Other / Outside Area'
        END

    ) AS geography_area

FROM rtds.dim_patient p;