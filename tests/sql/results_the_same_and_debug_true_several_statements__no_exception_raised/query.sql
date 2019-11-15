SET some_var = some_var;

ADD SOMETHING;

INSERT OVERWRITE TABLE some_schema.some_table PARTITION (field4=2) SELECT a.field1 FROM other_schema.other_table a

;
