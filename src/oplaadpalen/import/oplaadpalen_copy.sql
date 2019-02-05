BEGIN;
ALTER SEQUENCE oplaadpalen_new_id_seq OWNED BY oplaadpalen.id;
DROP TABLE IF EXISTS oplaadpalen_new;
CREATE TABLE oplaadpalen_new ( LIKE oplaadpalen INCLUDING DEFAULTS INCLUDING CONSTRAINTS INCLUDING INDEXES );
INSERT INTO oplaadpalen_new SELECT * FROM oplaadpalen;
ALTER SEQUENCE oplaadpalen_new_id_seq OWNED BY oplaadpalen_new.id;

COMMIT;