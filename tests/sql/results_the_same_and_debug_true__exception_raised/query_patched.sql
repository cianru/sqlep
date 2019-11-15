INSERT OVERWRITE TABLE tezt.some_schema_some_table PARTITION (field4=2)
SELECT
  a.field1
  , b.field2
FROM
  tezt.other_schema_other_table a
LEFT JOIN
    tezt.other_schema_another_table b
ON
    a.c = b.c