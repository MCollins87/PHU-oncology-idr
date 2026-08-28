## Geography

- Portsmouth: PO1 - PO6
- South East Hampshire: PO7 - PO11
- Gosport and Fareham: PO12 - PO17, SO31
- West Sussex: PO18 - PO22, GU28 - GU29
- Isle of Wight: PO30 - PO41
- North East Hampshire: GU30 - GU34
- Sussex: BN*
- Surrey: RH*, GU* excluding GU28-GU34
- Southampton: SO* excluding SO31
- Other / Outside Area: Everything else

## Practice Groups
- Breast
- Lung
- Head and Neck
- Upper GI
- Lower GI
- Urology
- Gynae
- Brain/CNS
- Lymphoma
- Skin
- Melanoma
- Other

## Treatment Intent

- 01 Adjuvant
- 02 Neoadjuvant
- 03 Radical
- 04 Disease Mod. Pall.
- 05 Symptom Ctrl. Pall.
- 97 Other (non cancer)
- 98 Other
- 99 Not Known

## Treatment Sites

Appendix 3 of "UK Guidance Notes Fr ARIA & v6 RTDS" (AI17.0-GDN-01-C)


## Administrative Category

RTDS extracts contain both legacy and modern coding
formats. Equivalent values are mapped to a common
category group.

| NHS | Private |
| --- | --- |
| 01 | 02 |
| 1 | 2 |
| NH | PP|

## Gender


- 1 Male
- 2 Female
- 9 Not Specified
- X Not Known

## Specialist Treatments

Codes

- S01 - Simple
- S02 - Conformal
- S03 - IMRT
- S04 - RapidArc / VMAT
- S05 - IORT
- S06 - TBI or TBE
- S07 - SABR
- S08 - SRS / SRT
- S09 - Proactive Adaptive RT
- S10 - Real-Time Adaptive RT
- S11 - Contact Radiotherapy
- S98 - Other Treatment

## Treatment Modalities

- 1 - External Beam Radiotherapy
- 2 - Brachytherapy
- 3 - Proton Therapy

## Special Diagnosis Mappings

- C61 = Prostate = Urology
- C67 = Bladder = Urology
- L91.0 = Keloid = Other = Bnign Conditions

### Keloid Scar

ICD10:
L91.0

Tumour Site:
Keloid

Disease Group:
Benign Conditions

Practice Group:
Other

Rationale:

Keloid scar radiotherapy is delivered within the service and is
included within operational and activity reporting.

Whilst L91.0 is not a malignant diagnosis, management and service
planning discussions frequently include keloid activity and therefore
these episodes are retained and classified.

## Treatment Start Definition

First treatment date

`MIN(time_and_date_of_exposure)`

Grouped by `radiotherapy_episode_identifier`