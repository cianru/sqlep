INSERT OVERWRITE TABLE some_schema.some_table PARTITION (field4=2)
SELECT
  a.field1
  , b.field2
FROM
  other_schema.other_table a
LEFT JOIN
    other_schema.another_table b
ON
    a.c = b.c
;
