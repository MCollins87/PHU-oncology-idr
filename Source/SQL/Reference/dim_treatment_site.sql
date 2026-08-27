/*
Object:     reference.dim_treatment_site

Purpose:    Lookup table for RTDS ANATOMICAL_TREATMENT_SITE_RADIOTHERAPY.

Author:     Mark Collins
Created:    2026-08-27

Source:
UK Guidance Notes for ARIA & v6 RTDS

Only treatment sites currently identified in the
Portsmouth RTDS dataset have been included.

Additional codes can be added as required.
*/

CREATE TABLE IF NOT EXISTS reference.dim_treatment_site
(
    treatment_site_code VARCHAR(10) PRIMARY KEY,
    treatment_site_name VARCHAR(200) NOT NULL
);

INSERT INTO reference.dim_treatment_site
(
    treatment_site_code,
    treatment_site_name
)
VALUES

-- Spinal Cord

('Z061','Cervical spinal cord'),
('Z062','Thoracic spinal cord'),
('Z063','Lumbar spinal cord'),
('Z064','Meninges of spinal cord'),
('Z065','Cerebrospinal fluid'),
('Z068','Specified spinal cord NEC'),
('Z069','Spinal cord NEC'),

-- Endocrine

('Z131','Thyroid gland'),
('Z135','Parathyroid gland'),
('Z141','Pituitary gland'),
('Z142','Pineal gland'),
('Z143','Thymus gland'),
('Z144','Adrenal gland'),

-- Breast

('Z151','Upper inner quadrant of breast'),
('Z152','Upper outer quadrant of breast'),
('Z153','Lower inner quadrant of breast'),
('Z154','Lower outer quadrant of breast'),
('Z155','Axillary tail of breast'),
('Z156','Nipple'),
('Z157','Areola'),
('Z158','Specified breast NEC'),
('Z159','Breast NEC'),

-- Respiratory

('Z241','Pharynx'),
('Z242','Larynx'),
('Z243','Trachea'),
('Z244','Carina'),
('Z245','Bronchus'),
('Z246','Lung'),
('Z247','Mediastinum'),

-- Oral

('Z255','Tongue'),
('Z256','Palate'),
('Z257','Tonsil'),
('Z258','Specified mouth NEC'),

-- Salivary

('Z261','Parotid gland'),

-- Upper GI

('Z271','Oesophagus'),

-- Lower GI

('Z291','Rectum'),
('Z292','Anus'),
('Z293','Perianal tissue'),
('Z294','Colorectal'),

-- Hepatobiliary

('Z301','Liver NEC'),
('Z302','Gall bladder'),

-- Other Abdominal Organs

('Z311','Pancreas'),
('Z313','Spleen'),

-- Brain and CNS

('Z011','Tissue of frontal lobe of brain'),
('Z012','Tissue of temporal lobe of brain'),
('Z013','Tissue of parietal lobe of brain'),
('Z014','Tissue of occipital lobe of brain'),
('Z015','Tissue of cerebellum'),
('Z016','Tissue of brain stem'),
('Z017','Cingulate gyrus'),
('Z018','Specified tissue of brain NEC'),
('Z019','Tissue of brain NEC'),

('Z032','Optic nerve (II)'),
('Z035','Trigeminal nerve (V)'),
('Z042','Acoustic nerve (VIII)'),

('Z059','Meninges of brain NEC'),

('Z071','Spinal nerve root of cervical spine'),
('Z072','Spinal nerve root of thoracic spine'),
('Z073','Spinal nerve root of lumbar spine'),
('Z079','Spinal nerve root NEC'),

('Z109','Lumbar plexus NEC'),
('Z119','Sacral plexus NEC'),

-- Endocrine

('Z139','Endocrine gland of neck NEC'),
('Z149','Endocrine gland NEC'),

-- Eye and Ear

('Z161','Orbit'),
('Z162','Eyebrow'),
('Z163','Canthus'),
('Z164','Eyelid'),
('Z169','External structure of eye NEC'),
('Z199','Eye NEC'),

('Z201','External ear'),
('Z209','Outer ear NEC'),
('Z219','Ear NEC'),

-- Nose and Sinuses

('Z221','External nose'),
('Z226','Nasopharynx'),
('Z229','Nose NEC'),

('Z231','Maxillary antrum'),
('Z232','Frontal sinus'),
('Z233','Ethmoid sinus'),
('Z234','Sphenoid sinus'),
('Z239','Nasal sinus NEC'),

-- Respiratory

('Z248','Specified other respiratory tract NEC'),
('Z249','Other respiratory tract NEC'),

-- Oral

('Z251','Lip'),
('Z254','Gingiva'),
('Z259','Mouth NEC'),

-- Salivary

('Z262','Submandibular gland'),
('Z263','Sublingual gland'),
('Z264','Salivary gland'),
('Z269','Salivary apparatus NEC'),

-- Gastrointestinal

('Z272','Stomach'),
('Z277','Small intestine'),
('Z279','Upper digestive tract NEC'),

('Z283','Ascending colon'),
('Z284','Transverse colon'),
('Z285','Descending colon'),
('Z286','Sigmoid colon'),
('Z287','Colon NEC'),
('Z289','Large intestine NEC'),

('Z298','Specified part of bowel NEC'),
('Z299','Bowel NEC'),

('Z309','Biliary tract NEC'),

('Z312','Pancreatic duct'),

('Z318','Specified abdominal organ NEC'),
('Z319','Abdominal organ NEC'),

-- Cardiovascular

('Z339','Heart NEC'),

('Z391','Superior vena cava'),

-- Urology

('Z411','Kidney'),
('Z413','Ureter NEC'),
('Z414','Renal pelvis NEC'),
('Z419','Upper urinary tract NEC'),

('Z421','Bladder NEC'),
('Z422','Prostate'),

('Z425','Urethra NEC'),
('Z427','Penis'),
('Z429','Lower urinary tract NEC'),

-- Male Genital Tract

('Z431','Scrotum'),
('Z432','Testis'),
('Z435','Seminal vesicle'),
('Z436','Male perineum'),
('Z438','Specified male genital organ NEC'),
('Z439','Male genital organ NEC'),

-- Female Genital Tract

('Z441','Clitoris'),
('Z442','Bartholin gland'),
('Z443','Vulva'),
('Z444','Female perineum'),
('Z449','Vagina NEC'),

('Z451','Cervix uteri'),
('Z458','Specified uterus NEC'),
('Z459','Uterus NEC'),

('Z463','Ovary'),
('Z469','Female genital tract NEC'),

-- Skin

('Z471','Skin of forehead'),
('Z472','Skin of temple'),
('Z473','Skin of cheek'),
('Z474','Skin of nasolabial area'),
('Z475','Skin of chin'),
('Z478','Specified skin of face NEC'),
('Z479','Skin of face NEC'),

('Z481','Skin of scalp'),
('Z482','Skin of neck'),
('Z488','Skin of specified part of head NEC'),
('Z489','Skin of head NEC'),

('Z491','Skin of breast'),
('Z492','Skin of axilla'),
('Z493','Skin of anterior trunk'),
('Z494','Skin of back'),
('Z495','Skin of buttock'),
('Z496','Skin of shoulder'),
('Z497','Skin of groin'),
('Z498','Specified skin of trunk NEC'),
('Z499','Skin of trunk NEC'),

('Z501','Skin of arm'),
('Z502','Skin of hand'),
('Z503','Skin of finger'),
('Z504','Skin of leg NEC'),
('Z505','Skin of foot NEC'),
('Z506','Skin of toe'),
('Z507','Skin of ankle'),
('Z508','Specified skin of site NEC'),
('Z509','Skin NEC'),

('Z519','Nail NEC'),

-- Pleura and Body Wall

('Z521','Pleura'),

('Z528','Specified chest wall NEC'),
('Z529','Chest wall NEC'),

('Z532','Umbilicus'),
('Z533','Peritoneum'),
('Z534','Peritoneal cavity'),
('Z539','Abdominal wall NEC'),

-- Lymph Nodes

('Z611','Cervical lymph node'),
('Z612','Scalene lymph node'),
('Z613','Axillary lymph node'),
('Z614','Mediastinal lymph node'),
('Z615','Para-aortic lymph node'),
('Z616','Inguinal lymph node'),
('Z617','Retroperitoneal lymph node'),
('Z618','Specified lymph node NEC'),
('Z619','Lymph node NEC'),

-- Soft Tissue

('Z623','Lymphatic tissue'),
('Z624','Connective tissue'),
('Z628','Specified soft tissue NEC'),
('Z629','Soft tissue NEC'),

-- Craniofacial Bones

('Z638','Specified bone of cranium NEC'),
('Z644','Maxilla'),
('Z651','Mandible'),

-- Vertebrae

('Z663','Cervical vertebra'),
('Z664', 'Thoracic vertebra'),
('Z665', 'Lumbar vertebra'),
('Z668','Specified vertebra NEC'),

-- Shoulder Girdle

('Z681','Clavicle'),
('Z685','Scapula NEC'),
('Z688','Specified bone of shoulder girdle NEC'),

-- Humerus

('Z691','Head of humerus'),
('Z698','Specified humerus NEC'),

-- Arm

('Z709','Radius NEC'),
('Z719','Ulna NEC'),
('Z729','Bone of arm or wrist NEC'),

-- Thorax

('Z742','Sternum NEC'),
('Z748', 'Specified rib cage NEC'),

-- Pelvis

('Z751','Body of sacrum'),
('Z756','Acetabulum'),
('Z758','Specified bone of pelvis NEC'),

-- Femur

('Z761','Head of femur'),
('Z762','Neck of femur'),
('Z768','Specified femur NEC'),

-- Lower Limb

('Z779','Tibia NEC'),

-- Joints

('Z841','Sacroiliac joint'),

-- Musculoskeletal

('Z871','Bone NEC'),
('Z879','Musculoskeletal system NEC'),

-- Regional Sites

('Z902','Hip NEC'),

-- General Body Regions

('Z921','Head NEC'),
('Z922','Face NEC'),
('Z923','Neck NEC'),
('Z924','Chest NEC'),
('Z925','Back NEC'),
('Z926','Abdomen NEC'),
('Z927','Trunk NEC'),
('Z928','Specified region of body NEC'),
('Z929','Region of body NEC'),

-- Intervertebral Discs

('Z991','Intervertebral disc of cervical spine'),
('Z992','Intervertebral disc of thoracic spine'),
('Z993','Intervertebral disc of lumbar spine'),
('Z998','Specified intervertebral disc NEC'),
('Z999','Intervertebral disc NEC')

ON CONFLICT (treatment_site_code)
DO NOTHING;